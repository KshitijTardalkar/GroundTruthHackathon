"""
Test Full Integration: PII + RAG + Memory Together
Run: python tests/test_full_integration.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.llm_handler import chatbot


def test_pii_with_rag():
    print("\n🔒📚 Testing PII Masking + RAG Together...")

    session_id = "test-integration-1"

    # Message with PII that should trigger RAG
    message = "My phone is 9876543210 and I want my usual hot cocoa"

    result = chatbot.get_response(message, session_id)

    print(f"  User: {message}")
    print(f"  EVA: {result['response']}")
    print(f"\n  Feature Status:")
    print(f"    PII Masked: {'✅' if result['pii_masked'] else '❌'}")
    print(f"    Context Retrieved: {'✅' if result['context_retrieved'] else '❌'}")

    # Check if response is personalized despite PII masking
    if result["context_retrieved"]:
        print(f"    Personalization: ✅ RAG worked despite masked PII")
    else:
        print(f"    Personalization: ⚠️ No context retrieved")


def test_conversation_with_context():
    print("\n💬📚 Testing Conversation Memory + RAG...")

    session_id = "test-integration-2"

    conversations = [
        "I love hot drinks",
        "What would you recommend based on what I said?",
    ]

    for i, message in enumerate(conversations, 1):
        result = chatbot.get_response(message, session_id)
        print(f"\n  Turn {i}: {message}")
        print(f"  EVA: {result['response'][:120]}...")
        print(f"  Context Used: {'✅' if result['context_retrieved'] else '❌'}")


def test_full_scenario():
    print("\n🎭 Testing Full Customer Scenario...")

    session_id = "test-scenario"

    scenario = [
        {
            "user": "Hi, my email is john@test.com and I'm feeling cold",
            "check": "Should mask email + understand 'cold' context",
        },
        {
            "user": "What's my usual order?",
            "check": "Should retrieve purchase history from RAG",
        },
        {
            "user": "Do you remember I said I'm cold?",
            "check": "Should remember from conversation memory",
        },
        {
            "user": "What discount do I have?",
            "check": "Should retrieve loyalty info from RAG",
        },
    ]

    for i, step in enumerate(scenario, 1):
        result = chatbot.get_response(step["user"], session_id)

        print(f"\n  Step {i}:")
        print(f"    User: {step['user']}")
        print(f"    Expected: {step['check']}")
        print(f"    EVA: {result['response'][:100]}...")
        print(f"    Features Active:")
        print(f"      - PII Masked: {'✅' if result['pii_masked'] else '❌'}")
        print(f"      - RAG Context: {'✅' if result['context_retrieved'] else '❌'}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 FULL INTEGRATION TEST")
    print("=" * 60)

    try:
        test_pii_with_rag()
        test_conversation_with_context()
        test_full_scenario()

        print("\n" + "=" * 60)
        print("✅ All integration tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
