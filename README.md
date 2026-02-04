# Gmail AI Assistant

A production-ready AI-powered Gmail automation assistant built with Next.js, FastAPI, and Claude/OpenAI. This application allows users to read, summarize, reply to, and manage their Gmail emails through natural language commands.

## 🌐 Live URLs

- **Frontend**: `https://constructure-ai-assistant.vercel.app`
- **Backend**: `https://constructure-ai-backend.onrender.com`

## ✨ Features

### Core Features
- ✅ **Google OAuth2 Authentication** with Gmail scopes
- ✅ **Read Emails** with AI-generated summaries
- ✅ **Generate Smart Replies** using LLM
- ✅ **Delete Emails** with confirmation
- ✅ **Natural Language Interface** for all commands

### Bonus Features
- ✅ **Intent Parsing** - Understands natural language commands
- ✅ **Email Categorization** - Automatically categorizes emails (Work, Personal, Promotions, etc.)
- ✅ **Daily Digest** - Generate summarized email digests
- ✅ **Backend Logging** - Comprehensive logging for debugging
- ✅ **Pytest Tests** - Core logic testing

## 🏗️ Tech Stack

### Frontend
- **Next.js 14** (App Router)
- **React 18**
- **Tailwind CSS**
- **Axios** for API calls
- **js-cookie** for token management

### Backend
- **FastAPI** (Python)
- **Google Gmail API**
- **Google OAuth2**
- **Anthropic Claude / OpenAI GPT**
- **JWT Authentication**
- **Pytest** for testing

## 📁 Project Structure

```
gmail-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── emails.py       # Email management endpoints
│   │   │   └── chat.py         # Chat interface endpoints
│   │   ├── core/
│   │   │   ├── config.py       # Configuration settings
│   │   │   └── security.py     # JWT utilities
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models
│   │   ├── services/
│   │   │   ├── auth_service.py # OAuth service
│   │   │   ├── gmail_service.py # Gmail API service
│   │   │   └── ai_service.py   # AI/LLM service
│   │   └── main.py             # FastAPI app
│   ├── tests/
│   │   ├── test_auth.py
│   │   └── test_ai_service.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.js             # Home/Login page
│   │   ├── layout.js           # Root layout
│   │   ├── globals.css         # Global styles
│   │   ├── auth/
│   │   │   └── callback/
│   │   │       └── page.js     # OAuth callback
│   │   └── dashboard/
│   │       └── page.js         # Main dashboard
│   ├── components/
│   │   ├── ChatMessage.js      # Chat message component
│   │   └── EmailCard.js        # Email card component
│   ├── lib/
│   │   ├── api.js              # API client
│   │   └── auth.js             # Auth context
│   ├── package.json
│   └── .env.example
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud Console account
- Anthropic API key OR OpenAI API key

### Step 1: Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Gmail API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Web application"
   - Name: "Gmail AI Assistant"
   - Authorized redirect URIs:
     - `https://constructure-ai-backend.onrender.com/api/auth/callback`
     - `http://localhost:8000/api/auth/callback` (for local dev)
   - Save Client ID and Client Secret
5. Configure OAuth consent screen:
   - User Type: "External"
   - App name: "Gmail AI Assistant"
   - Add scopes:
     - `gmail.readonly`
     - `gmail.send`
     - `gmail.modify`
     - `userinfo.email`
     - `userinfo.profile`
6. **Add test users**:
   - Go to "OAuth consent screen"
   - Under "Test users", click "Add users"
   - Add your Gmail address (e.g., `test@gmail.com`)
   - Important: While in testing mode, only added test users can authenticate!

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Configure .env:**
```env
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# From Google Cloud Console
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/callback

# Generate a secure random string
SECRET_KEY=your-super-secret-jwt-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Choose AI provider
AI_PROVIDER=anthropic  # or openai

# Get from https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-api03-your-key

# OR get from https://platform.openai.com
OPENAI_API_KEY=sk-your-key

ENVIRONMENT=development
```

**Run backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### Step 3: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

**Configure .env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000
```

**Run frontend:**
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Step 4: Testing

**Backend Tests:**
```bash
cd backend
pytest tests/ -v
```

**Manual Testing:**
1. Open `http://localhost:3000`
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Try commands:
   - "Show me my latest emails"
   - "Reply to email 1"
   - "Delete email 2"
   - "Give me a daily digest"

## 🌐 Production Deployment

### Deploy Backend (Render)

1. Create account on [Render](https://render.com)
2. New > Web Service
3. Connect GitHub repository
4. Configure:
   - **Name**: constructure-ai-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as .env)
