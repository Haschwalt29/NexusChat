# 🤖 NexusChat

A real-time AI chat application built with Flask, Socket.IO, and OpenAI. Users can register, login, and have conversations with an AI assistant in real-time.

## ✨ Features

- **Real-time Chat**: Instant messaging with WebSocket connections
- **AI Integration**: Powered by OpenAI GPT models for intelligent responses
- **User Authentication**: JWT-based authentication with secure password hashing
- **Message History**: Persistent chat history stored in MongoDB
- **Modern UI**: Responsive design with beautiful gradient styling
- **Cross-platform**: Works on desktop and mobile devices

## 🛠️ Tech Stack

- **Backend**: Flask 3.0.3, Flask-SocketIO 5.3.6
- **Database**: MongoDB with PyMongo
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI**: OpenAI API integration
- **Frontend**: HTML5, CSS3, JavaScript, Socket.IO client
- **Deployment**: Docker, Gunicorn, Eventlet

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB database (local or cloud)
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NexusChat
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
JWT_SECRET=your-secret-key-here
OPENAI_MODEL=gpt-4o-mini
PORT=5000
```

## 📡 API Endpoints

### Authentication

- `POST /api/register` - Register a new user
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

- `POST /api/login` - Login user
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```

- `GET /api/history` - Get user's chat history
  - Requires Authorization header: `Bearer <jwt-token>`

### Health Check

- `GET /health` - Application health status

## 🔌 WebSocket Events

### Client to Server

- `connect` - Connect to chat (requires token in query params)
- `send_message` - Send a message to AI
  ```json
  {
    "message": "Hello, how are you?"
  }
  ```
- `disconnect` - Disconnect from chat

### Server to Client

- `message` - Receive a message (user or AI)
  ```json
  {
    "sender": "user|ai",
    "content": "Message content",
    "timestamp": "2024-01-01T12:00:00Z"
  }
  ```
- `system` - System notifications
  ```json
  {
    "message": "Welcome, username!"
  }
  ```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the Docker image
docker build -t nexuschat .

# Run the container
docker run -p 8000:8000 --env-file .env nexuschat
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  nexuschat:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGODB_URI=${MONGODB_URI}
      - JWT_SECRET=${JWT_SECRET}
      - OPENAI_MODEL=${OPENAI_MODEL}
    depends_on:
      - mongodb
  
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

## ☁️ Cloud Deployment

### Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn -k eventlet -w 1 -b 0.0.0.0:$PORT app:app`
5. Add environment variables in Render dashboard
6. Deploy!

### Heroku

1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your-key
   heroku config:set MONGODB_URI=your-mongodb-uri
   heroku config:set JWT_SECRET=your-secret
   ```
4. Deploy: `git push heroku main`

## 🧪 Testing

Run basic tests:

```bash
python -m pytest tests/
```

## 📁 Project Structure

```
NexusChat/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── Procfile                   # Heroku/Render deployment
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── templates/
│   └── index.html             # Chat interface
│
├── static/
│   └── .gitkeep               # Git placeholder
│
├── nexuschat/                 # Core application package
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── database.py            # MongoDB connection
│   ├── auth.py                # Authentication & JWT
│   ├── ai.py                  # OpenAI integration
│   └── sockets.py             # WebSocket handlers
│
├── tests/
│   └── test_basic.py          # Basic tests
│
└── docs/
    └── screenshots.md         # Application screenshots
```

## 🔒 Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Secure authentication with expiration
- **CORS Protection**: Configured for cross-origin requests
- **Input Validation**: Server-side validation for all inputs
- **Error Handling**: Comprehensive error handling and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request



For additional help, please open an issue on GitHub.

---

**Made with ❤️ using Flask and OpenAI**
