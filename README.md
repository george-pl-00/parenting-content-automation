# 🎭 Magical Parenting Content Automation

Automated Instagram content generation for your magical parenting blog, combining child psychology with enchanting storytelling. Built with FastAPI, OpenAI, and Instagram Business API.

## ✨ Features

- **AI-Powered Content Generation**: Creates engaging carousels and video scripts using OpenAI GPT-4
- **Magical + Psychology Fusion**: Combines child psychology concepts with fairy tale elements
- **Daily Theme System**: 7 unique themes for each day of the week
- **Instagram Integration**: Automated posting with optimal timing and engagement optimization
- **Background Processing**: Celery workers for scalable content generation
- **Heroku Deployment**: Production-ready with automated CI/CD
- **Future-Ready**: Designed for upcoming Telegram bot integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HEROKU DEPLOYMENT                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │   Web Server    │  │  Background     │  │   Database    │ │
│  │   (FastAPI)     │  │   Workers       │  │  (PostgreSQL) │ │
│  │                 │  │  (Celery)       │  │               │ │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
└─────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    Content Pipeline     │
                    └──────────┬─────────────┘
                                │
    ┌───────────────┬───────────▼────────────┬─────────────────┐
    │               │                        │                 │
┌───▼────┐  ┌──────▼──────┐  ┌──────────▼────────┐  ┌────────▼─┐
│Content │  │   Visual    │  │   Publishing      │  │Analytics │
│Engine  │  │  Generator  │  │   Manager         │  │ Tracker  │
└────────┘  └─────────────┘  └───────────────────┘  └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Instagram Business Account with API access
- Heroku account (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/parenting-content-automation.git
   cd parenting-content-automation
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run with Docker Compose**
   ```bash
   docker-compose up
   ```

6. **Or run locally**
   ```bash
   uvicorn app.main:app --reload
   ```

### Environment Variables

Create a `.env` file with:

```env
# OpenAI
OPENAI_API_KEY=sk-your-openai-key

# Instagram Business API
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-business-account-id

# Database (for production)
DATABASE_URL=postgresql://user:password@host:port/db

# Redis (for production)
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
```

## 📱 Content Generation

### Daily Themes

- **Monday**: Magical Monday Wisdom
- **Tuesday**: Tiny Tales Tuesday
- **Wednesday**: Wonder Wednesday
- **Thursday**: Thoughtful Thursday
- **Friday**: Fantasy Friday
- **Saturday**: Story Saturday
- **Sunday**: Serene Sunday

### Content Types

- **Carousels**: 5-slide Instagram posts with psychology tips
- **Videos**: 60-90 second scripts with magical storytelling
- **Stories**: Interactive content for future bot integration

### Example API Usage

```python
import requests

# Generate today's content
response = requests.post("http://localhost:8000/generate/daily")
content = response.json()

# Generate custom content
response = requests.post("http://localhost:8000/generate/custom", 
    params={"theme": "magical_monday_wisdom", "topic": "toddler tantrums"})
custom_content = response.json()

# Generate weekly batch
response = requests.post("http://localhost:8000/generate/weekly")
weekly_content = response.json()
```

## 🚀 Deployment

### Heroku Deployment

1. **Create Heroku apps**
   ```bash
   heroku create parenting-automation-prod
   heroku create parenting-automation-staging
   ```

2. **Add PostgreSQL and Redis**
   ```bash
   heroku addons:create heroku-postgresql:mini --app parenting-automation-prod
   heroku addons:create heroku-redis:mini --app parenting-automation-prod
   ```

3. **Set environment variables**
   ```bash
   heroku config:set OPENAI_API_KEY=your-key --app parenting-automation-prod
   heroku config:set INSTAGRAM_ACCESS_TOKEN=your-token --app parenting-automation-prod
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### GitHub Actions Setup

1. **Add repository secrets**:
   - `HEROKU_API_KEY`
   - `HEROKU_APP_NAME_PROD`
   - `HEROKU_APP_NAME_STAGING`
   - `HEROKU_EMAIL`
   - `SLACK_WEBHOOK` (optional)

2. **Push to trigger deployment**:
   - `main` branch → Production
   - `staging` branch → Staging

## 🔧 API Endpoints

### Content Generation
- `POST /generate/daily` - Generate today's content
- `POST /generate/weekly` - Generate weekly batch
- `POST /generate/custom` - Custom content generation

### Instagram Publishing
- `POST /instagram/publish/carousel` - Publish carousel
- `POST /instagram/publish/video` - Publish video
- `GET /instagram/insights` - Account insights
- `GET /instagram/scheduled` - Scheduled posts

### Analytics & Health
- `GET /health` - System health check
- `GET /analytics/content/{id}` - Content performance
- `POST /test/generate-content` - Test endpoint

## 📊 Background Tasks

### Celery Workers

Start background workers:

```bash
# Start worker
celery -A app.tasks.celery_app worker --loglevel=info

# Start scheduler
celery -A app.tasks.celery_app beat --loglevel=info
```

### Scheduled Tasks

- **Hourly**: Daily content generation
- **Every 30 minutes**: Engagement monitoring
- **Weekly**: Weekly content batch generation
- **Daily**: Content cleanup

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_content_engine.py -v
```

## 🔮 Future Features

### Telegram Bot Integration
- Interactive storytelling based on user choices
- Personalized bedtime stories
- Cross-platform content sharing

### Advanced Analytics
- Content performance prediction
- Audience behavior analysis
- A/B testing for content optimization

### Visual Generation
- Midjourney API integration
- Canva template automation
- Video creation with AI

## 📁 Project Structure

```
parenting-automation/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── database.py             # Database setup
│   └── models/
│       ├── content.py          # Data models
│       └── __init__.py
├── services/
│   ├── content_engine.py       # AI content generation
│   └── instagram_publisher.py  # Instagram API
├── tasks/
│   ├── celery_app.py           # Celery configuration
│   └── daily_content.py        # Background tasks
├── tests/                      # Test suite
├── .github/workflows/          # CI/CD
├── docker-compose.yml          # Local development
├── Procfile                    # Heroku deployment
└── requirements.txt            # Dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API Docs](https://your-app.herokuapp.com/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/parenting-content-automation/issues)
- **Email**: your-email@example.com

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Instagram Business API
- FastAPI community
- Heroku platform

---

**Made with ✨ and 🧠 for magical parenting everywhere!**
