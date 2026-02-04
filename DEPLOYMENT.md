# Deployment Guide

## Quick Deploy Checklist

### 1. Get API Keys
- [ ] Google OAuth credentials from Google Cloud Console
- [ ] Anthropic API key from https://console.anthropic.com OR
- [ ] OpenAI API key from https://platform.openai.com

### 2. Backend Deployment (Render)

**Steps:**
1. Sign up at https://render.com
2. Click "New +" > "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: `constructure-ai-backend`
   - **Region**: Select closest to you
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables:
```
BACKEND_URL=https://constructure-ai-backend.onrender.com
FRONTEND_URL=https://constructure-ai-assistant.vercel.app
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://constructure-ai-backend.onrender.com/api/auth/callback
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
ENVIRONMENT=production
```

6. Click "Create Web Service"
7. Wait for deployment (5-10 minutes)
8. Note your Render URL

### 3. Frontend Deployment (Vercel)

**Steps:**
1. Sign up at https://vercel.com
2. Click "Add New" > "Project"
3. Import your GitHub repo
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

5. Add Environment Variables:
```
NEXT_PUBLIC_API_URL=https://constructure-ai-backend.onrender.com
NEXT_PUBLIC_FRONTEND_URL=https://constructure-ai-assistant.vercel.app
```

6. Click "Deploy"
7. Wait for deployment (2-5 minutes)
8. Note your Vercel URL

### 4. Update Google OAuth

1. Go to Google Cloud Console
2. Navigate to "APIs & Services" > "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add Authorized Redirect URIs:
   - `https://your-render-url.onrender.com/api/auth/callback`
   - `https://your-vercel-url.vercel.app/auth/callback`
5. Save changes

### 5. Test Production

1. Visit your Vercel URL
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Test email commands

## Environment Variables Explained

### Backend
- `BACKEND_URL`: Your Render URL
- `FRONTEND_URL`: Your Vercel URL
- `GOOGLE_CLIENT_ID`: From Google Cloud Console
- `GOOGLE_CLIENT_SECRET`: From Google Cloud Console
- `GOOGLE_REDIRECT_URI`: Backend callback URL
- `SECRET_KEY`: Random 32+ character string
- `AI_PROVIDER`: "anthropic" or "openai"
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)

### Frontend
- `NEXT_PUBLIC_API_URL`: Your backend URL
- `NEXT_PUBLIC_FRONTEND_URL`: Your frontend URL

## Custom Domain Setup

### Backend (Render)
1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain (e.g., api.yourdomain.com)
4. Update DNS records as instructed
5. Update `BACKEND_URL` environment variable

### Frontend (Vercel)
1. Go to project settings
2. Click "Domains"
3. Add your domain (e.g., app.yourdomain.com)
4. Update DNS records as instructed
5. Update `NEXT_PUBLIC_FRONTEND_URL` environment variable

## Monitoring

### Backend Health Check
- Endpoint: `https://your-backend-url.onrender.com/health`
- Expected: `{"status": "healthy"}`

### Frontend
- Vercel provides automatic monitoring
- Check dashboard for build logs and errors

## Troubleshooting Deployment

### Backend Issues
- **Build fails**: Check requirements.txt syntax
- **Start fails**: Verify uvicorn command
- **503 errors**: Check logs in Render dashboard
- **OAuth fails**: Verify redirect URIs match exactly

### Frontend Issues
- **Build fails**: Check package.json syntax
- **Blank page**: Check browser console for errors
- **API errors**: Verify environment variables
- **OAuth redirect fails**: Check callback URLs

## Scaling

### Backend
- Render: Upgrade to paid plan for better performance
- Consider: AWS Lambda, Google Cloud Run, or Railway

### Frontend
- Vercel automatically scales
- Consider: CDN configuration for global users

## Cost Estimates

### Free Tier
- Render: 750 hours/month free
- Vercel: Unlimited deployments
- Google OAuth: Free
- Anthropic/OpenAI: Pay per use

### Production
- Render: $7-25/month
- Vercel: $20/month (Pro)
- API costs: Variable based on usage

## Security Checklist

- [ ] Enable HTTPS (automatic on Render/Vercel)
- [ ] Set strong SECRET_KEY (32+ characters)
- [ ] Add environment variables (never commit .env)
- [ ] Configure CORS properly
- [ ] Use OAuth test users initially
- [ ] Submit for Google verification before public launch
- [ ] Monitor API usage and costs
- [ ] Set up error tracking (Sentry, LogRocket)
- [ ] Regular security updates

## Next Steps After Deployment

1. **Add Test Users** (Google OAuth)
   - Console > OAuth Consent > Test Users
   - Add gmail addresses

2. **Monitor Usage**
   - Backend logs in Render
   - Frontend logs in Vercel
   - API usage in Anthropic/OpenAI dashboard

3. **Get Google Verified** (for public use)
   - Required for >100 users
   - Submit app for review
   - Process takes 2-4 weeks

4. **Set Up Alerts**
   - Error monitoring
   - Usage alerts
   - Cost alerts

## Support Resources

- **Render**: https://render.com/docs
- **Vercel**: https://vercel.com/docs
- **Google OAuth**: https://developers.google.com/identity
- **Anthropic**: https://docs.anthropic.com
- **OpenAI**: https://platform.openai.com/docs

---

**Deployment takes ~20 minutes total. Good luck! 🚀**
