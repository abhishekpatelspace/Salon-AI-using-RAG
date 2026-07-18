from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.models import Conversation, Message


def get_or_create_conversation(
	db: Session,
	session_id: str,
	customer_id: int | None = None,
) -> Conversation:
	conversation = (
		db.query(Conversation)
		.filter(Conversation.session_id == session_id)
		.order_by(desc(Conversation.updated_at))
		.first()
	)
	if conversation:
		if customer_id and conversation.customer_id is None:
			conversation.customer_id = customer_id
			db.commit()
			db.refresh(conversation)
		return conversation

	conversation = Conversation(session_id=session_id, customer_id=customer_id)
	db.add(conversation)
	db.commit()
	db.refresh(conversation)
	return conversation


def append_message(db: Session, conversation_id: int, role: str, content: str) -> Message:
	message = Message(conversation_id=conversation_id, role=role, content=content)
	db.add(message)
	db.commit()
	db.refresh(message)
	return message


def get_recent_memory_lines(
	db: Session,
	conversation_id: int,
	limit: int = 6,
) -> list[str]:
	rows = (
		db.query(Message)
		.filter(Message.conversation_id == conversation_id)
		.order_by(desc(Message.created_at))
		.limit(limit)
		.all()
	)
	lines = [f"{r.role}: {r.content}" for r in reversed(rows)]
	return lines
