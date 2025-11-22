# 🚀 Quick Start Guide

Get Camila Call Taker running in 3 steps!

## Prerequisites

- Python 3.12+ installed
- Node.js 18+ installed
- HeyGen API key ([Get one here](https://app.heygen.com/settings))

## Step 1: Get Your HeyGen API Key

1. Visit [HeyGen Settings](https://app.heygen.com/settings)
2. Go to API Keys section
3. Create a new API key
4. Copy it (you'll need it in Step 3)

## Step 2: Start the Backend

Open a terminal and run:

```bash
cd /Users/javierruiz/Desktop/CallTaker
./start_backend.sh
```

✅ Backend will be running on **http://localhost:8000**

## Step 3: Configure and Start the Frontend

### Add Your API Key

Create the `.env` file:

```bash
cd /Users/javierruiz/Desktop/CallTaker/frontend
echo "VITE_HEYGEN_API_KEY=your_api_key_here" > .env
echo "VITE_API_URL=http://localhost:8000" >> .env
```

Replace `your_api_key_here` with your actual HeyGen API key.

### Start the Frontend

Open a **new terminal** and run:

```bash
cd /Users/javierruiz/Desktop/CallTaker
./start_frontend.sh
```

✅ Frontend will be running on **http://localhost:3000**

## Step 4: Use the App

1. Open your browser to **http://localhost:3000**
2. Click **"Start Avatar"** button to initialize the HeyGen avatar
3. Start chatting with Camila!

---

## What You'll See

- **Left side**: Clean chat interface inspired by modern AI assistants
- **Right side**: Interactive HeyGen avatar that speaks responses
- **Real-time**: Avatar lip-syncs to the AI's voice responses

## Example Conversation

```
You: "hello my pipes are leaking"
Camila: "Oh no, I'm really sorry you're dealing with that. That must be 
         frustrating! Let's get this sorted right away. I'll raise a report 
         to our technical team. I just need a couple of details first. Can 
         we start with your phone number, please?"

You: "050555555"
Camila: "Thank you. Let me check... yes, I see an address linked to this 
         number..."
```

---

## Stopping the Servers

Press `Ctrl+C` in each terminal window to stop the servers.

---

## Troubleshooting

### "Port already in use"
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

### "Module not found" errors
```bash
# Backend
source venv/bin/activate
pip install -r requirements.txt -r backend/requirements.txt

# Frontend
cd frontend
npm install
```

### Avatar not loading
- Check your HeyGen API key in `frontend/.env`
- Ensure you have credits in your HeyGen account
- Check browser console (F12) for errors

---

## Need More Help?

See the complete [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md) for detailed information.

---

**That's it! You're ready to use Camila Call Taker! 🎉**

