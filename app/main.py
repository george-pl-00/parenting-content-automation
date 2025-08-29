from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
from datetime import datetime, timedelta

from app.database import get_db, init_db
from app.models import (
    ContentTemplateCreate, ContentTemplateResponse,
    GeneratedContentCreate, GeneratedContentResponse,
    UserInteractionCreate, UserInteractionResponse
)
from app.services.content_engine import MagicalParentingContentEngine, DayTheme
from app.services.instagram_publisher import InstagramPublisher
from app.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Automated Instagram content generation for magical parenting blog",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
content_engine = None
instagram_publisher = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global content_engine, instagram_publisher
    
    try:
        # Initialize database
        init_db()
        
        # Initialize content engine if OpenAI key is available
        if settings.openai_api_key:
            content_engine = MagicalParentingContentEngine()
            print("✅ Content engine initialized")
        
        # Initialize Instagram publisher if token is available
        if settings.instagram_access_token:
            instagram_publisher = InstagramPublisher()
            print("✅ Instagram publisher initialized")
            
    except Exception as e:
        print(f"❌ Startup error: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🎭 Magical Parenting Content Automation",
        "status": "running",
        "version": "1.0.0",
        "services": {
            "content_engine": content_engine is not None,
            "instagram_publisher": instagram_publisher is not None
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Check content engine
        if content_engine:
            health_status["services"]["content_engine"] = "healthy"
        else:
            health_status["services"]["content_engine"] = "unavailable"
        
        # Check Instagram publisher
        if instagram_publisher:
            connection_test = await instagram_publisher.test_connection()
            health_status["services"]["instagram_publisher"] = connection_test.get("status", "error")
        else:
            health_status["services"]["instagram_publisher"] = "unavailable"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Content Generation Endpoints
@app.post("/generate/daily", response_model=dict)
async def generate_daily_content(background_tasks: BackgroundTasks):
    """Generate today's content based on current theme"""
    if not content_engine:
        raise HTTPException(status_code=503, detail="Content engine not available")
    
    try:
        # Get current theme
        theme = content_engine.get_daily_theme()
        
        # Generate carousel content
        carousel = await content_engine.generate_carousel_content(theme)
        
        # Generate video content on certain days (Mon, Wed, Fri)
        video = None
        if datetime.now().weekday() in [0, 2, 4]:  # Monday, Wednesday, Friday
            video = await content_engine.generate_video_content(theme)
        
        # Store in database (background task)
        background_tasks.add_task(store_generated_content, carousel, video)
        
        return {
            "status": "success",
            "theme": theme.value,
            "carousel": {
                "title": carousel.title,
                "slides": carousel.slides,
                "caption": carousel.caption,
                "hashtags": carousel.hashtags,
                "psychology_concept": carousel.psychology_concept,
                "magical_element": carousel.magical_element
            },
            "video": {
                "title": video.title,
                "script_sections": video.slides,
                "caption": video.caption,
                "hashtags": video.hashtags
            } if video else None,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@app.post("/generate/weekly", response_model=dict)
async def generate_weekly_content(background_tasks: BackgroundTasks):
    """Generate a full week's worth of content"""
    if not content_engine:
        raise HTTPException(status_code=503, detail="Content engine not available")
    
    try:
        weekly_content = await content_engine.generate_weekly_content()
        
        # Store in database (background task)
        background_tasks.add_task(store_weekly_content, weekly_content)
        
        return {
            "status": "success",
            "weekly_content": weekly_content,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weekly generation failed: {str(e)}")

@app.post("/generate/custom", response_model=dict)
async def generate_custom_content(
    theme: str,
    topic: Optional[str] = None,
    content_type: str = "carousel"
):
    """Generate custom content with specific theme and topic"""
    if not content_engine:
        raise HTTPException(status_code=503, detail="Content engine not available")
    
    try:
        # Convert theme string to enum
        try:
            day_theme = DayTheme(theme)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid theme: {theme}")
        
        if content_type == "carousel":
            content = await content_engine.generate_carousel_content(day_theme, topic)
        elif content_type == "video":
            content = await content_engine.generate_video_content(day_theme, topic)
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")
        
        return {
            "status": "success",
            "content": {
                "title": content.title,
                "slides": content.slides,
                "caption": content.caption,
                "hashtags": content.hashtags,
                "psychology_concept": content.psychology_concept,
                "magical_element": content.magical_element,
                "visual_prompts": content.visual_prompts
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom generation failed: {str(e)}")

# Instagram Publishing Endpoints
@app.post("/instagram/publish/carousel")
async def publish_carousel(
    content_id: int,
    image_urls: List[str],
    background_tasks: BackgroundTasks
):
    """Publish carousel to Instagram"""
    if not instagram_publisher:
        raise HTTPException(status_code=503, detail="Instagram publisher not available")
    
    try:
        # Get content from database (simplified for demo)
        # In production, fetch actual content object
        content = await get_content_by_id(content_id)
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Publish to Instagram
        result = await instagram_publisher.publish_carousel(content, image_urls)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Update database status (background task)
        background_tasks.add_task(update_content_status, content_id, "posted", result)
        
        return {
            "status": "success",
            "instagram_post_id": result["id"],
            "post_url": result["post_url"],
            "published_at": result["published_at"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")

@app.post("/instagram/publish/video")
async def publish_video(
    content_id: int,
    video_url: str,
    background_tasks: BackgroundTasks
):
    """Publish video to Instagram"""
    if not instagram_publisher:
        raise HTTPException(status_code=503, detail="Instagram publisher not available")
    
    try:
        # Get content from database
        content = await get_content_by_id(content_id)
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Publish to Instagram
        result = await instagram_publisher.publish_video(content, video_url)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Update database status (background task)
        background_tasks.add_task(update_content_status, content_id, "posted", result)
        
        return {
            "status": "success",
            "instagram_post_id": result["id"],
            "post_url": result["post_url"],
            "published_at": result["published_at"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video publishing failed: {str(e)}")

@app.get("/instagram/insights")
async def get_instagram_insights():
    """Get Instagram account insights"""
    if not instagram_publisher:
        raise HTTPException(status_code=503, detail="Instagram publisher not available")
    
    try:
        insights = await instagram_publisher.get_account_insights()
        
        if "error" in insights:
            raise HTTPException(status_code=500, detail=insights["error"])
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.get("/instagram/scheduled")
async def get_scheduled_posts():
    """Get scheduled Instagram posts"""
    if not instagram_publisher:
        raise HTTPException(status_code=503, detail="Instagram publisher not available")
    
    try:
        scheduled = await instagram_publisher.get_scheduled_posts()
        
        if "error" in scheduled:
            raise HTTPException(status_code=500, detail=scheduled["error"])
        
        return scheduled
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get scheduled posts: {str(e)}")

# Analytics Endpoints
@app.get("/analytics/content/{content_id}")
async def get_content_analytics(content_id: int):
    """Get analytics for specific content piece"""
    if not instagram_publisher:
        raise HTTPException(status_code=503, detail="Instagram publisher not available")
    
    try:
        # Get Instagram insights
        insights = await instagram_publisher.get_post_insights(str(content_id))
        
        if "error" in insights:
            raise HTTPException(status_code=500, detail=insights["error"])
        
        return {
            "content_id": content_id,
            "instagram_insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

# Test Endpoints
@app.post("/test/generate-content")
async def test_content_generation():
    """Test endpoint for content generation"""
    if not content_engine:
        raise HTTPException(status_code=503, detail="Content engine not available")
    
    try:
        # Generate a simple test carousel
        theme = DayTheme.MAGICAL_MONDAY
        carousel = await content_engine.generate_carousel_content(theme, "test topic")
        
        return {
            "status": "success",
            "test_content": {
                "title": carousel.title,
                "slides": carousel.slides,
                "psychology_concept": carousel.psychology_concept,
                "magical_element": carousel.magical_element
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test generation failed: {str(e)}")

# Background task functions
async def store_generated_content(carousel, video=None):
    """Store generated content in database"""
    # In production, implement actual database storage
    print(f"Storing carousel: {carousel.title}")
    if video:
        print(f"Storing video: {video.title}")

async def store_weekly_content(weekly_content):
    """Store weekly content in database"""
    # In production, implement actual database storage
    for date, content_pieces in weekly_content.items():
        print(f"Storing content for {date}: {len(content_pieces)} pieces")

async def update_content_status(content_id: int, status: str, result: dict):
    """Update content status in database"""
    # In production, implement actual database update
    print(f"Updating content {content_id} status to {status}")

async def get_content_by_id(content_id: int):
    """Get content by ID from database"""
    # In production, implement actual database query
    # For demo, return a mock content object
    from app.services.content_engine import ContentPiece, ContentType, DayTheme
    
    return ContentPiece(
        theme=DayTheme.MAGICAL_MONDAY,
        content_type=ContentType.CAROUSEL,
        title="Mock Content",
        slides=["Slide 1", "Slide 2", "Slide 3", "Slide 4", "Slide 5"],
        caption="Mock caption",
        hashtags=["#Mock", "#Content"],
        visual_prompts=["Mock visual prompt"],
        psychology_concept="mock psychology",
        magical_element="mock magic",
        target_age="3-10",
        engagement_hooks=["Mock hook"],
        created_at=datetime.now()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
