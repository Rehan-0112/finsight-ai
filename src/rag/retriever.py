from chromadb import PersistentClient

client = PersistentClient(
    path="data/vector_store"
)

collection = client.get_collection(
    "finance_papers"
)

query = "XGBoost financial forecasting"

results = collection.query(

    query_texts=[query],

    n_results=5,

    include=[

    "documents",

    "metadatas",

    "distances"

    ]

)

for i in range(5):

    print("\n")

    print("="*50)

    print(f"Result {i+1}")

    print("="*50)

    print()

    print(

        results['metadatas'][0][i]['title']

    )

    print()

    print(

        results['documents'][0][i][:300]

    )

    print(results['distances'][0][i])

    print(collection.count())
