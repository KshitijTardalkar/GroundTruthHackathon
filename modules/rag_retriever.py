import logging
import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_ollama import OllamaEmbeddings

from config.settings import settings

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Handle document retrieval using ChromaDB"""

    def __init__(self):
        # Initialize attributes first (always!)
        self.vectorstore = None
        self.embeddings = None

        try:
            # Use Ollama embeddings
            self.embeddings = OllamaEmbeddings(model="llama3.1")
            logger.info("✅ Embeddings initialized (Ollama)")

            # Load existing vector store if available
            if os.path.exists(settings.CHROMA_DB_PATH):
                self.vectorstore = Chroma(
                    persist_directory=settings.CHROMA_DB_PATH,
                    embedding_function=self.embeddings,
                )
                logger.info(f"✅ Loaded ChromaDB from {settings.CHROMA_DB_PATH}")
            else:
                logger.warning(
                    "⚠️  ChromaDB not found. Run: python scripts/index_customer_data.py"
                )

        except Exception as e:
            logger.error(f"Failed to initialize RAGRetriever: {str(e)}")
            logger.warning(
                "⚠️  RAG disabled - chatbot will work without personalization"
            )

    def retrieve_context(self, query: str, top_k: int = 3) -> tuple[str, bool]:
        """
        Retrieve relevant customer context (general search)

        Returns:
            tuple: (context_string, context_found)
        """
        if not self.vectorstore:
            return "", False

        try:
            docs = self.vectorstore.similarity_search(query, k=top_k)

            if docs:
                context_parts = []
                for i, doc in enumerate(docs, 1):
                    context_parts.append(f"Context {i}: {doc.page_content}")

                context = "\n\n".join(context_parts)
                logger.info(f"Retrieved {len(docs)} relevant documents")
                return context, True

            return "", False

        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return "", False

    def retrieve_customer_context(
        self, customer_id: str, query: str, top_k: int = 3
    ) -> tuple[str, bool]:
        """
        Retrieve context specific to a customer

        Args:
            customer_id: Customer identifier (e.g., "CUST-001")
            query: Search query
            top_k: Number of results to retrieve

        Returns:
            tuple: (context_string, context_found)
        """
        if not self.vectorstore:
            logger.warning("Vectorstore not initialized")
            return "", False

        try:
            # Try to search with customer_id in the content
            customer_query = f"{customer_id} {query}"
            docs = self.vectorstore.similarity_search(customer_query, k=top_k)

            # Filter docs that actually contain the customer_id
            customer_docs = [doc for doc in docs if customer_id in doc.page_content]

            # If we found customer-specific docs, use them
            if customer_docs:
                context_parts = []
                for i, doc in enumerate(customer_docs, 1):
                    context_parts.append(f"Context {i}: {doc.page_content}")

                context = "\n\n".join(context_parts)
                logger.info(
                    f"Retrieved {len(customer_docs)} documents for customer {customer_id}"
                )
                return context, True

            # If no customer-specific results, do general search
            logger.info(
                f"No customer-specific data for {customer_id}, doing general search"
            )
            return self.retrieve_context(query, top_k)

        except Exception as e:
            logger.error(f"Error retrieving customer context: {str(e)}")
            return "", False

    def index_documents(self, directory_path: str, append: bool = True) -> bool:
        """
        Index documents from directory

        Args:
            directory_path: Path to documents
            append: If True, add to existing vectorstore. If False, replace it.
        """
        try:
            logger.info(f"📚 Starting document indexing from: {directory_path}")

            if not os.path.exists(directory_path):
                logger.error(f"Directory not found: {directory_path}")
                return False

            if not self.embeddings:
                logger.error("Embeddings not initialized")
                return False

            # Load documents
            loader = DirectoryLoader(
                directory_path, glob="**/*.txt", loader_cls=TextLoader
            )
            documents = loader.load()

            if not documents:
                logger.warning(f"No .txt files found in {directory_path}")
                return False

            logger.info(f"Found {len(documents)} documents to index")

            # Create or append to vector store
            if append and self.vectorstore:
                # Add to existing vectorstore
                logger.info("Adding to existing vectorstore...")
                self.vectorstore.add_documents(documents)
                # No need to call persist() - langchain-chroma auto-persists
            else:
                # Create new vectorstore
                logger.info("Creating new vectorstore...")
                self.vectorstore = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=settings.CHROMA_DB_PATH,
                )
                # No need to call persist() - langchain-chroma auto-persists

            logger.info(f"✅ Indexed {len(documents)} documents successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error indexing documents: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


# Singleton instance
rag_retriever = RAGRetriever()
