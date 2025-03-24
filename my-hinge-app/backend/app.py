# app.py
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from profiles import generate_user_profiles
from conversation_simulator import simulate_conversations, simulate_conversation_with_ai
from sentiment_analyzer import analyze_sentiment, initialize_nlp
import time

app = Flask(__name__)
# Enable CORS with more explicit settings
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "X-Get-Current-Only"]}})

# Global state to store data between steps
app_state = {
    "profiles": None,
    "conversations": None,
    "sentiment_analyzed": None,
    "in_progress": False,
    "progress_step": None,
    "progress_message": None
}

# Initialize the NLP model at startup
@app.before_first_request
def before_first_request():
    initialize_nlp()

@app.route('/api/status', methods=['GET'])
def get_status():
    """Return the current status of the application"""
    return jsonify({
        "in_progress": app_state["in_progress"],
        "step": app_state["progress_step"],
        "message": app_state["progress_message"],
        "has_profiles": app_state["profiles"] is not None,
        "has_conversations": app_state["conversations"] is not None,
        "has_sentiment": app_state["sentiment_analyzed"] is not None
    })

@app.route('/api/generate-profiles', methods=['POST'])
def api_generate_profiles():
    """Generate user profiles"""
    # Check if this is just a request to get current profiles without regenerating
    if request.headers.get('X-Get-Current-Only') == 'true':
        if app_state["profiles"] is None:
            return jsonify({"error": "No profiles generated yet"}), 400
        return jsonify({
            "success": True,
            "profiles": app_state["profiles"],
            "message": "Retrieved existing profiles"
        })
    
    if app_state["in_progress"]:
        return jsonify({"error": "Another operation is in progress"}), 409
    
    # Start the operation
    app_state["in_progress"] = True
    app_state["progress_step"] = "generate_profiles"
    app_state["progress_message"] = "Generating user profiles..."
    
    try:
        # Get number of profiles from request or use default
        num_profiles = request.json.get("num_profiles", 10) if request.is_json else 10
        
        # Generate profiles
        app_state["profiles"] = generate_user_profiles(num_profiles=num_profiles)
        
        # Reset other state since we have new profiles
        app_state["conversations"] = None
        app_state["sentiment_analyzed"] = None
        
        # Complete the operation
        app_state["in_progress"] = False
        app_state["progress_message"] = f"Generated {len(app_state['profiles'])} user profiles"
        
        return jsonify({
            "success": True,
            "profiles": app_state["profiles"],
            "message": f"Generated {len(app_state['profiles'])} user profiles"
        })
        
    except Exception as e:
        app_state["in_progress"] = False
        app_state["progress_message"] = f"Error generating profiles: {str(e)}"
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulate-conversations', methods=['POST'])
def api_simulate_conversations():
    """Simulate conversations between user pairs"""
    # Check if this is just a request to get current conversations without resimulating
    if request.headers.get('X-Get-Current-Only') == 'true':
        if app_state["conversations"] is None:
            return jsonify({"error": "No conversations simulated yet"}), 400
        
        # Get a sample conversation for the response
        sample_pair = next(iter(app_state["conversations"].items()))
        sample_conversation = sample_pair[1]
        
        return jsonify({
            "success": True,
            "num_conversations": len(app_state["conversations"]),
            "sample_conversation": {
                "pair": sample_pair[0],
                "messages": sample_conversation
            },
            "message": "Retrieved existing conversations"
        })
    
    if app_state["in_progress"]:
        return jsonify({"error": "Another operation is in progress"}), 409
    
    if not app_state["profiles"]:
        return jsonify({"error": "No profiles generated yet. Generate profiles first."}), 400
    
    # Start the operation
    app_state["in_progress"] = True
    app_state["progress_step"] = "simulate_conversations"
    app_state["progress_message"] = "Simulating conversations between users..."
    
    try:
        # Simulate conversations
        profiles = app_state["profiles"]
        app_state["conversations"] = simulate_conversations(profiles)
        
        # Reset sentiment analysis since we have new conversations
        app_state["sentiment_analyzed"] = None
        
        # Get a sample conversation for the response
        sample_pair = next(iter(app_state["conversations"].items()))
        sample_conversation = sample_pair[1]
        
        # Complete the operation
        app_state["in_progress"] = False
        app_state["progress_message"] = f"Simulated {len(app_state['conversations'])} conversations"
        
        return jsonify({
            "success": True,
            "num_conversations": len(app_state["conversations"]),
            "sample_conversation": {
                "pair": sample_pair[0],
                "messages": sample_conversation
            },
            "message": f"Simulated {len(app_state['conversations'])} conversations"
        })
        
    except Exception as e:
        app_state["in_progress"] = False
        app_state["progress_message"] = f"Error simulating conversations: {str(e)}"
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze-sentiment', methods=['POST'])
def api_analyze_sentiment():
    """Analyze sentiment of conversations"""
    if app_state["in_progress"]:
        return jsonify({"error": "Another operation is in progress"}), 400
    
    if not app_state["conversations"]:
        return jsonify({"error": "No conversations to analyze. Generate profiles and simulate conversations first."}), 400
    
    try:
        app_state["in_progress"] = True
        app_state["progress_step"] = "ANALYZING_SENTIMENT"
        app_state["progress_message"] = "Analyzing sentiment..."
        
        # Create a simplified data structure for sentiment analysis
        conversation_pairs = []
        user_conversations = {}
        for (userA_id, userB_id), conversation in app_state["conversations"].items():
            user_conversations[(userA_id, userB_id)] = conversation
            conversation_pairs.append((userA_id, userB_id, conversation))
        
        profiles = app_state["profiles"]
        
        # Initialize user-match structure
        user_matches = {}
        for profile in profiles:
            user_matches[profile['id']] = {
                'user': profile,
                'matches': []
            }
        
        # Process all conversation pairs
        scored_pairs = []
        for userA_id, userB_id, conversation in conversation_pairs:
            # Get user names for output
            userA = next((p for p in profiles if p['id'] == userA_id), None)
            userB = next((p for p in profiles if p['id'] == userB_id), None)
            
            if not userA or not userB:
                continue
                
            userA_name = userA['name'] 
            userB_name = userB['name']
            
            try:
                print(f"Analyzing sentiment for conversation between {userA_name}, {userB_name}...")
                sentiment_score = analyze_sentiment(conversation)
                
                # Add to scored pairs
                scored_pairs.append({
                    'userA_id': userA_id,
                    'userB_id': userB_id,
                    'userA_name': userA_name,
                    'userB_name': userB_name,
                    'sentiment_score': sentiment_score,
                    'conversation': conversation
                })
            except Exception as e:
                print(f"Error analyzing sentiment between {userA_name} and {userB_name}: {str(e)}")
                # Provide a neutral score as fallback
                scored_pairs.append({
                    'userA_id': userA_id,
                    'userB_id': userB_id,
                    'userA_name': userA_name,
                    'userB_name': userB_name,
                    'sentiment_score': 0.5,  # Neutral score
                    'conversation': conversation,
                    'error': str(e)
                })
        
        # Sort by sentiment score (highest first)
        scored_pairs_sorted = sorted(scored_pairs, key=lambda x: x['sentiment_score'], reverse=True)
        
        # For each user, find top 3 matches
        for pair in scored_pairs_sorted:
            userA_id = pair['userA_id']
            userB_id = pair['userB_id']
            
            # Add match data for both sides if they don't have 3 yet
            if len(user_matches[userA_id]['matches']) < 3:
                userB = next((p for p in profiles if p['id'] == userB_id), None)
                user_matches[userA_id]['matches'].append({
                    'partner_id': userB_id,
                    'partner_name': userB['name'] if userB else f"User {userB_id}",
                    'sentiment_score': pair['sentiment_score'],
                    'conversation': pair['conversation']
                })
            
            if len(user_matches[userB_id]['matches']) < 3:
                userA = next((p for p in profiles if p['id'] == userA_id), None)
                user_matches[userB_id]['matches'].append({
                    'partner_id': userA_id,
                    'partner_name': userA['name'] if userA else f"User {userA_id}",
                    'sentiment_score': pair['sentiment_score'],
                    'conversation': pair['conversation']
                })
        
        # Store the results
        app_state["sentiment_analyzed"] = {
            'results': user_matches,
            'all_pairs': scored_pairs_sorted
        }
        
        # Complete the operation
        app_state["in_progress"] = False
        app_state["progress_message"] = "Sentiment analysis complete"
        
        return jsonify({
            "success": True,
            "results": user_matches,
            "all_pairs": scored_pairs_sorted
        })
        
    except Exception as e:
        app_state["in_progress"] = False
        app_state["progress_message"] = f"Error analyzing sentiment: {str(e)}"
        return jsonify({"error": str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    """Get the final results"""
    if not app_state["sentiment_analyzed"]:
        return jsonify({"error": "No sentiment analysis has been performed yet. Complete all steps first."}), 400
    
    return jsonify(app_state["sentiment_analyzed"])

@app.route('/api/reset', methods=['POST'])
def reset_state():
    """Reset the application state"""
    app_state["profiles"] = None
    app_state["conversations"] = None
    app_state["sentiment_analyzed"] = None
    app_state["in_progress"] = False
    app_state["progress_step"] = None
    app_state["progress_message"] = "Application reset"
    
    return jsonify({
        "success": True,
        "message": "Application reset successfully"
    })

# Add a route to get detailed conversation for a specific pair
@app.route('/api/conversation/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_conversation(user1_id, user2_id):
    if not app_state["profiles"]:
        return jsonify({"error": "No profiles generated yet"}), 400
    
    profiles = app_state["profiles"]
    user1 = next((p for p in profiles if p['id'] == user1_id), None)
    user2 = next((p for p in profiles if p['id'] == user2_id), None)
    
    if not user1 or not user2:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if conversation exists in cached conversations
    if app_state["conversations"]:
        if (user1_id, user2_id) in app_state["conversations"]:
            conversation = app_state["conversations"][(user1_id, user2_id)]
        elif (user2_id, user1_id) in app_state["conversations"]:
            conversation = app_state["conversations"][(user2_id, user1_id)]
        else:
            # Generate a new conversation for this pair
            try:
                conversation = simulate_conversation_with_ai(user1, user2)
            except Exception as e:
                return jsonify({'error': f'Error generating conversation: {str(e)}'}), 500
    else:
        # Generate a new conversation for this pair
        try:
            conversation = simulate_conversation_with_ai(user1, user2)
        except Exception as e:
            return jsonify({'error': f'Error generating conversation: {str(e)}'}), 500
    
    # Analyze sentiment
    try:
        sentiment_score = analyze_sentiment(conversation)
    except Exception as e:
        print(f"Error analyzing sentiment: {str(e)}")
        sentiment_score = 0.5  # Use neutral sentiment as fallback
    
    return jsonify({
        'user1': user1,
        'user2': user2,
        'conversation': conversation,
        'sentiment_score': sentiment_score
    })

# Add an OPTIONS route handler for CORS preflight requests
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-Get-Current-Only')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 