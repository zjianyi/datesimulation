# Hinge AI Match Simulation

This application simulates a Hinge-like dating platform with AI-powered conversations between users and sentiment analysis to determine matching scores.

## Features

- Creates 10 mock Hinge-style user profiles
- Simulates AI-driven conversations between user pairs
- Uses **spaCy** with **spaCyTextBlob** for sentiment analysis
- Ranks users' matches by sentiment score
- Displays profiles and conversation details in a modern front-end UI

## Project Structure

```
my-hinge-app/
├── backend/
│   ├── app.py                  # Main Flask application
│   ├── profiles.py             # User profile generation
│   ├── conversation_simulator.py # Conversation simulation
│   ├── sentiment_analyzer.py   # Sentiment analysis with spaCy
│   ├── requirements.txt        # Python dependencies
└── frontend/
    ├── index.html              # Frontend HTML
    └── app.js                  # Frontend JavaScript
```

## Setup Instructions

### 1. Install Backend Dependencies

```bash
# Navigate to the backend directory
cd my-hinge-app/backend

# Install Python dependencies
pip install -r requirements.txt

# Download the required spaCy model
python -m spacy download en_core_web_sm
```

### 2. Configure OpenAI API (Optional)

For AI-driven conversations, you will need an OpenAI API key. Edit `conversation_simulator.py` and uncomment the line:

```python
# openai.api_key = os.environ.get("OPENAI_API_KEY")
```

Set your API key as an environment variable:

```bash
# For Linux/macOS
export OPENAI_API_KEY="your-api-key-here"

# For Windows
set OPENAI_API_KEY=your-api-key-here
```

Or modify the code to use your key directly (not recommended for production).

### 3. Run the Flask Backend

```bash
# From the backend directory
python app.py
```

The Flask server will start on http://127.0.0.1:5000.

### 4. Open the Frontend

Simply open the `my-hinge-app/frontend/index.html` file in your web browser.

Or serve it using a local server:

```bash
# Using Python's built-in HTTP server
# From the frontend directory
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Extending the Application

Here are some potential ways to extend this project:

1. **Real User Data**: Replace mock profiles with a real user database.
2. **Custom NLP**: Train a custom spaCy model for more accurate sentiment analysis.
3. **User Authentication**: Add login/signup functionality.
4. **Real-time Chat**: Implement WebSockets for real-time messaging.
5. **Profile Images**: Add profile picture support using an image hosting API.
6. **Mobile App**: Convert to a mobile app using React Native or Flutter.

## Technologies Used

- **Backend**: Python, Flask, spaCy, spaCyTextBlob
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI**: OpenAI API (optional)

## License

MIT 