6. Update `BACKEND_URL` to your Render URL
7. Update Google OAuth redirect URI to include Render URL

### Deploy Frontend (Vercel)

1. Create account on [Vercel](https://vercel.com)
2. Import GitHub repository
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: frontend
4. Add environment variables:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
   - `NEXT_PUBLIC_FRONTEND_URL`: Your Vercel URL
5. Deploy!

**Important:** After deployment, update Google OAuth redirect URIs with production URLs.

## 📖 Usage Guide

### Natural Language Commands

The assistant understands natural language. Try these commands:

**Reading Emails:**
- "Show me my emails"
- "Get my latest 10 emails"
- "List my inbox"

**Generating Replies:**
- "Reply to email 2"
- "Generate a reply for the first email"

**Deleting Emails:**
- "Delete email 3"
- "Delete the latest email from Amazon"
- "Remove the promotion email"

**Searching:**
- "Find emails from John"
- "Search for invoice emails"

**Other Commands:**
- "Give me a daily digest"
- "Categorize my emails"
- "Help" - Show available commands

### Chat Interface

1. **Login**: Click "Sign in with Google"
2. **Grant Permissions**: Allow Gmail access
3. **Dashboard**: Start chatting with the AI assistant
4. **Email Actions**: 
   - Click "Reply" on email cards to generate responses
   - Click "Delete" to remove emails
   - View AI summaries in the sidebar

## 🔒 Security

- **JWT Tokens**: Secure session management with 30-day expiry
- **OAuth2**: Industry-standard Google authentication
- **Token Refresh**: Automatic token refresh handling
- **CORS**: Configured for specific origins
- **HTTPS**: Required in production

## ⚠️ Known Limitations

1. **OAuth Testing Mode**: 
   - App must be verified by Google for public use
   - Currently limited to test users
   - For production, submit for Google verification

2. **Rate Limits**:
   - Gmail API: 250 quota units per user per second
   - Anthropic API: Depends on your plan
   - OpenAI API: Depends on your plan

3. **Token Expiry**:
   - Access tokens expire after 1 hour
   - Refresh tokens used to obtain new access tokens
   - Implement token refresh logic for long-running sessions

4. **Email Parsing**:
   - HTML emails converted to text (may lose formatting)
   - Large emails truncated for AI processing
   - Attachments not currently processed

5. **AI Limitations**:
   - Context window limits (varies by model)
   - Response time depends on email length
   - May occasionally misunderstand complex commands

## 🐛 Troubleshooting

### "OAuth error: invalid_client"
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
- Verify redirect URI matches exactly (including http/https)

### "401 Unauthorized"
- Token expired - try logging in again
- Check JWT SECRET_KEY is same in both environments

### "Gmail API errors"
- Ensure Gmail API is enabled in Google Console
- Check OAuth scopes include gmail.* permissions
- Verify user is added as test user

### "AI not responding"
- Check ANTHROPIC_API_KEY or OPENAI_API_KEY
- Verify API_PROVIDER is set correctly
- Check API credits/quota

### Backend won't start
- Ensure all environment variables are set
- Check Python version (3.9+)
- Verify all dependencies installed

### Frontend build errors
- Clear .next folder: `rm -rf .next`
- Delete node_modules: `rm -rf node_modules`
- Reinstall: `npm install`

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/test_ai_service.py -v
```

### Test Coverage
- Authentication flow
- AI summarization
- Intent parsing
- Email categorization

## 📝 API Endpoints

### Authentication
- `GET /api/auth/login` - Get OAuth URL
- `GET /api/auth/callback` - OAuth callback
- `GET /api/auth/user` - Get current user
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh token

### Emails
- `GET /api/emails/list` - List emails with summaries
- `GET /api/emails/{id}` - Get email details
- `POST /api/emails/generate-reply` - Generate reply
- `POST /api/emails/send-reply` - Send reply
- `DELETE /api/emails/{id}` - Delete email
- `GET /api/emails/search/{query}` - Search emails
- `POST /api/emails/categorize` - Categorize emails
- `GET /api/emails/digest/daily` - Daily digest

### Chat
- `POST /api/chat/message` - Process chat message
- `POST /api/chat/confirm-delete` - Confirm deletion

## 🎯 Future Enhancements

- [ ] Email scheduling
- [ ] Attachment handling
- [ ] Calendar integration
- [ ] Multi-language support
- [ ] Voice commands
- [ ] Mobile app
- [ ] Email templates
- [ ] Advanced filtering
- [ ] Analytics dashboard

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📞 Support

For issues or questions:
- Create GitHub issue
- Check troubleshooting section
- Review API documentation

---

**Built with ❤️ using Next.js, FastAPI, and AI**
