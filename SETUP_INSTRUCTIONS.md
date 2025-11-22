# Camila Call Taker - Setup Instructions

Complete setup guide for running the FastAPI backend with React frontend and HeyGen avatar.

## Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- HeyGen API account

## Project Structure

```
CallTaker/
├── backend/              # FastAPI backend
│   ├── main.py
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── AvatarPanel.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── src/                  # Original agent code
│   └── agent/
│       ├── complaint_agent.py
│       └── utils.py
└── requirements.txt      # Original requirements
```

## Step 1: Get HeyGen API Key

1. Go to [HeyGen](https://app.heygen.com)
2. Sign up or log in
3. Navigate to Settings → API Keys
4. Create a new API key and copy it

## Step 2: Backend Setup

### Install Backend Dependencies

```bash
cd /Users/javierruiz/Desktop/CallTaker

# Install main dependencies (if not already done)
source venv/bin/activate
pip install -r requirements.txt

# Install backend-specific dependencies
pip install -r backend/requirements.txt
```

### Start the Backend

```bash
# Make sure venv is activated
source venv/bin/activate

# Start FastAPI server
python backend/main.py
```

The backend will run on: **http://localhost:8000**

You can test it by visiting: **http://localhost:8000/docs** (FastAPI interactive docs)

## Step 3: Frontend Setup

### Install Frontend Dependencies

```bash
cd /Users/javierruiz/Desktop/CallTaker/frontend

# Install npm packages
npm install
```

### Configure Environment Variables

Create a `.env` file in the `frontend/` directory:

```bash
cd /Users/javierruiz/Desktop/CallTaker/frontend
cp .env.example .env
```

Edit `.env` and add your HeyGen API key:

```env
VITE_HEYGEN_API_KEY=your_actual_heygen_api_key_here
VITE_API_URL=http://localhost:8000
```

### Start the Frontend

```bash
cd /Users/javierruiz/Desktop/CallTaker/frontend
npm run dev
```

The frontend will run on: **http://localhost:3000**

## Step 4: Access the Application

1. Make sure both backend and frontend are running
2. Open your browser and go to: **http://localhost:3000**
3. Click "Start Avatar" to initialize the HeyGen avatar
4. Start chatting with Camila!

## Running Both Servers (Quick Start)

### Terminal 1 - Backend
```bash
cd /Users/javierruiz/Desktop/CallTaker
source venv/bin/activate
python backend/main.py
```

### Terminal 2 - Frontend
```bash
cd /Users/javierruiz/Desktop/CallTaker/frontend
npm run dev
```

## Features

✅ **FastAPI Backend**: RESTful API wrapping the LangGraph agent
✅ **React Frontend**: Modern, clean UI based on the provided design
✅ **HeyGen Avatar**: Interactive AI avatar on the right panel
✅ **Real-time Chat**: Seamless conversation with Camila
✅ **Session Management**: Maintains conversation state
✅ **Responsive Design**: Clean, modern interface

## API Endpoints

### POST `/api/chat`
Send a message to the agent

**Request:**
```json
{
  "session_id": "uuid",
  "message": "my pipes are leaking"
}
```

**Response:**
```json
{
  "response": "Oh no, I'm really sorry you're dealing with that...",
  "agent_state": {...},
  "session_id": "uuid"
}
```

### POST `/api/session/clear`
Clear a session

### GET `/api/session/{session_id}`
Get session state

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt -r backend/requirements.txt
```

### Frontend Issues

**npm install errors:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**HeyGen avatar not working:**
- Check that your API key is correct in `.env`
- Ensure the `.env` file is in the `frontend/` directory
- Check browser console for errors
- Verify your HeyGen account has credits

**CORS errors:**
- Make sure backend is running on port 8000
- Check that frontend proxy is configured in `vite.config.js`

## HeyGen Avatar Options

You can customize the avatar in `frontend/src/components/AvatarPanel.jsx`:

```javascript
await avatar.createStartAvatar({
  quality: AvatarQuality.High, // Low, Medium, High
  avatarName: 'Anna_public_3_20240108', // Change to any available avatar
  voice: {
    voiceId: 'af8605ddecd64a2fa5bb949c641cbe8c' // Change voice
  },
  language: 'en', // Language
})
```

Popular avatar names:
- `Anna_public_3_20240108` (Female, professional)
- `Josh_lite3_20230714` (Male, friendly)
- `Angela_public_3_20240108` (Female, warm)

## Production Deployment

### Backend
```bash
# Use production ASGI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
cd frontend
npm run build
# Deploy the dist/ folder to your hosting service
```

## Support

For issues with:
- **Agent logic**: Check `src/agent/complaint_agent.py`
- **Backend API**: Check `backend/main.py`
- **Frontend UI**: Check `frontend/src/App.jsx`
- **Avatar**: Check `frontend/src/components/AvatarPanel.jsx`

## Notes

- The avatar will speak the AI's responses automatically
- First-time avatar initialization may take 10-15 seconds
- Make sure your HeyGen account has sufficient credits
- The application requires an internet connection for the HeyGen avatar

