from sqlalchemy.orm import Session

from app.llm.qwen_client import ask_qwen
from app.rag.retrieve import retrieve_context
from app.services.memory_service import (
    append_message,
    get_or_create_conversation,
    get_recent_memory_lines,
)


def chat(
    message: str,
    session_id: str,
    customer_id: int | None,
    top_k: int,
    db: Session,
) -> dict:
    conversation = get_or_create_conversation(
        db=db,
        session_id=session_id,
        customer_id=customer_id,
    )

    append_message(db, conversation.id, "user", message)
    memory_lines = get_recent_memory_lines(db, conversation.id, limit=6)

    chunks = retrieve_context(message, top_k=top_k)
    reply = ask_qwen(
        message=message,
        context_chunks=[c["text"] for c in chunks],
        memory_lines=memory_lines,
    )

    append_message(db, conversation.id, "assistant", reply)

    citations = [{"source": c["source"], "score": c.get("score")} for c in chunks]
    return {
        "reply": reply,
        "citations": citations,
        "intent": "chat",
    }
