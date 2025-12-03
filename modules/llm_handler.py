from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq

from config.settings import settings
from modules.prompts import CUSTOMER_SUPPORT_PROMPT


class ChatbotHandler:
    def __init__(self):
        self.groq_chat = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=0.7,
        )

        # Session-based memory storage
        self.store = {}

        # Modern prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CUSTOMER_SUPPORT_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        # LCEL chain using pipe operator
        chain = self.prompt | self.groq_chat

        # Wrap with message history
        self.conversation = RunnableWithMessageHistory(
            chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def get_session_history(self, session_id: str):
        """Retrieve or create chat history for a session"""
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]

    def get_response(self, user_message: str, session_id: str = "default") -> str:
        """Generate response using LCEL invoke pattern"""
        response = self.conversation.invoke(
            {"input": user_message}, config={"configurable": {"session_id": session_id}}
        )
        return response.content


# Singleton instance
chatbot = ChatbotHandler()
