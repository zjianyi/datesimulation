# Hinge AI Match Simulation

An AI-powered dating app simulation that creates user profiles, simulates conversations, and analyzes sentiment to find compatible matches.

## Features

- **Profile Generation**: Creates profiles with personalities, interests, and responses to Hinge-style prompts
- **AI Conversations**: Simulates natural conversations between users using OpenAI
- **Sentiment Analysis**: Analyzes conversation sentiment to determine compatibility
- **Interactive UI**: Modern web interface to visualize the matching process

## Project Structure

```
my-hinge-app/
├── backend/             # Flask API server
│   ├── app.py           # Main Flask application
│   ├── profiles.py      # User profile generation
│   ├── conversation_simulator.py # Conversation simulation
│   ├── sentiment_analyzer.py # Sentiment analysis with spaCy
│   ├── requirements.txt      # Python dependencies
│   ├── test_sentiment.py     # Test script for sentiment analysis
│   └── comprehensive_sentiment_test.py # Comprehensive testing
└── frontend/
    ├── index.html       # Frontend HTML
    ├── app.js           # Frontend JavaScript
    ├── proxy.js         # CORS proxy for local development
    ├── test-cors.html   # Testing page for CORS issues
    ├── no-cors.html     # Testing page with no-cors mode
    └── jquery-test.html # Testing page with jQuery
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/zjianyi/datesimulation.git
cd datesimulation
```

### 2. Backend Setup

```bash
cd my-hinge-app/backend

# Install Python dependencies
pip install -r requirements.txt

# Download the required spaCy model
python -m spacy download en_core_web_sm
```

### 3. Configure OpenAI API

Create a `.env` file in the backend directory with your OpenAI API key:

```
OPENAI_API_KEY=your-api-key-here
```

Then update `conversation_simulator.py` to load the API key:

```python
# Uncomment this line in conversation_simulator.py
openai.api_key = os.environ.get("OPENAI_API_KEY")
```

### 4. Start the Backend Server

```bash
cd my-hinge-app/backend
python app.py
```

The Flask server will start on http://localhost:5001.

### 5. Start the CORS Proxy (recommended for local development)

```bash
cd my-hinge-app/frontend
node proxy.js
```

The proxy server will start on http://localhost:3000 and forward requests to the backend.

### 6. Start the Frontend Server

```bash
cd my-hinge-app/frontend
python -m http.server 8000
```

Open http://localhost:8000 in your browser to access the application.

## Usage

1. **Generate Profiles**: Click the "Generate Profiles" button to create 10 user profiles with distinct personalities and prompt answers.
2. **Simulate Conversations**: Click "Simulate Conversations" to generate AI-powered conversations between users.
3. **Analyze Sentiment**: Click "Analyze Sentiment" to evaluate conversation compatibility.
4. **View Results**: Browse through user profiles and their top matches.
5. **View Conversations**: Click on any match to see their profile details, prompt answers, and conversation.

## Technologies Used

- **Backend**: Python, Flask, spaCy, spaCyTextBlob, OpenAI API
- **Frontend**: HTML, CSS, JavaScript, Bootstrap

## License

MIT 