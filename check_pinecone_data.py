from pinecone_utils import PineconeRAG
import json

# Initialize RAG
rag = PineconeRAG()

# Query for some sample results
test_query = "hydraulic system"
results = rag.query(test_query, top_k=3)

print(f"Query: '{test_query}'")
print(f"Found {len(results)} results\n")

for i, result in enumerate(results):
    print(f"\n--- Result {i+1} ---")
    print(f"ID: {result['id']}")
    print(f"Score: {result['score']:.4f}")
    print(f"Text preview: {result['text'][:100]}...")
    print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
    print("\nFormatted citation:", rag.format_citation(result, i+1))
