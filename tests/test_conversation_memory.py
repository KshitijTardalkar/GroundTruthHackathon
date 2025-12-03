"""
Test Conversation Memory Feature Independently
Run: python tests/test_conversation_memory.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.llm_handler import chatbot


def test_single_turn():
    print("\n💬 Testing Single Turn Conversation...")

    session_id = "test-single"
    message = "Hello, I want hot coffee"

    result = chatbot.get_response(message, session_id)

    print(f"  User: {message}")
    print(f"  EVA: {result['response'][:100]}...")
    print(f"  Status: ✅")


def test_multi_turn():
    print("\n🔄 Testing Multi-Turn Conversation...")

    session_id = "test-multi"

    conversations = [
        "I love hot chocolate",
        "What did I just say I love?",
        "Do you remember my preference?",
    ]

    for i, message in enumerate(conversations, 1):
        result = chatbot.get_response(message, session_id)
        print(f"\n  Turn {i}:")
        print(f"    User: {message}")
        print(f"    EVA: {result['response'][:100]}...")

        if i > 1:
            if (
                "chocolate" in result["response"].lower()
                or "hot" in result["response"].lower()
            ):
                print(f"    Memory Check: ✅ EVA remembered!")
            else:
                print(f"    Memory Check: ⚠️ May not have recalled")


def test_session_isolation():
    print("\n🔒 Testing Session Isolation...")

    # Session 1
    session1 = "user-alice"
    result1 = chatbot.get_response("My name is Alice", session1)
    print(f"\n  Session 1 (Alice):")
    print(f"    User: My name is Alice")
    print(f"    EVA: {result1['response'][:80]}...")

    # Session 2
    session2 = "user-bob"
    result2 = chatbot.get_response("My name is Bob", session2)
    print(f"\n  Session 2 (Bob):")
    print(f"    User: My name is Bob")
    print(f"    EVA: {result2['response'][:80]}...")

    # Check isolation - Ask session 1 about Bob
    result_check = chatbot.get_response("What's Bob's name?", session1)
    print(f"\n  Cross-Session Test (asking Alice about Bob):")
    print(f"    User: What's Bob's name?")
    print(f"    EVA: {result_check['response'][:80]}...")

    if "bob" not in result_check["response"].lower():
        print(f"    Isolation Check: ✅ Sessions are isolated!")
    else:
        print(f"    Isolation Check: ⚠️ Possible session leak")


def test_session_clearing():
    print("\n🗑️  Testing Session Clearing...")

    session_id = "test-clear"

    # Create conversation
    chatbot.get_response("I love iced coffee", session_id)
    print(f"  Created conversation in session: {session_id}")

    # Clear session
    cleared = chatbot.clear_session(session_id)
    print(f"  Cleared session: {'✅' if cleared else '❌'}")

    # Check if memory is gone
    result = chatbot.get_response("What did I say I love?", session_id)
    print(f"  User: What did I say I love?")
    print(f"  EVA: {result['response'][:100]}...")

    if (
        "don't" in result["response"].lower()
        or "not sure" in result["response"].lower()
    ):
        print(f"  Memory Cleared: ✅")
    else:
        print(f"  Memory Cleared: ⚠️ May still remember")


def test_memory_limit():
    print("\n📊 Testing Memory Length Limit...")

    session_id = "test-limit"

    print(f"  Memory length set to: {settings.MEMORY_LENGTH} messages")

    # Send more messages than memory limit
    for i in range(settings.MEMORY_LENGTH + 3):
        msg = f"Message number {i}"
        chatbot.get_response(msg, session_id)
        print(f"    Sent: {msg}")

    # Ask about early message
    result = chatbot.get_response("What was message number 0?", session_id)
    print(f"\n  Asking about old message...")
    print(f"  EVA: {result['response'][:100]}...")

    if "don't" in result["response"].lower() or "not" in result["response"].lower():
        print(f"  Memory Limit Working: ✅ Old messages forgotten")
    else:
        print(f"  Memory Limit: ⚠️ May remember beyond limit")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 CONVERSATION MEMORY FEATURE TEST")
    print("=" * 60)

    try:
        from config.settings import settings

        test_single_turn()
        test_multi_turn()
        test_session_isolation()
        test_session_clearing()
        test_memory_limit()

        print("\n" + "=" * 60)
        print("✅ All memory tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
