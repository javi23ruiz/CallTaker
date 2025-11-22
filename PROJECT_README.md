# 🤖 Camila Call Taker

An AI-powered customer service assistant for handling technical complaints and issues. Built with LangGraph, FastAPI, React, and HeyGen's streaming avatar technology.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

## ✨ Features

- 🎯 **Intelligent Complaint Handling**: LangGraph-powered agent for structured conversation flow
- 🔄 **Customer Registration Check**: Automatic lookup of registered customers
- 📍 **Address Management**: Smart address collection and validation
- 🎭 **Interactive Avatar**: HeyGen streaming avatar with real-time lip-sync
- 🚀 **Modern UI**: Clean, responsive interface inspired by leading AI assistants
- 📊 **State Management**: Persistent session tracking across conversations
- 🔌 **RESTful API**: FastAPI backend with automatic documentation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      React Frontend                      │
│  ┌────────────────────┐    ┌─────────────────────────┐ │
│  │   Chat Interface   │    │   HeyGen Avatar Panel   │ │
│  │  - Message Display │    │  - Video Stream         │ │
│  │  - Input Area      │    │  - Voice Synthesis      │ │
│  │  - Session Mgmt    │    │  - Lip Sync             │ │
│  └────────────────────┘    └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Backend                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │              API Endpoints                          │ │
│  │  /api/chat  •  /api/session/clear                  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   LangGraph Agent                        │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Agent State Machine                                │ │
│  │  • Complaint Collection                             │ │
│  │  • Phone Number Extraction                          │ │
│  │  • Registration Check                               │ │
│  │  • Address Validation                               │ │
│  │  • Confirmation & Submission                        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- HeyGen API account

### 1. Clone and Setup Backend

```bash
cd CallTaker
source venv/bin/activate
pip install -r requirements.txt -r backend/requirements.txt
```

### 2. Setup Frontend

```bash
cd frontend
npm install
echo "VITE_HEYGEN_API_KEY=your_key_here" > .env
```

### 3. Run

**Terminal 1 - Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start_frontend.sh
```

**Access:** http://localhost:3000

📖 See [QUICKSTART.md](./QUICKSTART.md) for detailed instructions.

## 📁 Project Structure

```
CallTaker/
├── backend/                    # FastAPI backend
│   ├── main.py                # API endpoints & session management
│   └── requirements.txt       # Backend dependencies
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── AvatarPanel.jsx    # HeyGen avatar integration
│   │   ├── App.jsx                # Main chat interface
│   │   ├── App.css                # Styles
│   │   └── main.jsx               # Entry point
│   ├── package.json
│   └── vite.config.js
├── src/agent/                  # LangGraph agent
│   ├── complaint_agent.py     # Agent logic & state machine
│   └── utils.py               # Helper functions
├── start_backend.sh           # Backend startup script
├── start_frontend.sh          # Frontend startup script
├── QUICKSTART.md             # Quick start guide
└── SETUP_INSTRUCTIONS.md     # Detailed setup guide
```

## 🎯 Agent Flow

The agent follows this conversation flow:

1. **Greeting** → Introduces as Camila
2. **Complaint Collection** → Asks for issue description
3. **Phone Number** → Requests contact number
4. **Registration Check** → Looks up customer in database
5. **Address Handling**:
   - Registered: Shows address on file
   - Non-registered: Asks for address
6. **Confirmation** → Reviews details with customer
7. **Submission** → Submits to technical team
8. **Closure** → Explains next steps, offers continued help

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, high-performance web framework
- **LangGraph**: State machine for conversation flow
- **LangChain**: LLM orchestration
- **OpenAI GPT-4**: Language model
- **Python-dotenv**: Environment management

### Frontend
- **React**: UI framework
- **Vite**: Build tool & dev server
- **Axios**: HTTP client
- **HeyGen SDK**: Avatar streaming
- **UUID**: Session management

## 🔧 Configuration

### Backend (.env in project root)
```env
OPENAI_API_KEY=your_openai_key
```

### Frontend (frontend/.env)
```env
VITE_HEYGEN_API_KEY=your_heygen_key
VITE_API_URL=http://localhost:8000
```

## 📡 API Endpoints

### POST `/api/chat`
Send a message to the agent.

**Request:**
```json
{
  "session_id": "uuid-v4",
  "message": "my pipes are leaking"
}
```

**Response:**
```json
{
  "response": "Oh no, I'm really sorry...",
  "agent_state": {
    "complaint": "...",
    "mobile_number": "...",
    "is_registered": true,
    "customer_data": {...}
  },
  "session_id": "uuid-v4"
}
```

### POST `/api/session/clear`
Clear session state.

### GET `/api/session/{session_id}`
Retrieve session state.

## 🎭 HeyGen Avatar

The application uses HeyGen's streaming avatar API to provide:

- **Real-time voice synthesis**
- **Lip-sync animation**
- **Natural expressions**
- **Low latency streaming**

Customize avatar in `frontend/src/components/AvatarPanel.jsx`:

```javascript
avatarName: 'Anna_public_3_20240108',  // Change avatar
voice: { voiceId: '...' },              // Change voice
quality: AvatarQuality.High,             // Adjust quality
```

## 🔒 Security Notes

- API keys should be kept secure
- Session data is stored in-memory (use Redis for production)
- CORS is configured for development (tighten for production)
- Add rate limiting for production deployment

## 📊 State Management

The agent maintains the following state:

```typescript
{
  complaint: string | null
  mobile_number: string | null
  is_registered: boolean | null
  customer_data: {
    priorityId: string
    sectorId: string
    networkId: string
    areaId: string
    labId: string
    commercialBranchCode: string
    clientAddress: string
  }
  address_loaded_from_system: boolean
  address_updated_by_user: boolean
  confirmation: boolean | null
  submitted: boolean
  messages: Message[]
}
```

## 🚢 Production Deployment

### Backend
```bash
# Use production ASGI server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to hosting service (Vercel, Netlify, etc.)
```

## 🐛 Troubleshooting

See [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md#troubleshooting) for common issues and solutions.

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- HeyGen for avatar technology
- OpenAI for GPT-4
- LangChain team for LangGraph
- FastAPI and React communities

## 📧 Support

For issues and questions:
- Check the [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)
- Review [QUICKSTART.md](./QUICKSTART.md)
- Open an issue on GitHub

---

**Built with ❤️ for better customer service**

