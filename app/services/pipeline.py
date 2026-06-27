"""
მთავარი Pipeline — ყველა სერვისის ორკესტრაცია.

📌 პრეზენტაციისთვის:
ეს არის "ორკესტრატორი" — მომხმარებლის შეკითხვიდან პასუხამდე მთელ
pipeline-ს მართავს. ნაბიჯები:

1. ინტენტის კლასიფიკაცია → BI კითხვაა თუ არა?
2. სქემის ამოღება → რა ცხრილები გვაქვს?
3. SQL გენერაცია → LLM ქმნის SQL-ს
4. SQL ვალიდაცია → უსაფრთხოა?
5. თვით-კორექცია → თუ შეცდომაა, ხელახლა ცდა (max 3)
6. შესრულება → DB-ზე გაშვება
7. ფორმატირება → ქართულ პასუხად გარდაქმნა

ეს არის "Multi-Agent Pipeline" — თითოეული ნაბიჯი სპეციალიზებული
კომპონენტია, არა ერთი მონოლითური ფუნქცია.
"""

import json
import time
import uuid
from dataclasses import dataclass, field

from app.services.schema_retriever import schema_retriever
from app.services.sql_generator import sql_generator
from app.services.sql_validator import sql_validator
from app.services.query_executor import query_executor
from app.models.schemas import ChatResponse, QueryResult, ChartSuggestion


# === საუბრის მეხსიერება (In-Memory) ===
# Production-ში ეს Redis-ში ან DB-ში შეინახება
_conversations: dict[str, list[dict]] = {}

MAX_SELF_CORRECTION_ATTEMPTS = 3


@dataclass
class PipelineState:
    """Pipeline-ის მდგომარეობა — თითოეულ ნაბიჯზე განახლდება."""
    user_message: str
    conversation_id: str
    intent: str = ""
    schema: str = ""
    generated_sql: str = ""
    sql_explanation: str = ""
    chart_info: dict = field(default_factory=dict)
    query_result: dict | None = None
    formatted_answer: str = ""
    error: str | None = None
    processing_start: float = 0.0


