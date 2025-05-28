import pandas as pd
import chromadb
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.core.schema import Document, TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SentenceSplitter
import os

from services.llm_service import llm
from config import OPENAI_API_KEY, DB_PERSIST_DIR, DB_COLLECTION_NAME

df = pd.read_csv("data/Resume.csv")
# Select 30 random records from the dataset
resume_data = df[["ID", "Resume_str", "Category"]].dropna().sample(n=30).to_dict('records')

if not os.path.exists(DB_PERSIST_DIR):
    os.makedirs(DB_PERSIST_DIR)

chroma_client = chromadb.PersistentClient(path=DB_PERSIST_DIR)
try:
    print("\nTrying to load existing collection...")
    collection = chroma_client.get_collection(DB_COLLECTION_NAME)
    print(f"Successfully loaded collection '{DB_COLLECTION_NAME}'")
except:
    print(f"\nCreating new collection '{DB_COLLECTION_NAME}'...")
    collection = chroma_client.create_collection(DB_COLLECTION_NAME)

vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Check if collection has any documents
has_documents = len(collection.get()['ids']) > 0
print(f"Collection has existing documents: {has_documents}")

# Configure LlamaIndex settings
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY,
    embed_batch_size=2
)
Settings.llm = llm

text_splitter = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=20,
    separator=" ",
    paragraph_separator="\n\n"
)

new_nodes = []
for record in resume_data:
    doc_id = str(record['ID'])
    # Create base document
    doc = Document(
        text=str(record['Resume_str']),
        metadata={
            'doc_id': doc_id,
            'category': record.get('Category'),
        }
    )

    nodes = text_splitter.get_nodes_from_documents([doc])

    # Update node metadata to maintain relationship with original document
    for i, node in enumerate(nodes):
        chunk_id = f"{doc_id}_chunk_{i}"
        node.metadata.update({
            'chunk_id': chunk_id,
            'doc_id': doc_id,
            'category': record.get('Category'),
            'chunk_index': i,
            'total_chunks': len(nodes)
        })
        new_node = TextNode(
            text=node.text,
            metadata=node.metadata,
            id_=chunk_id
        )
        new_nodes.append(new_node)

if new_nodes:
    print(f"\nProcessing {len(new_nodes)} new document chunks...")
    if not has_documents:
        index = VectorStoreIndex(
            nodes=new_nodes,
            storage_context=storage_context,
            show_progress=True
        )
    else:
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
        index.insert_nodes(new_nodes, show_progress=True)
    print("Document processing complete!")
else:
    print("\nNo new documents to add")
