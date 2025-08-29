from celery import shared_task
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio
import json

from app.services.content_engine import MagicalParentingContentEngine, DayTheme
from app.services.instagram_publisher import InstagramPublisher
from app.config import settings

@shared_task(bind=True, max_retries=3)
def generate_daily_content(self):
    """Generate today's content based on current theme"""
    try:
        # Create content engine
        content_engine = MagicalParentingContentEngine()
        
        # Get current theme
        theme = content_engine.get_daily_theme()
        
        # Run async content generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Generate carousel content
            carousel = loop.run_until_complete(
                content_engine.generate_carousel_content(theme)
            )
            
            # Generate video content on certain days (Mon, Wed, Fri)
            video = None
            if datetime.now().weekday() in [0, 2, 4]:  # Monday, Wednesday, Friday
                video = loop.run_until_complete(
                    content_engine.generate_video_content(theme)
                )
            
            # Store in database (simplified for demo)
            content_data = {
                "theme": theme.value,
                "carousel": {
                    "title": carousel.title,
                    "slides": carousel.slides,
                    "caption": carousel.caption,
                    "hashtags": carousel.hashtags,
                    "psychology_concept": carousel.psychology_concept,
                    "magical_element": carousel.magical_element,
                    "visual_prompts": carousel.visual_prompts
                },
                "video": {
                    "title": video.title,
                    "slides": video.slides,
                    "caption": video.caption,
                    "hashtags": video.hashtags,
                    "visual_prompts": video.visual_prompts
                } if video else None,
                "generated_at": datetime.now().isoformat()
            }
            
            print(f"✅ Daily content generated for {theme.value}")
            print(f"Carousel: {carousel.title}")
            if video:
                print(f"Video: {video.title}")
            
            return {
                "status": "success",
                "content": content_data,
                "generated_at": datetime.now().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        print(f"❌ Daily content generation failed: {exc}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 60  # 1, 2, 4 minutes
            print(f"🔄 Retrying in {retry_delay} seconds...")
            raise self.retry(countdown=retry_delay, exc=exc)
        else:
            print(f"❌ Max retries reached for daily content generation")
            raise

@shared_task(bind=True, max_retries=3)
def generate_weekly_content(self):
    """Generate a full week's worth of content"""
    try:
        # Create content engine
        content_engine = MagicalParentingContentEngine()
        
        # Run async weekly generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            weekly_content = loop.run_until_complete(
                content_engine.generate_weekly_content()
            )
            
            # Process weekly content
            processed_content = {}
            for date, content_pieces in weekly_content.items():
                processed_content[date] = []
                for piece in content_pieces:
                    processed_content[date].append({
                        "title": piece.title,
                        "type": piece.content_type.value,
                        "slides": piece.slides,
                        "caption": piece.caption,
                        "hashtags": piece.hashtags,
                        "psychology_concept": piece.psychology_concept,
                        "magical_element": piece.magical_element
                    })
            
            print(f"✅ Weekly content generated: {len(processed_content)} days")
            
            return {
                "status": "success",
                "weekly_content": processed_content,
                "generated_at": datetime.now().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        print(f"❌ Weekly content generation failed: {exc}")
        
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 300  # 5, 10, 20 minutes
            print(f"🔄 Retrying weekly generation in {retry_delay} seconds...")
            raise self.retry(countdown=retry_delay, exc=exc)
        else:
            print(f"❌ Max retries reached for weekly content generation")
            raise

@shared_task(bind=True, max_retries=3)
def generate_bot_teaser_campaign(self):
    """Generate content campaign for upcoming bot launch"""
    try:
        # Create content engine
        content_engine = MagicalParentingContentEngine()
        
        # Run async campaign generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            campaign_content = loop.run_until_complete(
                content_engine.generate_bot_teaser_campaign()
            )
            
            # Process campaign content
            processed_campaign = []
            for piece in campaign_content:
                processed_campaign.append({
                    "title": piece.title,
                    "slides": piece.slides,
                    "caption": piece.caption,
                    "hashtags": piece.hashtags,
                    "psychology_concept": piece.psychology_concept,
                    "magical_element": piece.magical_element,
                    "visual_prompts": piece.visual_prompts
                })
            
            print(f"✅ Bot teaser campaign generated: {len(processed_campaign)} pieces")
            
            return {
                "status": "success",
                "campaign_content": processed_campaign,
                "generated_at": datetime.now().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        print(f"❌ Bot teaser campaign generation failed: {exc}")
        
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 600  # 10, 20, 40 minutes
            print(f"🔄 Retrying campaign generation in {retry_delay} seconds...")
            raise self.retry(countdown=retry_delay, exc=exc)
        else:
            print(f"❌ Max retries reached for bot teaser campaign")
            raise

@shared_task(bind=True, max_retries=3)
def publish_scheduled_content(self, content_id: int, content_type: str, media_urls: List[str]):
    """Publish scheduled content to Instagram"""
    try:
        # Create Instagram publisher
        instagram_publisher = InstagramPublisher()
        
        # Run async publishing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if content_type == "carousel":
                result = loop.run_until_complete(
                    instagram_publisher.publish_carousel(content_id, media_urls)
                )
            elif content_type == "video":
                result = loop.run_until_complete(
                    instagram_publisher.publish_video(content_id, media_urls[0])
                )
            else:
                raise ValueError(f"Invalid content type: {content_type}")
            
            if "error" in result:
                raise Exception(result["error"])
            
            print(f"✅ Content {content_id} published successfully")
            print(f"Instagram post ID: {result['id']}")
            
            return {
                "status": "success",
                "instagram_post_id": result["id"],
                "post_url": result["post_url"],
                "published_at": result["published_at"]
            }
            
        finally:
            loop.close()
            
    except Exception as exc:
        print(f"❌ Content publishing failed: {exc}")
        
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 300  # 5, 10, 20 minutes
            print(f"🔄 Retrying publishing in {retry_delay} seconds...")
            raise self.retry(countdown=retry_delay, exc=exc)
        else:
            print(f"❌ Max retries reached for content publishing")
            raise

@shared_task
def cleanup_old_content():
    """Clean up old generated content (keep last 30 days)"""
    try:
        cutoff_date = datetime.now() - timedelta(days=30)
        print(f"🧹 Cleaning up content older than {cutoff_date}")
        
        # In production, implement actual database cleanup
        # For demo, just log the cleanup
        
        print("✅ Content cleanup completed")
        return {"status": "success", "cleaned_at": datetime.now().isoformat()}
        
    except Exception as exc:
        print(f"❌ Content cleanup failed: {exc}")
        return {"status": "error", "error": str(exc)}
