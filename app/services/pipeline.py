"""
მთავარი Pipeline — ყველა სერვისის ორკესტრაცია.

📌 არქიტექტურა:
1. ლოკალური NLU (local_nlu.py) — keyword matching, Gemini-ს გარეშე, instant
2. SQL ვალიდაცია — SQL-ის გაწმენდა/შემოწმება
3. Query Executor — PostgreSQL-ზე SQL-ის გაშვება
4. პასუხის ფორმატირება — ბუნებრივ ქართულ ენაზე

Gemini fallback: თუ ლოკალური NLU ვერ ცნობს კითხვას,
ცდილობს Gemini-ს გამოიძახოს. თუ ეს მარცხდება — ატყობინებს შესაბამისად.
"""

import json
import time
import uuid
from dataclasses import dataclass, field

from app.services.schema_retriever import schema_retriever
from app.services.sql_generator import sql_generator
from app.services.sql_validator import sql_validator
from app.services.query_executor import query_executor
from app.services.local_nlu import classify_and_generate
from app.models.schemas import ChatResponse, QueryResult, ChartSuggestion


# === საუბრის მეხსიერება (In-Memory) ===
_conversations: dict[str, list[dict]] = {}

MAX_SELF_CORRECTION_ATTEMPTS = 2


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

        ნაბიჯები:
        1. ლოკალური NLU (instant, Gemini-ს გარეშე)
        2. SQL ვალიდაცია
        3. DB-ზე გაშვება
        4. პასუხის ფორმირება
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        state = PipelineState(
            user_message=message,
            conversation_id=conversation_id,
            processing_start=time.time(),
        )

        try:
            # ========== ნაბიჯი 1: ლოკალური NLU ==========
            msg_lower = message.strip().lower()

            # /sql პირდაპირი ბრძანება (დეველოპერებისთვის)
            if msg_lower.startswith("/sql "):
                state.intent = "bi_query"
                state.generated_sql = message.strip()[5:].strip()
                state.chart_info = {"chart_type": "table", "chart_title": "SQL შედეგი"}
                return await self._execute_and_respond(state, message, conversation_id)

            # ლოკალური NLU
            nlu = classify_and_generate(message)

            if nlu.intent == "greeting":
                state.intent = "greeting"
                state.formatted_answer = nlu.answer or "გამარჯობა!"
                return self._direct_answer_response(state)

            if nlu.intent == "bi_query" and nlu.sql:
                state.intent = "bi_query"
                state.generated_sql = nlu.sql
                state.chart_info = {
                    "chart_type": nlu.chart_type or "table",
                    "chart_title": nlu.chart_title,
                    "x_axis": nlu.x_axis,
                    "y_axis": nlu.y_axis,
                }
                state.sql_explanation = nlu.explanation or ""
                return await self._execute_and_respond(state, message, conversation_id)

            # ========== Fallback: Gemini (თუ კვოტა ხელმისაწვდომია) ==========
            # ლოკალური NLU ვერ ცნო — ვცდი Gemini-ს
            try:
                conversation_history = self._get_conversation_history(conversation_id)
                gemini_intent = await sql_generator.classify_intent(message, conversation_history)

                if gemini_intent == "greeting":
                    state.intent = "greeting"
                    state.formatted_answer = (
                        "გამარჯობა! 👋 BeeEye — ბიზნეს ანალიტიკის AI.\n"
                        "დამისვი ნებისმიერი კითხვა ბიზნეს-მონაცემების შესახებ!"
                    )
                    return self._direct_answer_response(state)

                if gemini_intent == "unclear":
                    state.intent = "unclear"
                    return self._unclear_response(state)

                # bi_query ან followup — Gemini-ით SQL გენერაცია
                state.schema = await schema_retriever.get_full_schema()
                full_message = message
                if gemini_intent == "followup" and conversation_history:
                    full_message = f"კონტექსტი:\n{conversation_history}\n\nახალი კითხვა: {message}"

                sql_result = await sql_generator.generate_sql(
                    user_question=full_message,
                    schema=state.schema,
                    conversation_history=conversation_history,
                )

                state.generated_sql = sql_result.get("sql", "")
                state.sql_explanation = sql_result.get("explanation", "")
                state.chart_info = {
                    "chart_type": sql_result.get("chart_type", "table"),
                    "chart_title": sql_result.get("chart_title"),
                    "x_axis": sql_result.get("x_axis"),
                    "y_axis": sql_result.get("y_axis"),
                }

                validation = sql_validator.validate(state.generated_sql)
                if not validation.is_valid:
                    state.error = f"SQL ვალიდაცია: {validation.error_message}"
                    return self._unclear_response(state)

                state.generated_sql = validation.sanitized_sql
                return await self._execute_and_respond(state, message, conversation_id)

            except Exception as gemini_err:
                # Gemini მიუწვდომელია (rate limit / unavailable)
                # ვუბრუნებთ მეგობრულ "unclear" პასუხს
                state.intent = "unclear"
                state.error = str(gemini_err)
                return self._unclear_response(state)

        except Exception as e:
            state.error = f"სისტემური შეცდომა: {str(e)}"
            return self._error_response(state)

    async def _execute_and_respond(
        self,
        state: PipelineState,
        original_message: str,
        conversation_id: str,
    ) -> ChatResponse:
        """SQL-ის შესრულება და ქართული პასუხის ფორმირება."""
        # ვალიდაცია
        validation = sql_validator.validate(state.generated_sql)
        if not validation.is_valid:
            state.error = f"SQL ვალიდაცია ვერ გაიარა: {validation.error_message}"
            return self._error_response(state)
        state.generated_sql = validation.sanitized_sql

        # შესრულება
        try:
            state.query_result = await query_executor.execute(state.generated_sql)
        except Exception as e:
            state.error = f"მოთხოვნის შესრულება ვერ მოხერხდა: {str(e)}"
            return self._error_response(state)

        if not state.query_result or state.query_result.get("row_count", 0) == 0:
            state.formatted_answer = (
                "🔍 მოთხოვნა შესრულდა, მაგრამ ბაზაში შედეგი ვერ მოიძებნა.\n"
                "სცადეთ სხვა ფორმულირება."
            )
            return self._success_response(state)

        # ქართული პასუხის ფორმირება SQL შედეგიდან (Gemini-ს გარეშე)
        rows = state.query_result.get("rows", [])
        cols = state.query_result.get("columns", [])
        row_count = state.query_result.get("row_count", 0)
        explanation = state.sql_explanation or ""

        state.formatted_answer = self._format_answer_locally(
            question=original_message,
            rows=rows,
            cols=cols,
            row_count=row_count,
            explanation=explanation,
            chart_info=state.chart_info,
        )

        self._save_to_history(conversation_id, original_message, state.formatted_answer)
        return self._success_response(state)

    def _format_answer_locally(
        self,
        question: str,
        rows: list,
        cols: list,
        row_count: int,
        explanation: str,
        chart_info: dict,
    ) -> str:
        """ადგილობრივი პასუხის ფორმირება — Gemini-ს გარეშე."""
        chart_title = chart_info.get("chart_title", "მონაცემები")
        chart_type = chart_info.get("chart_type", "table")

        lines = [f"✅ **{chart_title}** — {row_count} ჩანაწერი მოიძებნა\n"]

        if explanation:
            lines.append(f"_{explanation}_\n")

        # პირველი 5 სტრიქონი ტექსტში
        if rows and cols:
            preview = rows[:5]
            for row in preview:
                if isinstance(row, dict):
                    parts = [f"**{k}:** {v}" for k, v in row.items()]
                elif isinstance(row, (list, tuple)):
                    parts = [f"**{cols[i]}:** {row[i]}" for i in range(min(len(cols), len(row)))]
                else:
                    parts = [str(row)]
                lines.append("• " + " | ".join(parts))

            if row_count > 5:
                lines.append(f"\n_...და კიდევ {row_count - 5} ჩანაწერი_")

        if chart_type not in ("none", "table") and chart_info.get("x_axis"):
            lines.append(f"\n📊 **გრაფიკი გაიხსნა დეშბორდზე** ({chart_type} chart)")

        return "\n".join(lines)

    # ===== helper responses =====

    def _direct_answer_response(self, state: PipelineState) -> ChatResponse:
        """პირდაპირი ტექსტური პასუხი (greeting, meta)."""
        processing_time = int((time.time() - state.processing_start) * 1000)
        return ChatResponse(
            answer=state.formatted_answer,
            conversation_id=state.conversation_id,
            processing_time_ms=processing_time,
        )

    def _success_response(self, state: PipelineState) -> ChatResponse:
        """წარმატებული პასუხის ფორმირება."""
        processing_time = int((time.time() - state.processing_start) * 1000)

        chart = None
        ct = state.chart_info.get("chart_type")
        if ct and ct not in ("none", None):
            chart = ChartSuggestion(
                chart_type=ct,
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

    def _unclear_response(self, state: PipelineState) -> ChatResponse:
        """გაუგებარი შეტყობინების პასუხი."""
        processing_time = int((time.time() - state.processing_start) * 1000)
        return ChatResponse(
            answer=(
                "ვერ ვიცანი ეს კითხვა. სცადეთ:\n\n"
                "- 'ჯამური შემოსავალი'\n"
                "- 'ტოპ 5 პროდუქტი'\n"
                "- 'შემოსავალი ქალაქების მიხედვით'\n"
                "- 'შეკვეთები სტატუსის მიხედვით'\n"
                "- 'გადახდის მეთოდები'\n"
                "- 'პროდუქტები მცირე მარაგით'\n\n"
                "ან ჩაწერეთ 'რა შეგიძლია' სრული სიისთვის."
            ),
            conversation_id=state.conversation_id,
            processing_time_ms=processing_time,
            error=state.error,
        )

    def _error_response(self, state: PipelineState) -> ChatResponse:
        """შეცდომის პასუხი."""
        processing_time = int((time.time() - state.processing_start) * 1000)
        return ChatResponse(
            answer=(
                "⚠️ ბაზასთან კავშირი ვერ მოხდა.\n"
                "გთხოვ, სცადე კიდევ ერთხელ."
            ),
            sql_query=state.generated_sql if state.generated_sql else None,
            conversation_id=state.conversation_id,
            processing_time_ms=processing_time,
            error=state.error,
        )

    def _get_conversation_history(self, conversation_id: str) -> str:
        history = _conversations.get(conversation_id, [])
        if not history:
            return ""
        recent = history[-10:]
        parts = []
        for msg in recent:
            role = "მომხმარებელი" if msg["role"] == "user" else "ასისტენტი"
            parts.append(f"{role}: {msg['content']}")
        return "\n".join(parts)

    def _save_to_history(self, conversation_id: str, user_msg: str, assistant_msg: str):
        if conversation_id not in _conversations:
            _conversations[conversation_id] = []
        _conversations[conversation_id].extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg},
        ])
        if len(_conversations[conversation_id]) > 20:
            _conversations[conversation_id] = _conversations[conversation_id][-20:]


# Singleton instance
pipeline = ConversationalBIPipeline()
