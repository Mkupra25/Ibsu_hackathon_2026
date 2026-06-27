"""
SQL გენერატორი — ტექსტიდან SQL-ის გენერაცია Google Gemini-ით.

📌 პრეზენტაციისთვის:
ეს არის სისტემის "ტვინი" — იღებს მომხმარებლის ქართულ კითხვას,
DB-ის სქემას, და აგენერირებს PostgreSQL SQL მოთხოვნას.

ძირითადი ტექნიკები:
- Few-shot prompting: მაგალითები prompt-ში, რომ LLM-მა ისწავლოს ფორმატი
- Structured output: JSON ფორმატით პასუხი (არა თავისუფალი ტექსტი)
- Self-correction: თუ SQL არავალიდურია, შეცდომას უბრუნებს და ახლიდან ცდის
"""

import json
import google.generativeai as genai
from pathlib import Path

from app.config import get_settings

settings = get_settings()

# === Gemini-ის კონფიგურაცია ===
genai.configure(api_key=settings.google_api_key)


class SQLGenerator:
    """ტექსტიდან SQL-ის გენერატორი Gemini-ით."""

    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.1,      # დაბალი — უფრო დეტერმინისტული, ზუსტი
                "top_p": 0.95,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json",  # Structured output!
            },
        )
        self._system_prompt_template = self._load_prompt("system_prompt.txt")
        self._intent_prompt_template = self._load_prompt("intent_prompt.txt")
        self._formatter_prompt_template = self._load_prompt("formatter_prompt.txt")

    def _load_prompt(self, filename: str) -> str:
        """Prompt ფაილის წაკითხვა."""
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / filename
        return prompt_path.read_text(encoding="utf-8")

    async def classify_intent(
        self, message: str, conversation_history: str = ""
    ) -> str:
        """
        მომხმარებლის შეტყობინების ინტენტის კლასიფიკაცია.
        
        აბრუნებს: 'bi_query', 'followup', 'greeting', ან 'unclear'
        """
        prompt = self._intent_prompt_template.format(
            conversation_history=conversation_history or "არ არის",
            message=message,
        )

        # Intent-ისთვის არ გვჭირდება JSON mode
        intent_model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.0,
                "max_output_tokens": 20,
            },
        )

        response = await intent_model.generate_content_async(prompt)
        intent = response.text.strip().lower()

        # ნორმალიზება
        valid_intents = {"bi_query", "followup", "greeting", "unclear"}
        if intent not in valid_intents:
            # თუ intent ვერ ამოიცნო, default-ად bi_query
            return "bi_query"

        return intent

    async def generate_sql(
        self,
        user_question: str,
        schema: str,
        conversation_history: str = "",
        error_feedback: str | None = None,
    ) -> dict:
        """
        SQL მოთხოვნის გენერაცია მომხმარებლის კითხვის საფუძველზე.
        
        Args:
            user_question: მომხმარებლის კითხვა ქართულად
            schema: DB-ის სქემა ტექსტური ფორმატით
            conversation_history: წინა საუბრის ისტორია
            error_feedback: წინა ცდის შეცდომის შეტყობინება (self-correction)
        
        Returns:
            dict: {"sql": "...", "explanation": "...", "chart_type": "...", ...}
        """
        system_prompt = self._system_prompt_template.format(schema=schema)

        # მოთხოვნის ფორმირება
        user_prompt = f"მომხმარებლის კითხვა: {user_question}"

        if conversation_history:
            user_prompt = f"წინა საუბარი:\n{conversation_history}\n\n{user_prompt}"

        if error_feedback:
            user_prompt += (
                f"\n\n⚠️ წინა ცდის SQL შეცდომით დასრულდა: {error_feedback}\n"
                "გთხოვ, გაასწორე SQL და ხელახლა ცადე."
            )

        # Gemini-სთან საუბარი
        chat = self.model.start_chat(history=[])
        response = await chat.send_message_async(
            f"{system_prompt}\n\n{user_prompt}"
        )

        # JSON-ის პარსინგი
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            # fallback — ტექსტიდან SQL-ის ამოღება
            result = {
                "sql": response.text,
                "explanation": "SQL გენერირებულია",
                "chart_type": "table",
                "chart_title": None,
                "x_axis": None,
                "y_axis": None,
            }

        return result

    async def format_response(
        self,
        user_question: str,
        sql_query: str,
        query_result: str,
    ) -> str:
        """
        SQL შედეგის ფორმატირება ბუნებრივ ქართულ ენაზე.
        
        Args:
            user_question: ორიგინალი კითხვა
            sql_query: შესრულებული SQL
            query_result: მოთხოვნის შედეგი (JSON string)
        
        Returns:
            str: ფორმატირებული პასუხი ქართულად
        """
        prompt = self._formatter_prompt_template.format(
            sql_query=sql_query,
            query_result=query_result,
            user_question=user_question,
        )

        formatter_model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
            },
        )

        response = await formatter_model.generate_content_async(prompt)
        return response.text.strip()


# Singleton instance
sql_generator = SQLGenerator()
