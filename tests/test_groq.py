from src.rag.groq_client import generate_response

response = generate_response(
    "Explain why moving averages are useful in stock forecasting."
)

print(response)