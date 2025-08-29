import openai
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from app.config import settings
import asyncio

class ContentType(Enum):
    CAROUSEL = "carousel"
    VIDEO = "video"
    STORY = "story"

class DayTheme(Enum):
    MAGICAL_MONDAY = "magical_monday_wisdom"
    TINY_TALES_TUESDAY = "tiny_tales_tuesday"
    WONDER_WEDNESDAY = "wonder_wednesday"
    THOUGHTFUL_THURSDAY = "thoughtful_thursday"
    FANTASY_FRIDAY = "fantasy_friday"
    STORY_SATURDAY = "story_saturday"
    SERENE_SUNDAY = "serene_sunday"

@dataclass
class ContentPiece:
    theme: DayTheme
    content_type: ContentType
    title: str
    slides: List[str]
    caption: str
    hashtags: List[str]
    visual_prompts: List[str]
    psychology_concept: str
    magical_element: str
    target_age: str
    engagement_hooks: List[str]
    created_at: datetime

class MagicalParentingContentEngine:
    def __init__(self):
        """Initialize the content generation engine"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        
        # Psychology concepts bank
        self.psychology_concepts = [
            "attachment theory", "positive reinforcement", "emotional regulation",
            "growth mindset", "active listening", "boundary setting",
            "emotional intelligence", "resilience building", "empathy development",
            "self-esteem nurturing", "stress management", "mindful parenting",
            "play therapy", "cognitive development", "social learning theory"
        ]
        
        # Magical elements bank
        self.magical_elements = [
            "enchanted forest wisdom", "fairy tale lessons", "dragon courage",
            "unicorn compassion", "wizard patience", "magic mirror reflection",
            "crystal ball insight", "phoenix resilience", "owl wisdom",
            "butterfly transformation", "star guidance", "moon serenity",
            "magic carpet adventures", "talking animals", "enchanted objects"
        ]
        
        # Trending parenting topics (would be fetched via API in production)
        self.trending_topics = [
            "toddler tantrums", "bedtime struggles", "sibling rivalry",
            "screen time balance", "picky eating", "homework battles",
            "social anxiety in kids", "building confidence", "morning routines",
            "emotional meltdowns", "transition difficulties", "friendship issues",
            "back to school anxiety", "holiday stress", "family traditions"
        ]

    def get_daily_theme(self) -> DayTheme:
        """Get theme based on current day of week"""
        weekday = datetime.now().weekday()
        themes = list(DayTheme)
        return themes[weekday]

    async def generate_carousel_content(self, 
                                     theme: DayTheme, 
                                     topic: Optional[str] = None) -> ContentPiece:
        """Generate a 5-slide carousel with magical parenting wisdom"""
        
        if not topic:
            topic = random.choice(self.trending_topics)
            
        psychology_concept = random.choice(self.psychology_concepts)
        magical_element = random.choice(self.magical_elements)
        
        # AI prompt for content generation
        content_prompt = f"""
        Create a 5-slide Instagram carousel about "{topic}" for parents.
        
        Theme: {theme.value}
        Psychology Concept: {psychology_concept}
        Magical Element: {magical_element}
        Target: Parents with children ages 3-10
        
        Requirements:
        - Slide 1: Hook (question or surprising fact)
        - Slides 2-4: Practical tips with magical storytelling
        - Slide 5: Call-to-action + teaser for upcoming AI story bot
        
        Tone: Warm, supportive, magical but practical
        Each slide should be 1-2 sentences maximum
        
        Return as JSON with: title, slides (array of 5), psychology_explanation, magical_narrative
        """
        
        try:
            response = await self._call_openai(content_prompt)
            content_data = json.loads(response)
            
            # Generate visual prompts
            visual_prompts = await self._generate_visual_prompts(content_data, magical_element)
            
            # Generate caption and hashtags
            caption = await self._generate_caption(content_data, topic, theme)
            hashtags = await self._generate_hashtags(topic, theme)
            
            return ContentPiece(
                theme=theme,
                content_type=ContentType.CAROUSEL,
                title=content_data.get("title", ""),
                slides=content_data.get("slides", []),
                caption=caption,
                hashtags=hashtags,
                visual_prompts=visual_prompts,
                psychology_concept=psychology_concept,
                magical_element=magical_element,
                target_age="3-10",
                engagement_hooks=self._extract_hooks(content_data),
                created_at=datetime.now()
            )
            
        except Exception as e:
            print(f"Error generating carousel: {e}")
            return self._generate_fallback_content(theme, topic)

    async def generate_video_content(self, 
                                   theme: DayTheme, 
                                   topic: Optional[str] = None) -> ContentPiece:
        """Generate video script with magical storytelling"""
        
        if not topic:
            topic = random.choice(self.trending_topics)
            
        psychology_concept = random.choice(self.psychology_concepts)
        magical_element = random.choice(self.magical_elements)
        
        video_prompt = f"""
        Create a 60-90 second Instagram video script about "{topic}".
        
        Theme: {theme.value}
        Psychology: {psychology_concept}
        Magic: {magical_element}
        
        Structure:
        - Hook (0-5 seconds): Attention-grabbing question
        - Story Setup (5-25 seconds): Magical scenario introduction
        - Teaching Moment (25-60 seconds): Psychology tip within story
        - Call-to-Action (60-90 seconds): Engagement + bot teaser
        
        Include: scene descriptions, voiceover script, text overlays
        
        Return as JSON with: title, script_sections, scene_descriptions, text_overlays, background_music_mood
        """
        
        try:
            response = await self._call_openai(video_prompt)
            video_data = json.loads(response)
            
            caption = await self._generate_video_caption(video_data, topic)
            hashtags = await self._generate_hashtags(topic, theme, is_video=True)
            
            return ContentPiece(
                theme=theme,
                content_type=ContentType.VIDEO,
                title=video_data.get("title", ""),
                slides=video_data.get("script_sections", []),
                caption=caption,
                hashtags=hashtags,
                visual_prompts=video_data.get("scene_descriptions", []),
                psychology_concept=psychology_concept,
                magical_element=magical_element,
                target_age="3-10",
                engagement_hooks=[video_data.get("hook", "")],
                created_at=datetime.now()
            )
            
        except Exception as e:
            print(f"Error generating video: {e}")
            return self._generate_fallback_video(theme, topic)

    async def _call_openai(self, prompt: str, model: str = None) -> str:
        """Make API call to OpenAI with error handling"""
        if not model:
            model = settings.openai_model
            
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a magical parenting content creator who combines child psychology with storytelling. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise

    async def _generate_visual_prompts(self, content_data: dict, magical_element: str) -> List[str]:
        """Generate Midjourney prompts for carousel images"""
        visual_prompt = f"""
        Create 5 Midjourney prompts for Instagram carousel about "{content_data.get('title', '')}".
        
        Style: Whimsical children's book illustration, soft pastels, magical realism
        Elements: {magical_element}
        
        Each prompt should be optimized for Instagram carousel (1080x1080px equivalent)
        Include: magical creatures, parent-child interactions, cozy settings
        
        Return as JSON array of prompts.
        """
        
        try:
            response = await self._call_openai(visual_prompt)
            prompts_data = json.loads(response)
            return prompts_data.get("prompts", [])
        except:
            # Fallback prompts
            return [
                f"Whimsical illustration of {magical_element}, children's book style",
                f"Magical parent-child moment, soft colors, cozy setting",
                f"Enchanted forest scene with family, warm lighting",
                f"Fairy tale inspired parenting scene, gentle magic",
                f"Magical family bonding moment, dreamy atmosphere"
            ]

    async def _generate_caption(self, content_data: dict, topic: str, theme: DayTheme) -> str:
        """Generate engaging Instagram caption"""
        caption_prompt = f"""
        Write an Instagram caption for a carousel about "{topic}".
        
        Content Summary: {content_data.get('title', '')}
        Theme: {theme.value}
        
        Requirements:
        - Start with hook/question
        - Include story element from carousel
        - Add psychology tip
        - End with CTA about upcoming AI story bot
        - Warm, supportive tone
        - 150-200 words
        - Include emoji sparingly
        
        Return just the caption text.
        """
        
        try:
            return await self._call_openai(caption_prompt)
        except:
            return f"✨ Magical parenting wisdom for {topic}! Every challenge is an opportunity for growth. What's your experience with this? Share below! 👇 #MagicalParenting #ParentingTips"

    async def _generate_hashtags(self, topic: str, theme: DayTheme, is_video: bool = False) -> List[str]:
        """Generate relevant hashtags for the post"""
        base_hashtags = [
            "#MagicalParenting", "#ParentingWisdom", "#ParentingTips",
            "#ChildPsychology", "#ParentingSupport", "#BedtimeStories",
            "#ParentingCommunity", "#RaisingKids", "#ParentingAdvice"
        ]
        
        # Add theme-specific hashtags
        theme_hashtags = {
            DayTheme.MAGICAL_MONDAY: ["#MondayMotivation", "#ParentingMindset"],
            DayTheme.TINY_TALES_TUESDAY: ["#TuesdayTales", "#Storytelling"],
            DayTheme.WONDER_WEDNESDAY: ["#WonderWednesday", "#ParentingQuestions"],
            DayTheme.THOUGHTFUL_THURSDAY: ["#ThoughtfulParenting", "#DeepThoughts"],
            DayTheme.FANTASY_FRIDAY: ["#FantasyFriday", "#WeekendFun"],
            DayTheme.STORY_SATURDAY: ["#StorySaturday", "#FamilyTime"],
            DayTheme.SERENE_SUNDAY: ["#SereneParenting", "#SelfCare"]
        }
        
        topic_hashtags = [f"#{topic.replace(' ', '').replace('_', '')}", 
                         f"#{topic.replace(' ', 'Tips').replace('_', 'Tips')}"]
        
        if is_video:
            base_hashtags.extend(["#ParentingVideo", "#InstagramVideo", "#ParentingReel"])
            
        all_hashtags = base_hashtags + theme_hashtags.get(theme, []) + topic_hashtags
        return all_hashtags[:25]  # Instagram limit

    async def _generate_video_caption(self, video_data: dict, topic: str) -> str:
        """Generate caption specifically for video content"""
        caption_prompt = f"""
        Write an Instagram video caption for "{topic}".
        
        Video Summary: {video_data.get('title', '')}
        
        Requirements:
        - Start with hook that matches video opening
        - Mention the magical story element
        - Include the psychology tip
        - Encourage interaction (comments/shares)
        - Tease upcoming AI storytelling bot
        - 100-150 words
        - Video-optimized format
        
        Return just the caption text.
        """
        
        try:
            return await self._call_openai(caption_prompt)
        except:
            return f"🎬 Quick magical parenting tip for {topic}! Every challenge is a story waiting to be told. What's your experience? Comment below! 👇 #ParentingVideo #MagicalParenting"

    def _extract_hooks(self, content_data: dict) -> List[str]:
        """Extract engagement hooks from generated content"""
        hooks = []
        if "slides" in content_data and content_data["slides"]:
            hooks.append(content_data["slides"][0])  # First slide is usually the hook
        return hooks

    def _generate_fallback_content(self, theme: DayTheme, topic: str) -> ContentPiece:
        """Generate basic fallback content if AI fails"""
        return ContentPiece(
            theme=theme,
            content_type=ContentType.CAROUSEL,
            title=f"Quick Tips for {topic}",
            slides=[
                f"Struggling with {topic}?",
                "Take a deep breath, you've got this!",
                "Every challenge is a growth opportunity",
                "Small steps lead to big changes",
                "Share your experience below! 👇"
            ],
            caption=f"Quick thoughts on {topic}. What works for your family?",
            hashtags=["#ParentingTips", "#ParentingSupport", "#YouGotThis"],
            visual_prompts=["Simple, calming illustration"],
            psychology_concept="general support",
            magical_element="gentle encouragement",
            target_age="all",
            engagement_hooks=["Quick question for you..."],
            created_at=datetime.now()
        )

    def _generate_fallback_video(self, theme: DayTheme, topic: str) -> ContentPiece:
        """Generate basic fallback video content if AI fails"""
        return ContentPiece(
            theme=theme,
            content_type=ContentType.VIDEO,
            title=f"Quick Video: {topic}",
            slides=[
                "Quick tip coming your way!",
                f"When dealing with {topic}...",
                "Remember: Progress, not perfection",
                "What would you add? Comment below!"
            ],
            caption=f"Quick thoughts on {topic}. What's your experience?",
            hashtags=["#ParentingVideo", "#QuickTips", "#ParentingSupport"],
            visual_prompts=["Simple talking head with text overlay"],
            psychology_concept="general support",
            magical_element="encouraging tone",
            target_age="all",
            engagement_hooks=["Quick question..."],
            created_at=datetime.now()
        )

    async def generate_weekly_content(self) -> Dict[str, List[ContentPiece]]:
        """Generate a full week's worth of content"""
        weekly_content = {}
        
        for day_num, theme in enumerate(DayTheme):
            date = datetime.now() + timedelta(days=day_num)
            
            # Generate carousel for each day
            carousel = await self.generate_carousel_content(theme)
            
            # Generate video content 3x per week (Mon, Wed, Fri)
            content_pieces = [carousel]
            if day_num in [0, 2, 4]:  # Monday, Wednesday, Friday
                video = await self.generate_video_content(theme)
                content_pieces.append(video)
            
            weekly_content[date.strftime("%Y-%m-%d")] = content_pieces
            
        return weekly_content

    async def generate_bot_teaser_campaign(self) -> List[ContentPiece]:
        """Generate content campaign for upcoming bot launch"""
        campaign_content = []
        
        teaser_topics = [
            "Behind the scenes: Building magical stories for your kids",
            "What if bedtime stories adapted to your child's choices?",
            "The psychology behind interactive storytelling",
            "Sneak peek: AI that creates personalized fairy tales"
        ]
        
        for topic in teaser_topics:
            content = await self.generate_carousel_content(
                DayTheme.STORY_SATURDAY, 
                topic
            )
            campaign_content.append(content)
            
        return campaign_content
