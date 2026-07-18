# Salon AI Assistant

Architecture:
Frontend -> FastAPI -> ChatService -> Gemini -> RAG -> Database

Run:
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

Environment:
- GEMINI_API_KEY=your_api_key
- DATABASE_URL=sqlite:///./salon_ai.db (optional, defaults to SQLite)
- MySQL example: DATABASE_URL=mysql+pymysql://root:password@localhost:3306/salon_ai
- CHROMA_PATH=./.chroma (optional)
- CHROMA_COLLECTION=salon_knowledge (optional)

MySQL Notes:
- Install dependencies: pip install -r requirements.txt
- Ensure MySQL server is running and the database exists.
- The app auto-creates tables on startup via SQLAlchemy metadata.
- Optional pool env vars: DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_RECYCLE

Knowledge Base:
- Put salon documents in data/knowledge
- Supported formats: .txt, .md, .json
- Reindex knowledge by calling POST /rag/reindex

API:
- GET /health
- GET /health/db
- POST /rag/reindex?reset=true
- POST /chat
- POST /book

Booking Request Fields:
- name
- gender
- age
- service
- phone
- preferred_slot (ISO datetime)
- duration_minutes (optional)
- notes (optional)

Booking SMS Notification:
- Booking confirmation SMS is sent to the provided phone if Twilio env vars are configured.
- If Twilio is not configured, booking still succeeds and response returns notification_status.

Sample chat request:
{
	"message": "What is the haircut price?",
	"session_id": "cust-101",
	"customer_id": null,
	"top_k": 4
}

Sample response:
{
	"reply": "Haircut prices are INR 700 for women and INR 500 for men.",
	"citations": [
		{"source": "data/knowledge/services_and_prices.md", "score": 0.12}
	],
	"intent": "chat"
}
