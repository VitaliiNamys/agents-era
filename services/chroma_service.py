import chromadb
from collections import defaultdict
from config import DB_PERSIST_DIR, DB_COLLECTION_NAME

def get_resumes_data():
    chroma_client = chromadb.PersistentClient(path=DB_PERSIST_DIR)
    collection = chroma_client.get_collection(DB_COLLECTION_NAME)
    data = collection.get()

    print(f"\nTotal chunks in database: {len(data['documents'])}")

    # Group chunks by document ID
    doc_chunks = defaultdict(list)
    for chunk_id, metadata, content in zip(data['ids'], data['metadatas'], data['documents']):
        # Extract doc_id from chunk_id (format: "doc_id_chunk_index")
        doc_id = chunk_id.split('_chunk_')[0]

        # If it's a chunked document, use chunk_index for ordering
        if 'chunk_index' in metadata:
            doc_chunks[doc_id].append((metadata['chunk_index'], content))
        else:
            # If it's an old format document, treat it as a single chunk
            doc_chunks[doc_id].append((0, content))

    print(f"\nNumber of unique documents: {len(doc_chunks)}")
    # Combine chunks into complete documents
    complete_docs = []
    for doc_id, chunks in doc_chunks.items():
        # Sort chunks by their index
        sorted_chunks = sorted(chunks, key=lambda x: x[0])
        # Combine chunk contents
        full_content = ' '.join(chunk[1] for chunk in sorted_chunks)
        # Find metadata for this document
        # Look for metadata where either doc_id or id matches our document ID
        matching_metadata = None
        for m in data['metadatas']:
            if (m.get('doc_id') == doc_id or 
                m.get('id') == doc_id or 
                any(chunk_id.startswith(f"{doc_id}_chunk_") for chunk_id in data['ids'])):
                matching_metadata = m
                break

        if matching_metadata:
            complete_docs.append((doc_id, matching_metadata, full_content))
        else:
            # If no metadata found, create basic metadata
            complete_docs.append((doc_id, {'doc_id': doc_id, 'category': 'Unknown'}, full_content))

    print(f"Returning {len(complete_docs)} complete documents")

    return complete_docs
