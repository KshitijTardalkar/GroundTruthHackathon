import logging

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

logger = logging.getLogger(__name__)


class PIIMasker:
    """Handle PII detection and masking using Microsoft Presidio"""

    def __init__(self):
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            logger.info("PIIMasker initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PIIMasker: {str(e)}")
            raise

    def mask_pii(self, text: str) -> tuple[str, bool]:
        """
        Detect and mask PII in text

        Returns:
            tuple: (masked_text, pii_detected)
        """
        try:
            # Analyze text for PII entities
            results = self.analyzer.analyze(
                text=text,
                entities=[
                    "PHONE_NUMBER",
                    "EMAIL_ADDRESS",
                    "PERSON",
                    "CREDIT_CARD",
                    "IBAN_CODE",
                    "US_SSN",
                ],
                language="en",
            )

            if results:
                # Mask detected entities
                anonymized_result = self.anonymizer.anonymize(
                    text=text, analyzer_results=results
                )

                logger.info(f"PII detected and masked: {len(results)} entities")
                return anonymized_result.text, True

            return text, False

        except Exception as e:
            logger.error(f"Error in PII masking: {str(e)}")
            # Return original text if masking fails (fail-safe)
            return text, False

    def get_detected_entities(self, text: str) -> list[str]:
        """Get list of detected PII entity types"""
        try:
            results = self.analyzer.analyze(text=text, language="en")
            return [result.entity_type for result in results]
        except Exception as e:
            logger.error(f"Error detecting entities: {str(e)}")
            return []


# Singleton instance
pii_masker = PIIMasker()
