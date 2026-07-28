"""
VoxLens — Embedding Service

Manages HuggingFace sentence-transformer embeddings and ChromaDB vector storage.
Provides transcript chunking, embedding, and storage.
"""

import logging

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logger = logging.getLogger("voxlens.embedding")

# Lazy-initialized instances
_embeddings = None
_chroma_client = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """Get or create the HuggingFace embeddings model."""
    global _embeddings
    if _embeddings is None:
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embedding model loaded")
    return _embeddings


def _get_chroma_client() -> chromadb.PersistentClient:
    """Get or create the ChromaDB persistent client."""
    global _chroma_client
    if _chroma_client is None:
        persist_dir = str(settings.chroma_path)
        logger.info(f"Initializing ChromaDB at: {persist_dir}")
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
        logger.info("ChromaDB initialized")
    return _chroma_client


def chunk_transcript(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[str]:
    """
    Split transcript text into chunks for embedding.

    Args:
        text: Full transcript text
        chunk_size: Target characters per chunk
        chunk_overlap: Overlap between chunks for context continuity

    Returns:
        List of text chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    logger.info(f"Transcript split into {len(chunks)} chunks")
    return chunks


def embed_and_store(
    meeting_id: str,
    chunks: list[str],
    metadatas: list[dict] | None = None,
) -> str:
    """
    Embed text chunks and store them in ChromaDB.

    Args:
        meeting_id: Unique meeting identifier (used as collection name)
        chunks: List of text chunks to embed
        metadatas: Optional metadata for each chunk

    Returns:
        Collection name
    """
    if not chunks:
        logger.warning("No chunks to embed")
        return meeting_id

    embeddings = _get_embeddings()
    client = _get_chroma_client()

    # Create or get collection for this meeting
    collection_name = f"meeting_{meeting_id.replace('-', '_')}"
    # Ensure collection name is valid (alphanumeric + underscores, 3-63 chars)
    collection_name = collection_name[:63]

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    # Generate embeddings
    logger.info(f"Generating embeddings for {len(chunks)} chunks...")
    vectors = embeddings.embed_documents(chunks)

    # Prepare IDs and metadata
    ids = [f"{meeting_id}_chunk_{i}" for i in range(len(chunks))]
    if metadatas is None:
        metadatas = [{"chunk_index": i, "meeting_id": meeting_id} for i in range(len(chunks))]

    # Upsert into ChromaDB
    collection.upsert(
        ids=ids,
        embeddings=vectors,
        documents=chunks,
        metadatas=metadatas,
    )

    logger.info(f"Stored {len(chunks)} embeddings in collection '{collection_name}'")
    return collection_name


def query_similar(
    meeting_id: str,
    query_text: str,
    n_results: int = 5,
) -> list[dict]:
    """
    Query ChromaDB for chunks similar to the query text.

    Args:
        meeting_id: Meeting to search within
        query_text: The search query
        n_results: Number of results to return

    Returns:
        List of dicts with keys: text, metadata, distance
    """
    embeddings = _get_embeddings()
    client = _get_chroma_client()

    collection_name = f"meeting_{meeting_id.replace('-', '_')}"
    collection_name = collection_name[:63]

    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        logger.warning(f"Collection '{collection_name}' not found")
        return []

    # Generate query embedding
    query_vector = embeddings.embed_query(query_text)

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(n_results, collection.count()),
    )

    # Format results
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        formatted.append({
            "text": doc,
            "metadata": meta,
            "distance": dist,
        })

    logger.info(f"Found {len(formatted)} similar chunks for query")
    return formatted


def delete_meeting_embeddings(meeting_id: str) -> None:
    """Delete all embeddings for a meeting."""
    client = _get_chroma_client()
    collection_name = f"meeting_{meeting_id.replace('-', '_')}"
    collection_name = collection_name[:63]

    try:
        client.delete_collection(name=collection_name)
        logger.info(f"Deleted embeddings collection: {collection_name}")
    except Exception as e:
        logger.warning(f"Could not delete collection '{collection_name}': {e}")
