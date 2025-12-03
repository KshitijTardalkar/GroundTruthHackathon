"""
Test RAG Retrieval Feature Independently
Run: python tests/test_rag_retrieval.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import settings
from modules.rag_retriever import rag_retriever


def test_context_retrieval():
    print("\n📚 Testing Context Retrieval...")

    if not rag_retriever.vectorstore:
        print("  ❌ ChromaDB not found!")
        print("  Run: python scripts/index_customer_data.py")
        return False

    test_queries = [
        {
            "query": "I want my usual hot cocoa",
            "expected": "Should retrieve John's profile (Hot Cocoa favorite)",
        },
        {
            "query": "I love iced coffee",
            "expected": "Should retrieve Sarah's profile (Iced Americano)",
        },
        {
            "query": "I'm a vegan customer",
            "expected": "Should retrieve Sarah's dietary restrictions",
        },
        {
            "query": "What's my loyalty discount?",
            "expected": "Should retrieve customer loyalty info",
        },
    ]

    for i, test in enumerate(test_queries, 1):
        print(f"\n  Test {i}: {test['query']}")
        print(f"  Expected: {test['expected']}")

        context, found = rag_retriever.retrieve_context(test["query"], top_k=2)

        if found:
            print(f"  Status: ✅ Context Retrieved")
            print(f"  Preview: {context[:200]}...")
        else:
            print(f"  Status: ❌ No context found")

    return True


def test_semantic_search():
    print("\n🔍 Testing Semantic Search Quality...")

    # Test if similar queries retrieve same customer
    queries = [
        "hot chocolate preference",
        "cocoa drink favorite",
        "warm beverage history",
    ]

    print("  Testing: Do similar queries return consistent results?")
    contexts = []

    for query in queries:
        context, found = rag_retriever.retrieve_context(query, top_k=1)
        contexts.append(context[:100])
        print(f"    Query: '{query}'")
        print(f"    Preview: {context[:80]}...")

    # Check if contexts are similar
    if len(set(contexts)) == 1:
        print("\n  ✅ Semantic search is consistent!")
    else:
        print("\n  ⚠️  Different results for similar queries")


def test_no_match():
    print("\n❌ Testing Queries with No Matches...")

    queries = [
        "What's the weather like?",
        "Tell me about politics",
        "Random unrelated topic",
    ]

    for query in queries:
        context, found = rag_retriever.retrieve_context(query)
        print(f"  Query: '{query}'")
        print(
            f"  Context Found: {'❌ (Expected)' if not found else '✅ (Unexpected!)'}"
        )


def check_indexed_data():
    print("\n📊 Checking Indexed Data...")

    if not os.path.exists(settings.CUSTOMER_DATA_PATH):
        print(f"  ❌ Data directory not found: {settings.CUSTOMER_DATA_PATH}")
        return False

    files = [f for f in os.listdir(settings.CUSTOMER_DATA_PATH) if f.endswith(".txt")]
    print(f"  Data files found: {len(files)}")
    for f in files:
        print(f"    - {f}")

    if not os.path.exists(settings.CHROMA_DB_PATH):
        print(f"\n  ❌ ChromaDB not found at: {settings.CHROMA_DB_PATH}")
        print(f"  Run: python scripts/index_customer_data.py")
        return False

    print(f"\n  ✅ ChromaDB exists at: {settings.CHROMA_DB_PATH}")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 RAG RETRIEVAL FEATURE TEST")
    print("=" * 60)

    try:
        if check_indexed_data():
            test_context_retrieval()
            test_semantic_search()
            test_no_match()

        print("\n" + "=" * 60)
        print("✅ All RAG tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
