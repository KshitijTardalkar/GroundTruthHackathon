"""
Script to index customer data AND business info into ChromaDB
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

from config.settings import settings
from modules.rag_retriever import rag_retriever

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Index both customer profiles and business information"""
    logger.info("Starting data indexing...")

    # Check directories exist
    customer_path = settings.CUSTOMER_DATA_PATH
    business_path = "./data/business_info"

    if not os.path.exists(customer_path):
        logger.error(f"Customer data directory not found: {customer_path}")
        return

    if not os.path.exists(business_path):
        logger.error(f"Business info directory not found: {business_path}")
        return

    # Index customer data
    logger.info(f"Indexing customer profiles from {customer_path}...")
    success1 = rag_retriever.index_documents(customer_path)

    # Index business data (this will add to existing vectorstore)
    logger.info(f"Indexing business info from {business_path}...")
    success2 = rag_retriever.index_documents(business_path)

    if success1 and success2:
        logger.info("✅ All data indexed successfully!")
    else:
        logger.error("❌ Some indexing failed")


if __name__ == "__main__":
    main()
