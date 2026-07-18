from app.llm.gemini_client import rewrite_query
from app.rag.vector_db import get_collection


def retrieve_context(query: str, top_k: int = 4) -> list[dict]:
	if not query.strip():
		return []

	try:
		corrected_query = rewrite_query(query)
		collection = get_collection()
		result = collection.query(
			query_texts=[corrected_query],
			n_results=top_k,
			include=["documents", "metadatas", "distances"],
		)
	except Exception:
		return []

	documents = (result.get("documents") or [[]])[0]
	metadatas = (result.get("metadatas") or [[]])[0]
	distances = (result.get("distances") or [[]])[0]

	rows: list[dict] = []
	for doc, meta, distance in zip(documents, metadatas, distances):
		rows.append(
			{
				"text": doc,
				"source": (meta or {}).get("source", "unknown"),
				"score": float(distance) if distance is not None else None,
			}
		)
	return rows
