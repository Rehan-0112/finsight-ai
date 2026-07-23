from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

from src.rag.chunker import load_papers


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

documents = load_papers()


client = PersistentClient(
    path="data/vector_store"
)

collection = client.get_or_create_collection(
    name="finance_papers"
)


for i, doc in enumerate(documents):

    embedding = model.encode(
        doc["text"]
    ).tolist()

    collection.add(

        ids=[str(i)],

        embeddings=[embedding],

        documents=[doc["text"]],

        metadatas=[doc["metadata"]]

    )


print(

f"Stored {len(documents)} documents."

)