"""
Context and conversation history management.
Maintains the last N messages for each session.
"""

from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict, deque

from models.schemas import ConversationMessage, MessageRole
from config import settings
from utils.logger import logger


class ContextManager:
    """Manages conversation context and history for each session."""
    
    def __init__(self, max_messages: int = None):
        """Initialize context manager."""
        self.max_messages = max_messages or settings.context_window_size
        self.conversations: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.max_messages)
        )
    
    def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """Add a message to the conversation history."""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.conversations[session_id].append(message)
        logger.debug(f"Added {role} message to session {session_id}")
    
    def get_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Get conversation history for a session."""
        if session_id not in self.conversations:
            return []
        
        messages = list(self.conversations[session_id])
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_formatted_history(self, session_id: str) -> str:
        """Get conversation history formatted as a string."""
        messages = self.get_history(session_id)
        
        if not messages:
            return "No previous conversation."
        
        formatted = []
        for msg in messages:
            formatted.append(f"{msg.role.upper()}: {msg.content}")
        
        return "\n".join(formatted)
    
    def has_context(self, session_id: str) -> bool:
        """Check if session has conversation history."""
        return session_id in self.conversations and len(self.conversations[session_id]) > 0
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session."""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation history for session {session_id}")


# Global context manager instance
context_manager = ContextManager()