"""
WeatherGPT Database Models
SQLAlchemy models for conversation history and user sessions
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for tracking sessions and preferences."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User preferences
    preferred_language = Column(String(10), default="en")
    preferred_role = Column(String(50), default="citizen")
    preferred_location = Column(String(255), nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(session_id={self.session_id}, role={self.preferred_role})>"


class Conversation(Base):
    """Conversation model for storing chat history."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, messages={len(self.messages)})>"


class Message(Base):
    """Message model for individual chat messages."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # Query metadata
    query_metadata = Column(JSON, nullable=True)  # stores intent, location, etc.
    weather_data = Column(JSON, nullable=True)  # stores weather snapshot
    llm_tier_used = Column(String(20), nullable=True)  # which LLM tier was used

    # User context
    user_role = Column(String(50), default="citizen")  # citizen/farmer/pilot/disaster-manager
    user_language = Column(String(10), default="en")
    user_location = Column(String(255), nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, content={self.content[:50]}...)>"


class WeatherAlert(Base):
    """Weather alert model for storing alert history and subscriptions."""
    __tablename__ = "weather_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_session_id = Column(String(255), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Alert details
    location = Column(String(255), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)

    severity = Column(String(20), nullable=False)  # normal/caution/warning/severe
    alert_type = Column(String(50), nullable=False)  # rain/temperature/wind/storm
    message = Column(Text, nullable=False)

    # Delivery status
    sent_via_sms = Column(Integer, default=0)  # 0=not sent, 1=sent, 2=failed
    phone_number = Column(String(20), nullable=True)

    # Weather snapshot
    weather_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<WeatherAlert(location={self.location}, severity={self.severity})>"
