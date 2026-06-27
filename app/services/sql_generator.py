"""
SQL გენერატორი — ტექსტიდან SQL-ის გენერაცია Google Gemini-ით.

📌 პრეზენტაციისთვის:
ეს არის სისტემის "ტვინი" — იღებს მომხმარებლის ქართულ კითხვას,
DB-ის სქემას, და აგენერირებს PostgreSQL SQL მოთხოვნას.

განახლებულია google-genai SDK-ით Gemini 2.5 Flash-სთვის.
"""

import json
from google import genai
from google.genai import types
from pathlib import Path

from app.config import get_settings

settings = get_settings()

class SQLGenerator:
    """ტექსტიდან SQL-ის გენერატორი Gemini-ით."""

    def __init__(self):
        # ახალი Google GenAI კლიენტის ინიციალიზაცია
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_name = settings.gemini_model
        
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

        config = types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=20,
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        
        text = response.text or "bi_query"
        intent_lower = text.strip().lower()

        # ნორმალიზება
        if "greeting" in intent_lower:
            return "greeting"
        elif "followup" in intent_lower:
            return "followup"
        elif "unclear" in intent_lower:
            return "unclear"
        else:
            return "bi_query"

    async def generate_sql(
        self,
        user_question: str,
        schema: str,
        conversation_history: str = "",
        error_feedback: str | None = None,
    ) -> dict:
        """
        SQL მოთხოვნის გენერაცია მომხმარებლის კითხვის საფუძველზე.
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

        config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.95,
            max_output_tokens=2048,
            response_mime_type="application/json",
            system_instruction=system_prompt,
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=config
        )

        # JSON-ის პარსინგი (Markdown გაწმენდით)
        try:
            raw_text = (response.text or "{}").strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3].strip()

            result = json.loads(raw_text)
        except Exception:
            # fallback — ტექსტიდან SQL-ის ამოღება
            result = {
                "sql": getattr(response, "text", ""),
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
        """
        prompt = self._formatter_prompt_template.format(
            sql_query=sql_query,
            query_result=query_result,
            user_question=user_question,
        )

        config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=1024,
        )

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        text = response.text or "მონაცემები მოძიებულია."
        return text.strip()


# Singleton instance
sql_generator = SQLGenerator()
