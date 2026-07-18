import os

import chromadb
from chromadb.config import Settings


CHROMA_PATH = os.getenv("CHROMA_PATH", "./.chroma")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "salon_knowledge")

_client = chromadb.PersistentClient(
	path=CHROMA_PATH,
	settings=Settings(anonymized_telemetry=False),
)


def get_collection():
	return _client.get_or_create_collection(name=CHROMA_COLLECTION)


def reset_collection():
	try:
		_client.delete_collection(CHROMA_COLLECTION)
	except Exception:
		# Missing collection is fine during first run.
		pass
	return _client.get_or_create_collection(name=CHROMA_COLLECTION)
