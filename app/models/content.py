from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# SQLAlchemy Models
class ContentTemplate(Base):
    __tablename__ = "content_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # 'carousel', 'video', 'story'
    theme = Column(String(100), nullable=False)  # 'magical_monday', 'tiny_tales_tuesday'
    psychology_concept = Column(Text)
    magical_element = Column(Text)
    target_age_group = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    generated_content = relationship("GeneratedContent", back_populates="template")

class GeneratedContent(Base):
    __tablename__ = "generated_content"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("content_templates.id"))
    content_data = Column(JSON)  # Stores slides, captions, hashtags
    visual_prompts = Column(ARRAY(Text))
    status = Column(String(20), default="generated")  # 'generated', 'approved', 'posted'
    instagram_post_id = Column(String(100))
    performance_metrics = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_time = Column(DateTime(timezone=True))
    posted_at = Column(DateTime(timezone=True))
    
    # Relationships
    template = relationship("ContentTemplate", back_populates="generated_content")
    user_interactions = relationship("UserInteraction", back_populates="content")

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("generated_content.id"))
    interaction_type = Column(String(50))  # 'like', 'comment', 'share', 'save'
    user_data = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content = relationship("GeneratedContent", back_populates="user_interactions")

# Pydantic Models for API
class ContentTemplateCreate(BaseModel):
    type: str
    theme: str
    psychology_concept: Optional[str] = None
    magical_element: Optional[str] = None
    target_age_group: Optional[str] = None

class ContentTemplateResponse(BaseModel):
    id: int
    type: str
    theme: str
    psychology_concept: Optional[str]
    magical_element: Optional[str]
    target_age_group: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class GeneratedContentCreate(BaseModel):
    template_id: int
    content_data: dict
    visual_prompts: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None

class GeneratedContentResponse(BaseModel):
    id: int
    template_id: int
    content_data: dict
    visual_prompts: Optional[List[str]]
    status: str
    instagram_post_id: Optional[str]
    performance_metrics: Optional[dict]
    created_at: datetime
    scheduled_time: Optional[datetime]
    posted_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserInteractionCreate(BaseModel):
    content_id: int
    interaction_type: str
    user_data: Optional[dict] = None

class UserInteractionResponse(BaseModel):
    id: int
    content_id: int
    interaction_type: str
    user_data: Optional[dict]
    timestamp: datetime
    
    class Config:
        from_attributes = True
