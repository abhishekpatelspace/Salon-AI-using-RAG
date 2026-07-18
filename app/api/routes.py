from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.rag.ingest import ingest_knowledge
from app.schemas.booking import BookingRequest, BookingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.booking_service import create_booking
from app.services.chat_service import chat

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "salon-ai"}


@router.get("/health/db")
async def health_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={"status": "error", "database": "unreachable", "reason": str(exc)},
        ) from exc


@router.post("/rag/reindex")
async def rag_reindex(reset: bool = False):
    return ingest_knowledge(reset=reset)


@router.post("/chat", response_model=ChatResponse)
async def chat_api(req: ChatRequest, db: Session = Depends(get_db)):
    result = chat(
        message=req.message,
        session_id=req.session_id,
        customer_id=req.customer_id,
        top_k=req.top_k,
        db=db,
    )
    return ChatResponse(**result)


@router.post("/book", response_model=BookingResponse)
async def book_api(req: BookingRequest, db: Session = Depends(get_db)):
    result = create_booking(
        db=db,
        name=req.name,
        gender=req.gender,
        age=req.age,
        service_name=req.service,
        phone=req.phone,
        preferred_slot=req.preferred_slot,
        duration_minutes=req.duration_minutes,
        notes=req.notes,
    )
    return BookingResponse(**result)
