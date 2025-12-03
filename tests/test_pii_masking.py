"""
Test PII Masking Feature Independently
Run: python tests/test_pii_masking.py
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.pii_masker import pii_masker


def test_phone_masking():
    print("\n🔒 Testing Phone Number Masking...")
    test_cases = [
        "My phone is 9876543210",
        "Call me at (987) 654-3210",
        "Contact: +91-9876543210",
    ]

    for text in test_cases:
        masked, detected = pii_masker.mask_pii(text)
        print(f"  Original: {text}")
        print(f"  Masked:   {masked}")
        print(f"  PII Found: {'✅' if detected else '❌'}\n")


def test_email_masking():
    print("\n📧 Testing Email Masking...")
    test_cases = ["Email me at john@example.com", "Contact: sarah.johnson@company.org"]

    for text in test_cases:
        masked, detected = pii_masker.mask_pii(text)
        print(f"  Original: {text}")
        print(f"  Masked:   {masked}")
        print(f"  PII Found: {'✅' if detected else '❌'}\n")


def test_person_name_masking():
    print("\n👤 Testing Person Name Masking...")
    test_cases = [
        "My name is John Doe and I need help",
        "Sarah Johnson placed an order",
    ]

    for text in test_cases:
        masked, detected = pii_masker.mask_pii(text)
        print(f"  Original: {text}")
        print(f"  Masked:   {masked}")
        print(f"  PII Found: {'✅' if detected else '❌'}\n")


def test_mixed_pii():
    print("\n🔐 Testing Mixed PII...")
    text = "Hi, I'm John Doe, phone: 9876543210, email: john@test.com"
    masked, detected = pii_masker.mask_pii(text)
    entities = pii_masker.get_detected_entities(text)

    print(f"  Original: {text}")
    print(f"  Masked:   {masked}")
    print(f"  Entities Found: {', '.join(entities)}")
    print(f"  PII Found: {'✅' if detected else '❌'}\n")


def test_no_pii():
    print("\n✅ Testing Text Without PII...")
    text = "I'm cold and want hot chocolate"
    masked, detected = pii_masker.mask_pii(text)

    print(f"  Original: {text}")
    print(f"  Masked:   {masked}")
    print(f"  PII Found: {'❌ (Expected)' if not detected else '❌ (Unexpected!)'}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PII MASKING FEATURE TEST")
    print("=" * 60)

    try:
        test_phone_masking()
        test_email_masking()
        test_person_name_masking()
        test_mixed_pii()
        test_no_pii()

        print("=" * 60)
        print("✅ All PII masking tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
