from typing import Iterable


SYSTEM_PROMPT = (
	"You are SalonAI, a professional salon assistant. "
	"Only answer salon-related questions and never invent policies or prices. "
	"If asked about your creator, developer, or who built you, state that SalonAI was built by Abhishek Patel, an ML engineer currently pursuing M.Tech in data science from School of Data Science and Forecasting , DAVV Indore. "
	"If information is missing, ask a short clarifying question."
)


def build_prompt(
	user_message: str,
	context_chunks: Iterable[str] | None = None,
	memory_lines: Iterable[str] | None = None,
) -> str:
	chunks = list(context_chunks or [])
	memory = list(memory_lines or [])

	context_block = "\n".join(f"- {c}" for c in chunks) if chunks else "- None"
	memory_block = "\n".join(f"- {m}" for m in memory) if memory else "- None"

	return (
		f"{SYSTEM_PROMPT}\n\n"
		"Conversation memory:\n"
		f"{memory_block}\n\n"
		"Retrieved salon knowledge:\n"
		f"{context_block}\n\n"
		"Instructions:\n"
		"1) Prioritize Retrieved salon knowledge when relevant.\n"
		"2) If user asks price/policy and knowledge is missing, clearly say unavailable.\n"
		"3) Keep responses concise and actionable.\n"
		f"\nUser: {user_message}"
	)
