import hashlib
import json
from pathlib import Path

from app.rag.vector_db import get_collection, reset_collection


SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".pdf"}



def _chunk_text(text: str, chunk_size: int = 900, overlap: int = 140) -> list[str]:
	text = " ".join(text.split())
	if not text:
		return []

	chunks: list[str] = []
	start = 0
	while start < len(text):
		end = min(start + chunk_size, len(text))
		chunks.append(text[start:end])
		if end == len(text):
			break
		start = max(end - overlap, start + 1)
	return chunks


def _read_file_text(path: Path) -> str:
	suffix = path.suffix.lower()
	if suffix == ".json":
		raw = json.loads(path.read_text(encoding="utf-8"))
		return json.dumps(raw, ensure_ascii=True)
	elif suffix == ".pdf":
		try:
			from pypdf import PdfReader
			reader = PdfReader(path)
			text = []
			for page in reader.pages:
				page_text = page.extract_text()
				if page_text:
					text.append(page_text)
			return "\n".join(text)
		except Exception as e:
			print(f"[SalonAI] Error reading PDF {path}: {e}")
			return ""
	return path.read_text(encoding="utf-8")


def ingest_knowledge(
	knowledge_dir: str = "data/knowledge",
	reset: bool = False,
) -> dict:
	root = Path(knowledge_dir)
	if not root.exists():
		return {
			"indexed_files": 0,
			"indexed_chunks": 0,
			"message": f"Knowledge directory not found: {knowledge_dir}",
		}

	collection = reset_collection() if reset else get_collection()

	total_files = 0
	total_chunks = 0
	for file_path in root.rglob("*"):
		if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
			continue

		text = _read_file_text(file_path)
		chunks = _chunk_text(text)
		if not chunks:
			continue

		file_rel = str(file_path.as_posix())
		ids: list[str] = []
		metadatas: list[dict] = []
		documents: list[str] = []
		for i, chunk in enumerate(chunks):
			digest = hashlib.md5(f"{file_rel}:{i}:{chunk}".encode("utf-8")).hexdigest()[:12]
			ids.append(f"{file_rel}:{i}:{digest}")
			metadatas.append({"source": file_rel, "chunk_index": i})
			documents.append(chunk)

		collection.upsert(ids=ids, metadatas=metadatas, documents=documents)
		total_files += 1
		total_chunks += len(chunks)

	return {
		"indexed_files": total_files,
		"indexed_chunks": total_chunks,
		"message": "Knowledge ingestion completed",
	}
