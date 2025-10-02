import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient
import os

# ------------------------------
# Step 1: Read CSV
# ------------------------------
df = pd.read_csv("/home/mhabrar/Downloads/NASA Space Apps/candidates_FIXED.csv")

# ------------------------------
# Step 2: Convert rows to LangChain Documents
# ------------------------------
docs = []
for _, row in df.iterrows():
    # Use some fields as main searchable text
    text = f"Mission: {row['mission']}, Object: {row['object_name']}, Disposition: {row['disposition']}"
    
    # The rest as metadata
    metadata = row.drop(["mission", "object_name", "disposition"]).to_dict()
    
    docs.append(Document(page_content=text, metadata=metadata))

# ------------------------------
# Step 3: Embedding model
# ------------------------------
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ------------------------------
# Step 4: Setup local Qdrant
# ------------------------------
qdrant = Qdrant.from_documents(
    documents=docs,
    embedding=embeddings,
    location=":memory:",  # for in-memory testing
    collection_name="exoplanets"
)

# If you already have Qdrant running locally, do:
# client = QdrantClient(url="http://localhost:6333")
# qdrant = Qdrant.from_documents(
#     documents=docs,
#     embedding=embeddings,
#     url="http://localhost:6333",
#     collection_name="exoplanets"
# )

# ------------------------------
# Step 5: Define search function
# ------------------------------
def search_exoplanets(query: str, k: int = 3):
    results = qdrant.similarity_search_with_score(query, k=k)
    for doc, score in results:
        print(f"Score: {score:.4f}")
        print(f"Content: {doc.page_content}")
        print(f"Metadata: {doc.metadata}\n")
    return results


# ------------------------------
# Example search
# ------------------------------
if __name__ == "__main__":
    print("\n🔍 Searching for: 'Hot Jupiter with small radius'")
    search_exoplanets("Hot Jupiter with small radius", k=3)
