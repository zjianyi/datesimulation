#!/usr/bin/env python3
# comprehensive_sentiment_test.py - A comprehensive test for sentiment analysis

import requests
import time
import json
from sentiment_analyzer import initialize_nlp, analyze_sentiment

def test_standalone_sentiment_analyzer():
    """Test the sentiment analyzer directly"""
    print("\n========== TESTING STANDALONE SENTIMENT ANALYZER ==========")
    
    initialize_nlp()
    
    # Test cases with varying sentiment
    test_cases = [
        {
            "name": "Positive Conversation",
            "conversation": [
                "Alex: I really enjoyed our time together yesterday!",
                "Sam: Me too! It was so much fun. We should do it again soon.",
                "Alex: Definitely! How about this weekend?",
                "Sam: That sounds perfect! I'm looking forward to it."
            ]
        },
        {
            "name": "Negative Conversation",
            "conversation": [
                "Alex: I didn't like that movie at all.",
                "Sam: It was terrible. What a waste of time and money.",
                "Alex: The acting was awful and the plot made no sense.",
                "Sam: I agree. Let's never watch anything by that director again."
            ]
        },
        {
            "name": "Mixed Conversation",
            "conversation": [
                "Alex: I had a rough day at work today.",
                "Sam: I'm sorry to hear that. What happened?",
                "Alex: My project got rejected, but at least my boss was understanding.",
                "Sam: That's good. Tomorrow will be better!"
            ]
        },
        {
            "name": "Empty Conversation",
            "conversation": []
        },
        {
            "name": "Single Message Conversation",
            "conversation": ["Alex: Hello there!"]
        },
        {
            "name": "Long Conversation",
            "conversation": [
                "Alex: Hey there! How's it going?",
                "Sam: Pretty good, thanks for asking! How about you?",
                "Alex: I'm doing great. Just got back from a vacation.",
                "Sam: Oh nice! Where did you go?",
                "Alex: I went to Hawaii. It was amazing - beautiful beaches and perfect weather.",
                "Sam: That sounds incredible! I've always wanted to go there.",
                "Alex: You definitely should. The food was fantastic too.",
                "Sam: What was your favorite thing you did there?",
                "Alex: Probably the snorkeling. Saw so many colorful fish and even a sea turtle!",
                "Sam: Wow! That must have been an unforgettable experience."
            ]
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        conversation = test_case['conversation']
        
        try:
            score = analyze_sentiment(conversation)
            print(f"Sentiment score: {score:.2f}")
            
            # Range check
            if 0 <= score <= 1:
                print("✅ Score is in valid range (0-1)")
            else:
                print("❌ Score outside valid range (0-1)")
                
            # Expectation check
            if "Positive" in test_case["name"] and score > 0.6:
                print("✅ Positive conversation correctly scored high")
            elif "Negative" in test_case["name"] and score < 0.4:
                print("✅ Negative conversation correctly scored low")
            elif "Mixed" in test_case["name"] and 0.4 <= score <= 0.6:
                print("✅ Mixed conversation correctly scored neutral")
            
        except Exception as e:
            print(f"❌ Error during sentiment analysis: {str(e)}")

def test_api_endpoint(base_url="http://localhost:5000"):
    """Test the API endpoint for sentiment analysis"""
    print("\n========== TESTING API ENDPOINT ==========")
    
    # First reset the application state
    try:
        reset_response = requests.post(f"{base_url}/api/reset")
        if reset_response.status_code == 200:
            print("✅ Successfully reset application state")
        else:
            print(f"❌ Failed to reset application: {reset_response.text}")
            return
    except Exception as e:
        print(f"❌ Error resetting application: {str(e)}")
        return
    
    # Generate profiles
    try:
        profiles_response = requests.post(f"{base_url}/api/generate-profiles")
        if profiles_response.status_code == 200:
            profiles_data = profiles_response.json()
            profiles = profiles_data.get('profiles', [])
            print(f"✅ Successfully generated {len(profiles)} profiles")
        else:
            print(f"❌ Failed to generate profiles: {profiles_response.text}")
            return
    except Exception as e:
        print(f"❌ Error generating profiles: {str(e)}")
        return
    
    # Wait for profiles to complete
    wait_for_completion(base_url)
    
    # Simulate conversations
    try:
        conversations_response = requests.post(f"{base_url}/api/simulate-conversations")
        if conversations_response.status_code == 200:
            conversations_data = conversations_response.json()
            print(f"✅ Successfully started conversation simulation")
        else:
            print(f"❌ Failed to simulate conversations: {conversations_response.text}")
            return
    except Exception as e:
        print(f"❌ Error simulating conversations: {str(e)}")
        return
    
    # Wait for conversations to complete
    wait_for_completion(base_url)
    
    # Analyze sentiment
    try:
        sentiment_response = requests.post(f"{base_url}/api/analyze-sentiment")
        if sentiment_response.status_code == 200:
            sentiment_data = sentiment_response.json()
            all_pairs = sentiment_data.get('all_pairs', [])
            print(f"✅ Successfully analyzed sentiment for {len(all_pairs)} conversation pairs")
            
            # Check the sentiment scores
            for idx, pair in enumerate(all_pairs[:3]):  # Display first 3 pairs
                score = pair.get('sentiment_score', 0)
                userA = pair.get('userA_name', 'Unknown')
                userB = pair.get('userB_name', 'Unknown')
                print(f"  Pair {idx+1}: {userA} & {userB} - Score: {score:.2f}")
        else:
            print(f"❌ Failed to analyze sentiment: {sentiment_response.text}")
            return
    except Exception as e:
        print(f"❌ Error analyzing sentiment: {str(e)}")
        return
    
    # Wait for sentiment analysis to complete
    wait_for_completion(base_url)
    
    # Get final results
    try:
        results_response = requests.get(f"{base_url}/api/results")
        if results_response.status_code == 200:
            results_data = results_response.json()
            results = results_data.get('results', {})
            print(f"✅ Successfully retrieved final results")
            
            # Display some matches
            user_ids = list(results.keys())
            if user_ids:
                sample_user_id = user_ids[0]
                sample_user = results[sample_user_id]
                print(f"\nMatches for {sample_user['user']['name']}:")
                for match in sample_user.get('matches', []):
                    print(f"  {match['partner_name']} - Score: {match['sentiment_score']:.2f}")
        else:
            print(f"❌ Failed to get results: {results_response.text}")
            return
    except Exception as e:
        print(f"❌ Error getting results: {str(e)}")
        return

def wait_for_completion(base_url, timeout=120):
    """Wait for the current operation to complete"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            status_response = requests.get(f"{base_url}/api/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if not status_data.get('in_progress'):
                    # Operation completed
                    current_step = status_data.get('step')
                    message = status_data.get('message', '')
                    print(f"  Operation completed: {message}")
                    return True
                else:
                    # Still in progress
                    print(f"  In progress: {status_data.get('message', '')}")
            else:
                print(f"  Error checking status: {status_response.text}")
        except Exception as e:
            print(f"  Error polling status: {str(e)}")
        
        # Wait before checking again
        time.sleep(2)
    
    print(f"  Timeout after waiting {timeout} seconds")
    return False

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE SENTIMENT ANALYSIS TEST")
    print("=" * 80)
    
    # Test standalone sentiment analyzer
    test_standalone_sentiment_analyzer()
    
    # Test API endpoint
    test_api_endpoint()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80) 