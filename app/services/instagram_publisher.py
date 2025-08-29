import requests
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.config import settings
from app.services.content_engine import ContentPiece, ContentType
import asyncio

class InstagramPublisher:
    """Handle Instagram posting and scheduling"""
    
    def __init__(self):
        if not settings.instagram_access_token:
            raise ValueError("Instagram access token is required")
            
        self.access_token = settings.instagram_access_token
        self.business_account_id = settings.instagram_business_account_id
        self.base_url = f"https://graph.facebook.com/{settings.instagram_api_version}"
        
        # Optimal posting times (in production, use analytics to optimize)
        self.optimal_times = [
            "09:00", "12:00", "15:00", "18:00", "20:00"
        ]
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = datetime.now()
        self.rate_limit = settings.instagram_rate_limit

    async def publish_carousel(self, content: ContentPiece, image_urls: List[str]) -> dict:
        """Post carousel to Instagram"""
        try:
            # Check rate limits
            await self._check_rate_limit()
            
            # Create media objects
            media_ids = []
            for i, image_url in enumerate(image_urls):
                media_data = {
                    "image_url": image_url,
                    "caption": content.slides[i] if i < len(content.slides) else "",
                    "access_token": self.access_token
                }
                
                # Create media container
                response = requests.post(
                    f"{self.base_url}/{self.business_account_id}/media",
                    data=media_data
                )
                
                if response.status_code == 200:
                    media_id = response.json().get("id")
                    media_ids.append(media_id)
                else:
                    print(f"Error creating media {i}: {response.text}")
                    return {"error": f"Media creation failed: {response.text}"}
            
            # Publish carousel
            post_data = {
                "caption": f"{content.caption}\n\n{' '.join(content.hashtags)}",
                "media_type": "CAROUSEL",
                "children": media_ids,
                "access_token": self.access_token
            }
            
            response = requests.post(
                f"{self.base_url}/{self.business_account_id}/media_publish",
                data=post_data
            )
            
            if response.status_code == 200:
                post_result = response.json()
                return {
                    "id": post_result.get("id"),
                    "status": "published",
                    "post_url": f"https://instagram.com/p/{post_result.get('id')}",
                    "published_at": datetime.now().isoformat()
                }
            else:
                return {"error": f"Publishing failed: {response.text}"}
                
        except Exception as e:
            print(f"Publishing error: {e}")
            return {"error": str(e)}

    async def publish_video(self, content: ContentPiece, video_url: str) -> dict:
        """Post video content to Instagram"""
        try:
            await self._check_rate_limit()
            
            # Create video media container
            media_data = {
                "media_type": "REELS",
                "video_url": video_url,
                "caption": f"{content.caption}\n\n{' '.join(content.hashtags)}",
                "access_token": self.access_token
            }
            
            response = requests.post(
                f"{self.base_url}/{self.business_account_id}/media",
                data=media_data
            )
            
            if response.status_code == 200:
                media_id = response.json().get("id")
                
                # Publish the video
                publish_data = {
                    "creation_id": media_id,
                    "access_token": self.access_token
                }
                
                publish_response = requests.post(
                    f"{self.base_url}/{self.business_account_id}/media_publish",
                    data=publish_data
                )
                
                if publish_response.status_code == 200:
                    post_result = publish_response.json()
                    return {
                        "id": post_result.get("id"),
                        "status": "published",
                        "post_url": f"https://instagram.com/p/{post_result.get('id')}",
                        "published_at": datetime.now().isoformat()
                    }
                else:
                    return {"error": f"Video publishing failed: {publish_response.text}"}
            else:
                return {"error": f"Video media creation failed: {response.text}"}
                
        except Exception as e:
            print(f"Video publishing error: {e}")
            return {"error": str(e)}

    async def schedule_content(self, content_pieces: List[ContentPiece], 
                             start_date: datetime) -> List[dict]:
        """Schedule multiple pieces of content"""
        scheduled_posts = []
        
        for i, content in enumerate(content_pieces):
            # Calculate optimal posting time
            post_time = self._calculate_optimal_time(start_date, i)
            
            scheduled_post = {
                "content": content,
                "scheduled_time": post_time.isoformat(),
                "status": "scheduled",
                "estimated_engagement": self._estimate_engagement(content)
            }
            scheduled_posts.append(scheduled_post)
            
        return scheduled_posts

    async def get_account_insights(self) -> dict:
        """Get Instagram account performance insights"""
        try:
            await self._check_rate_limit()
            
            # Get basic account metrics
            metrics = [
                "impressions", "reach", "profile_views", "follower_count",
                "email_contacts", "phone_call_clicks", "text_message_clicks"
            ]
            
            insights_url = f"{self.base_url}/{self.business_account_id}/insights"
            params = {
                "metric": ",".join(metrics),
                "period": "day",
                "access_token": self.access_token
            }
            
            response = requests.get(insights_url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get insights: {response.text}"}
                
        except Exception as e:
            print(f"Insights error: {e}")
            return {"error": str(e)}

    async def get_post_insights(self, post_id: str) -> dict:
        """Get performance metrics for a specific post"""
        try:
            await self._check_rate_limit()
            
            metrics = [
                "impressions", "reach", "engagement", "saved",
                "video_views", "video_view_rate"
            ]
            
            insights_url = f"{self.base_url}/{post_id}/insights"
            params = {
                "metric": ",".join(metrics),
                "access_token": self.access_token
            }
            
            response = requests.get(insights_url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to get post insights: {response.text}"}
                
        except Exception as e:
            print(f"Post insights error: {e}")
            return {"error": str(e)}

    def _calculate_optimal_time(self, start_date: datetime, post_index: int) -> datetime:
        """Calculate optimal posting time based on engagement patterns"""
        # Start with morning time and space posts throughout the day
        base_hour = 9 + (post_index * 3)  # 9 AM, 12 PM, 3 PM, 6 PM, 9 PM
        
        if base_hour > 21:  # Don't post after 9 PM
            base_hour = 9 + (post_index * 2)
        
        post_time = start_date.replace(
            hour=base_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        # Add some randomization to avoid predictable patterns
        post_time += timedelta(minutes=random.randint(-15, 15))
        
        return post_time

    def _estimate_engagement(self, content: ContentPiece) -> dict:
        """Estimate potential engagement based on content characteristics"""
        base_engagement = 0.05  # 5% base engagement rate
        
        # Psychology concepts that typically perform well
        high_engagement_concepts = [
            "emotional regulation", "positive reinforcement", 
            "growth mindset", "empathy development"
        ]
        
        # Magical elements that increase engagement
        engaging_magical_elements = [
            "fairy tale lessons", "dragon courage", "unicorn compassion",
            "enchanted forest wisdom"
        ]
        
        # Adjust engagement based on content characteristics
        if content.psychology_concept in high_engagement_concepts:
            base_engagement += 0.02
        
        if content.magical_element in engaging_magical_elements:
            base_engagement += 0.015
        
        # Video content typically gets higher engagement
        if content.content_type == ContentType.VIDEO:
            base_engagement += 0.03
        
        # Weekend content often performs better
        if content.theme.value in ["story_saturday", "serene_sunday"]:
            base_engagement += 0.01
        
        estimated_reach = random.randint(500, 2000)
        estimated_engagement_count = int(estimated_reach * base_engagement)
        
        return {
            "estimated_reach": estimated_reach,
            "estimated_engagement_rate": round(base_engagement * 100, 2),
            "estimated_likes": int(estimated_engagement_count * 0.7),
            "estimated_comments": int(estimated_engagement_count * 0.2),
            "estimated_saves": int(estimated_engagement_count * 0.1)
        }

    async def _check_rate_limit(self):
        """Check and enforce rate limiting"""
        now = datetime.now()
        
        # Reset counter if more than an hour has passed
        if (now - self.last_request_time).total_seconds() > 3600:
            self.request_count = 0
            self.last_request_time = now
        
        # Check if we're at the limit
        if self.request_count >= self.rate_limit:
            wait_time = 3600 - (now - self.last_request_time).total_seconds()
            if wait_time > 0:
                print(f"Rate limit reached. Waiting {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = datetime.now()
        
        self.request_count += 1

    async def test_connection(self) -> dict:
        """Test Instagram API connection"""
        try:
            await self._check_rate_limit()
            
            # Try to get basic account info
            response = requests.get(
                f"{self.base_url}/{self.business_account_id}",
                params={"access_token": self.access_token}
            )
            
            if response.status_code == 200:
                account_info = response.json()
                return {
                    "status": "connected",
                    "account_name": account_info.get("name", "Unknown"),
                    "username": account_info.get("username", "Unknown"),
                    "followers": account_info.get("followers_count", 0),
                    "media_count": account_info.get("media_count", 0)
                }
            else:
                return {"status": "error", "message": response.text}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_scheduled_posts(self) -> List[dict]:
        """Get list of scheduled posts"""
        try:
            await self._check_rate_limit()
            
            # Get media that's been created but not published
            response = requests.get(
                f"{self.base_url}/{self.business_account_id}/media",
                params={
                    "access_token": self.access_token,
                    "fields": "id,media_type,media_url,thumbnail_url,created_time"
                }
            )
            
            if response.status_code == 200:
                media_list = response.json().get("data", [])
                scheduled_posts = []
                
                for media in media_list:
                    if "published" not in media:
                        scheduled_posts.append({
                            "media_id": media.get("id"),
                            "media_type": media.get("media_type"),
                            "created_time": media.get("created_time"),
                            "status": "scheduled"
                        })
                
                return scheduled_posts
            else:
                return {"error": f"Failed to get scheduled posts: {response.text}"}
                
        except Exception as e:
            print(f"Get scheduled posts error: {e}")
            return {"error": str(e)}
