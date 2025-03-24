# sentiment_analyzer.py
import spacy
from spacy.tokens import Doc, Span
from spacytextblob.spacytextblob import SpacyTextBlob
import re

# Load spaCy model
nlp = None

def initialize_nlp():
    """Initialize spaCy model with spacytextblob extension"""
    global nlp
    try:
        # Check if the model is already loaded
        if nlp is None:
            nlp = spacy.load("en_core_web_sm")
            # Add the TextBlob sentiment component
            if "spacytextblob" not in nlp.pipe_names:
                nlp.add_pipe("spacytextblob")
            print("NLP model loaded successfully")
    except Exception as e:
        print(f"Error loading spaCy model: {e}")
        print("Please make sure you have downloaded the model with:")
        print("python -m spacy download en_core_web_sm")

def analyze_sentiment(conversation):
    """
    Returns an average polarity for the entire conversation.
    Polarity range: -1.0 (most negative) to +1.0 (most positive).
    Also includes detailed sentiment breakdown by user and message.
    """
    # Make sure NLP is initialized
    initialize_nlp()
    
    if nlp is None:
        print("Warning: NLP model not initialized. Returning neutral sentiment.")
        return 0.0
    
    # Lists to store message-level detail
    message_details = []
    
    # Track each user's sentiment separately
    user_polarities = {}
    
    # Extract user names from conversation
    users = set()
    for message in conversation:
        name_end = message.find(':')
        if name_end > 0:
            name = message[:name_end].strip()
            users.add(name)
    
    print(f"Analyzing sentiment for conversation between {', '.join(users)}...")
    
    # Process each message in the conversation
    total_polarity = 0
    message_count = 0
    
    for message in conversation:
        # Split into name and content
        name_end = message.find(':')
        if name_end <= 0:
            continue
            
        name = message[:name_end].strip()
        content = message[name_end+1:].strip()
        
        # Skip empty messages
        if not content:
            continue
            
        # Process text content 
        doc = nlp(content)
        
        # Get message-level sentiment using TextBlob sentiment
        # In spacytextblob, blob property contains TextBlob object
        try:
            polarity = doc._.blob.polarity  
            subjectivity = doc._.blob.subjectivity
        except AttributeError:
            # Fallback if attributes aren't available
            print(f"Warning: Unable to access sentiment attributes for message: {content}")
            polarity = 0
            subjectivity = 0.5
        
        message_count += 1
        total_polarity += polarity
        
        # Initialize user data structure if needed
        if name not in user_polarities:
            user_polarities[name] = {
                "total_polarity": 0, 
                "total_subjectivity": 0,
                "count": 0,
                "messages": []
            }
        
        # Update user stats
        user_polarities[name]["total_polarity"] += polarity
        user_polarities[name]["total_subjectivity"] += subjectivity
        user_polarities[name]["count"] += 1
        user_polarities[name]["messages"].append({
            "text": content,
            "polarity": polarity,
            "subjectivity": subjectivity
        })
        
        # Store message details
        message_details.append({
            "name": name,
            "message": content,
            "polarity": polarity,
            "subjectivity": subjectivity
        })
    
    # Calculate overall conversation statistics
    overall_sentiment = total_polarity / message_count if message_count > 0 else 0.0
    
    # Calculate user-level sentiment
    user_sentiments = {}
    for name, data in user_polarities.items():
        user_sentiments[name] = {
            "average_polarity": data["total_polarity"] / data["count"] if data["count"] > 0 else 0.0,
            "average_subjectivity": data["total_subjectivity"] / data["count"] if data["count"] > 0 else 0.0,
            "message_count": data["count"],
            "message_sentiments": data["messages"]
        }
    
    # Calculate compatibility score between users
    compatibility_score = 0.0
    
    # If we have 2 or more users in the conversation
    if len(user_polarities) >= 2:
        # Get individual sentiment scores
        user_scores = [data["total_polarity"] / data["count"] if data["count"] > 0 else 0.0 
                       for data in user_polarities.values()]
        
        # Calculate the geometric mean of positive-shifted values
        pos_shifted = [(s + 1) / 2 for s in user_scores]  # Shift from [-1,1] to [0,1]
        
        # Find minimum score (weakest link)
        min_score = min(pos_shifted)
        
        # Find average score
        avg_score = sum(pos_shifted) / len(pos_shifted)
        
        # Detect pattern of increasing positivity (conversation getting better)
        trend_scores = []
        for name, data in user_polarities.items():
            if len(data["messages"]) >= 2:
                first_half = data["messages"][:len(data["messages"])//2]
                second_half = data["messages"][len(data["messages"])//2:]
                
                first_half_avg = sum(m["polarity"] for m in first_half) / len(first_half)
                second_half_avg = sum(m["polarity"] for m in second_half) / len(second_half)
                
                # Positive trend if second half is more positive
                trend_scores.append(1 if second_half_avg > first_half_avg else 0)
        
        # If we have trend data, use it
        trend_bonus = sum(trend_scores) / len(trend_scores) if trend_scores else 0.5
        
        # Final compatibility is weighted average of min, avg and trend
        compatibility_score = (0.4 * min_score) + (0.4 * avg_score) + (0.2 * trend_bonus)
    else:
        # If only one user, just use their sentiment directly (shouldn't happen in conversation)
        compatibility_score = (overall_sentiment + 1) / 2  # Convert from [-1,1] to [0,1]
    
    # Print detailed breakdown for debugging
    print(f"Overall sentiment: {overall_sentiment:.2f}")
    print(f"Compatibility score: {compatibility_score:.2f}")
    for name, data in user_sentiments.items():
        print(f"{name}'s average sentiment: {data['average_polarity']:.2f}")
    
    # Return the compatibility score (0-1 range)
    return compatibility_score 