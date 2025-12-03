import logging

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq

from config.settings import settings
from modules.pii_masker import pii_masker
from modules.prompts import CUSTOMER_SUPPORT_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG retriever reference (will be set in main.py)
rag_retriever = None


class ChatbotError(Exception):
    """Custom exception for chatbot errors"""

    pass


class ChatbotHandler:
    def __init__(self):
        try:
            settings.validate()

            self.groq_chat = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.MODEL_NAME,
                temperature=0.7,  # Lower = more focused
                timeout=settings.REQUEST_TIMEOUT,
                max_retries=2,
                max_tokens=150,  # LIMIT TOKEN LENGTH (was 500)
            )

            self.store = {}

            logger.info(f"ChatbotHandler initialized with model: {settings.MODEL_NAME}")

        except Exception as e:
            logger.error(f"Failed to initialize ChatbotHandler: {str(e)}")
            raise ChatbotError(f"Chatbot initialization failed: {str(e)}")

    def get_session_history(self, session_id: str):
        """Retrieve or create chat history for a session"""
        try:
            if session_id not in self.store:
                self.store[session_id] = ChatMessageHistory()
                logger.info(f"Created new session: {session_id}")
            return self.store[session_id]
        except Exception as e:
            logger.error(f"Error accessing session {session_id}: {str(e)}")
            raise ChatbotError(f"Session error: {str(e)}")

    def clear_session(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        try:
            if session_id in self.store:
                del self.store[session_id]
                logger.info(f"Cleared session: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error clearing session {session_id}: {str(e)}")
            return False

    def get_response(
        self, user_message: str, customer_id: str, session_id: str = "default"
    ) -> dict:
        """
        Generate response with customer-specific RAG + PII masking

        Args:
            user_message: User's chat message
            customer_id: Customer identifier (e.g., "CUST-001")
            session_id: Session identifier (default: "default")

        Returns:
            dict: {
                "response": str,
                "pii_masked": bool,
                "context_retrieved": bool
            }
        """
        try:
            # Input validation
            if not user_message or not user_message.strip():
                raise ValueError("Message cannot be empty")

            if len(user_message) > settings.MAX_MESSAGE_LENGTH:
                raise ValueError(
                    f"Message too long (max {settings.MAX_MESSAGE_LENGTH} chars)"
                )

            clean_message = user_message.strip()

            # Step 1: PII Masking
            masked_message, pii_detected = pii_masker.mask_pii(clean_message)
            if pii_detected:
                logger.info(f"PII detected and masked for customer {customer_id}")

            # Step 2: Customer-specific RAG Retrieval
            context = ""
            context_found = False

            global rag_retriever
            if rag_retriever and rag_retriever.vectorstore:
                try:
                    context, context_found = rag_retriever.retrieve_customer_context(
                        customer_id=customer_id, query=masked_message
                    )
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {str(e)}")
                    context_found = False
            else:
                logger.warning("RAG not available - responses will not be personalized")

            # Step 3: Build prompt with context
            # Step 3: Build prompt with context
            system_prompt = CUSTOMER_SUPPORT_PROMPT
            if context_found:
                system_prompt += f"\n\n=== CUSTOMER PROFILE FOR {customer_id} ===\n{context}\n\nUse this information naturally in your responses. Reference their favorites, habits, and loyalty status as if you remember them from previous visits."
            else:
                system_prompt += f"\n\nNote: This is a new customer ({customer_id}). Provide general helpful information and offer to help them discover our menu and loyalty program."

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                ]
            )

            # Step 4: LCEL chain
            chain = prompt | self.groq_chat

            # Use customer_id in session for isolation
            full_session_id = f"{customer_id}:{session_id}"

            conversation = RunnableWithMessageHistory(
                chain,
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

            # Step 5: Invoke LLM
            logger.info(f"Processing message for customer {customer_id}")
            response = conversation.invoke(
                {"input": masked_message},
                config={"configurable": {"session_id": full_session_id}},
            )

            logger.info(f"Response generated for customer {customer_id}")

            return {
                "response": response.content,
                "pii_masked": pii_detected,
                "context_retrieved": context_found,
            }

        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise ChatbotError(f"Input validation failed: {str(e)}")

        except TimeoutError as e:
            logger.error(f"Timeout error for customer {customer_id}: {str(e)}")
            raise ChatbotError("Request timed out. Please try again.")

        except Exception as e:
            logger.error(f"Unexpected error in get_response: {str(e)}", exc_info=True)
            raise ChatbotError(f"Failed to generate response: {str(e)}")


# Initialize singleton
try:
    chatbot = ChatbotHandler()
except Exception as e:
    logger.critical(f"Failed to create chatbot instance: {str(e)}")
    raise