class ConversationalBIPipeline:
    """მთავარი BI Pipeline — შეკითხვიდან პასუხამდე."""

    async def process_message(
        self,
        message: str,
        conversation_id: str | None = None,
    ) -> ChatResponse:
        """
        მომხმარებლის შეტყობინების სრული დამუშავება.
        
        Args:
            message: მომხმარებლის შეკითხვა
            conversation_id: საუბრის ID (follow-up-ისთვის)
            
        Returns:
            ChatResponse: სრული პასუხი
        """
        # === ინიციალიზაცია ===
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        state = PipelineState(
            user_message=message,
            conversation_id=conversation_id,
            processing_start=time.time(),
        )

        try:
            # === ნაბიჯი 1: ინტენტის კლასიფიკაცია ===
            conversation_history = self._get_conversation_history(conversation_id)
            state.intent = await sql_generator.classify_intent(
                message, conversation_history
            )

            # === ნაბიჯი 2: ინტენტის მიხედვით დამუშავება ===
            if state.intent == "greeting":
                return self._greeting_response(state)

            if state.intent == "unclear":
                return self._unclear_response(state)

            # bi_query ან followup — ორივე SQL-ს მოითხოვს
            # === ნაბიჯი 3: სქემის ამოღება ===
            state.schema = await schema_retriever.get_full_schema()

            # === ნაბიჯი 4-5: SQL გენერაცია + ვალიდაცია (self-correction loop) ===
            error_feedback = None
            for attempt in range(MAX_SELF_CORRECTION_ATTEMPTS):
                # SQL-ის გენერაცია
                full_message = message
                if state.intent == "followup" and conversation_history:
                    full_message = f"კონტექსტი:\n{conversation_history}\n\nახალი კითხვა: {message}"

                sql_result = await sql_generator.generate_sql(
                    user_question=full_message,
                    schema=state.schema,
                    conversation_history=conversation_history,
                    error_feedback=error_feedback,
                )

                state.generated_sql = sql_result.get("sql", "")
                state.sql_explanation = sql_result.get("explanation", "")
                state.chart_info = {
                    "chart_type": sql_result.get("chart_type", "table"),
                    "chart_title": sql_result.get("chart_title"),
                    "x_axis": sql_result.get("x_axis"),
                    "y_axis": sql_result.get("y_axis"),
                }

                # SQL ვალიდაცია
                validation = sql_validator.validate(state.generated_sql)

                if validation.is_valid:
                    state.generated_sql = validation.sanitized_sql
                    break
                else:
                    error_feedback = validation.error_message
                    if attempt == MAX_SELF_CORRECTION_ATTEMPTS - 1:
                        state.error = (
                            f"SQL ვალიდაცია ვერ გაიარა {MAX_SELF_CORRECTION_ATTEMPTS} ცდის შემდეგ: "
                            f"{validation.error_message}"
                        )
                        return self._error_response(state)

            # === ნაბიჯი 6: SQL-ის შესრულება ===
            try:
                state.query_result = await query_executor.execute(state.generated_sql)
            except TimeoutError as e:
                state.error = str(e)
                return self._error_response(state)
            except Exception as e:
                # თუ execution error-ია, self-correction ვცადოთ
                error_feedback = str(e)
                sql_result = await sql_generator.generate_sql(
                    user_question=full_message,
                    schema=state.schema,
                    error_feedback=f"SQL შესრულების შეცდომა: {error_feedback}",
                )
                state.generated_sql = sql_result.get("sql", "")
                validation = sql_validator.validate(state.generated_sql)
                if validation.is_valid:
                    state.query_result = await query_executor.execute(
                        validation.sanitized_sql
                    )
                else:
                    state.error = f"მოთხოვნის შესრულება ვერ მოხერხდა: {str(e)}"
                    return self._error_response(state)

            # === ნაბიჯი 7: პასუხის ფორმატირება ===
            result_json = json.dumps(
                state.query_result["rows"][:20],  # მაქსიმუმ 20 მწკრივი LLM-ისთვის
                ensure_ascii=False,
                default=str,
            )

            state.formatted_answer = await sql_generator.format_response(
                user_question=message,
                sql_query=state.generated_sql,
                query_result=result_json,
            )

            # === საუბრის ისტორიაში დამატება ===
            self._save_to_history(conversation_id, message, state.formatted_answer)

            # === პასუხის ფორმირება ===
            return self._success_response(state)

        except Exception as e:
            state.error = f"სისტემური შეცდომა: {str(e)}"
            return self._error_response(state)

    def _get_conversation_history(self, conversation_id: str) -> str:
        """საუბრის ისტორიის ამოღება."""
        history = _conversations.get(conversation_id, [])
        if not history:
            return ""

        # ბოლო 5 შეტყობინება
        recent = history[-10:]  # 5 წყვილი (user + assistant)
        parts = []
        for msg in recent:
            role = "მომხმარებელი" if msg["role"] == "user" else "ასისტენტი"
            parts.append(f"{role}: {msg['content']}")

        return "\n".join(parts)

    def _save_to_history(
        self, conversation_id: str, user_msg: str, assistant_msg: str
    ):
        """შეტყობინების შენახვა ისტორიაში."""
        if conversation_id not in _conversations:
            _conversations[conversation_id] = []

        _conversations[conversation_id].extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ])

        # მაქსიმუმ 20 შეტყობინება
        if len(_conversations[conversation_id]) > 20:
            _conversations[conversation_id] = _conversations[conversation_id][-20:]

    def _success_response(self, state: PipelineState) -> ChatResponse:
        """წარმატებული პასუხის ფორმირება."""
        processing_time = int((time.time() - state.processing_start) * 1000)

        chart = None
        if state.chart_info.get("chart_type") and state.chart_info["chart_type"] != "none":
            chart = ChartSuggestion(
                chart_type=state.chart_info["chart_type"],
                x_axis=state.chart_info.get("x_axis"),
                y_axis=state.chart_info.get("y_axis"),
                title=state.chart_info.get("chart_title"),
            )

        data = None
        if state.query_result:
            data = QueryResult(
                columns=state.query_result["columns"],
                rows=state.query_result["rows"],
                row_count=state.query_result["row_count"],
            )

        return ChatResponse(
            answer=state.formatted_answer,
            sql_query=state.generated_sql,
            data=data,
            chart=chart,
            conversation_id=state.conversation_id,
            processing_time_ms=processing_time,
        )

    def _greeting_response(self, state: PipelineState) -> ChatResponse:
        """მისალმების პასუხი."""
        processing_time = int((time.time() - state.processing_start) * 1000)
        return ChatResponse(
            answer=(
                "გამარჯობა! 👋 მე ვარ სასაუბრო BI ასისტენტი.\n\n"
                "შემიძლია დაგეხმაროთ ბიზნეს-მონაცემების ანალიზში. "
                "მაგალითად, შეგიძლიათ მკითხოთ:\n\n"
                "📊 „რა არის ჩვენი ჯამური შემოსავალი?“\n"
                "📈 „აჩვენე გაყიდვები თვეების მიხედვით“\n"
                "🏆 „ტოპ 10 პროდუქტი გაყიდვებით“\n"
                "🏙️ „შეადარე ქალაქები შემოსავლით“\n\n"
                "რით შემიძლია დაგეხმაროთ?"
            ),
            conversation_id=state.conversation_id,
            processing_time_ms=processing_time,
        )

    def _unclear_response(self, state: PipelineState) -> ChatResponse:
        """გაუგებარი შეტყობინების პასუხი."""
        processing_time = int((time.time() - state.processing_start) * 1000)
        return ChatResponse(
            answer=(
                "ბოდიშით, ვერ გავიგე თქვენი შეკითხვა. 🤔\n\n"
                "გთხოვ, დასვით ბიზნეს-ანალიტიკის კითხვა, მაგალითად:\n"
                "• „რა არის შემოსავალი ამ თვეში?“\n"
                "• „რომელ ქალაქში გვაქვს ყველაზე მეტი მომხმარებელი?“\n"
                "• „ტოპ 5 პროდუქტი მოგების მიხედვით“"
            ),
            conversation_id=state.conversation_id,
            processing_time_ms=processing_time,
        )

    def _error_response(self, state: PipelineState) -> ChatResponse:
        """შეცდომის პასუხი."""
        processing_time = int((time.time() - state.processing_start) * 1000)
        return ChatResponse(
            answer=(
                "სამწუხაროდ, მოთხოვნის დამუშავებისას შეცდომა მოხდა. 😔\n"
                "გთხოვ, სცადეთ კითხვის სხვანაირად ფორმულირება."
            ),
            sql_query=state.generated_sql if state.generated_sql else None,
            conversation_id=state.conversation_id,
            processing_time_ms=processing_time,
            error=state.error,
        )


# Singleton instance
pipeline = ConversationalBIPipeline()
