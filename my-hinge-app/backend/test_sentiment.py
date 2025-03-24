#!/usr/bin/env python3
# test_sentiment.py - Test script for sentiment analysis

from sentiment_analyzer import initialize_nlp, analyze_sentiment
import time

def test_simple_conversation():
    """Test sentiment analysis with a simple conversation"""
    print("Testing simple conversation...")
    conversation = [
        "Alex: Hey there! How's it going?",
        "Sam: Pretty good, thanks for asking! How about you?",
        "Alex: I'm doing great. I really enjoyed that movie we talked about.",
        "Sam: Me too! It was fantastic. We should watch more films like that."
    ]
    
    score = analyze_sentiment(conversation)
    print(f"Positive conversation sentiment score: {score}")
    print("")
    
def test_negative_conversation():
    """Test sentiment analysis with a negative conversation"""
    print("Testing negative conversation...")
    conversation = [
        "Alex: I didn't like that restaurant at all.",
        "Sam: Me neither. The service was terrible and the food was cold.",
        "Alex: I'm never going back there again. What a waste of money.",
        "Sam: Agreed. Next time let's try somewhere else."
    ]
    
    score = analyze_sentiment(conversation)
    print(f"Negative conversation sentiment score: {score}")
    print("")

def test_mixed_conversation():
    """Test sentiment analysis with a mixed conversation"""
    print("Testing mixed conversation...")
    conversation = [
        "Alex: I had a terrible day at work today.",
        "Sam: I'm sorry to hear that. What happened?",
        "Alex: My presentation didn't go well, but my boss was actually supportive.",
        "Sam: That's good to hear! Everyone has off days. I'm sure you'll do better next time."
    ]
    
    score = analyze_sentiment(conversation)
    print(f"Mixed conversation sentiment score: {score}")
    print("")

def test_empty_conversation():
    """Test sentiment analysis with an empty conversation"""
    print("Testing empty conversation...")
    conversation = []
    
    score = analyze_sentiment(conversation)
    print(f"Empty conversation sentiment score: {score}")
    print("")

def test_one_sided_conversation():
    """Test sentiment analysis with a one-sided conversation"""
    print("Testing one-sided conversation...")
    conversation = [
        "Alex: Hey there!",
        "Alex: How's it going?",
        "Alex: Hello? Are you there?",
        "Alex: I guess you're busy. Talk later!"
    ]
    
    score = analyze_sentiment(conversation)
    print(f"One-sided conversation sentiment score: {score}")
    print("")

if __name__ == "__main__":
    print("Initializing NLP...")
    initialize_nlp()
    print("\nRunning sentiment analysis tests...")
    time.sleep(1)
    
    test_simple_conversation()
    test_negative_conversation()
    test_mixed_conversation()
    test_empty_conversation()
    test_one_sided_conversation()
    
    print("All tests completed!") 