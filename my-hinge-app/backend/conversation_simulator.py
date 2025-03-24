# conversation_simulator.py
import random
import openai
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def simulate_conversations(profiles):
    """
    Simulates conversations between all pairs of users.
    Returns a dict of: (userA_id, userB_id) -> list of messages (strings)
    """
    conversation_results = {}
    
    # Ensure all pairs of users talk to each other
    for i in range(len(profiles)):
        for j in range(len(profiles)):
            # Skip conversations with self
            if i == j:
                continue
                
            userA = profiles[i]
            userB = profiles[j]
            
            # Only process each pair once (avoid duplicates)
            if (userB['id'], userA['id']) in conversation_results:
                continue
            
            try:
                print(f"Simulating conversation between {userA['name']} and {userB['name']}...")
                conversation = simulate_conversation_with_ai(userA, userB)
                conversation_results[(userA['id'], userB['id'])] = conversation
            except Exception as e:
                print(f"Error with OpenAI API: {e}")
                # Create a simple placeholder conversation instead of using the basic function
                conversation = [
                    f"{userA['name']}: Hey {userB['name']}, how's it going?",
                    f"{userB['name']}: Hey {userA['name']}, I'm good! How are you?",
                    f"{userA['name']}: Doing pretty well. I saw you're into {userA['interests'][0] if userA['interests'] else 'cool stuff'}?",
                    f"{userB['name']}: Yeah! Been into that for a while. Do you like {userB['interests'][0] if userB['interests'] else 'anything fun'}?",
                    f"{userA['name']}: Absolutely! We should hang out sometime.",
                    f"{userB['name']}: Sounds good to me!"
                ]
                conversation_results[(userA['id'], userB['id'])] = conversation
    
    return conversation_results

def simulate_conversation_with_ai(userA, userB):
    """
    Simulates conversation using OpenAI API with improved context handling
    and more casual conversation style.
    """
    try:
        # Prepare a more detailed system prompt to guide conversation style
        system_prompt = """
        You are simulating a casual dating app conversation between two individuals on Hinge. 
        
        Guidelines:
        - Write in a very casual, natural tone like actual dating app messages
        - Use occasional slang, abbreviations, and emojis where appropriate
        - Keep messages relatively short (1-3 sentences max per message)
        - Avoid overly formal language or perfect grammar
        - Make the conversation feel authentic and spontaneous
        - Reference the users' interests and background naturally
        - Create a progression where each message builds on what was said before
        - Focus on creating a natural back-and-forth dynamic
        """
        
        # Prepare the user prompt with more detailed instructions
        user_prompt = f"""
        Simulate a casual Hinge dating app conversation between these two users:
        
        User 1: {userA['name']}, {userA['age']} years old
        Bio: {userA['bio']}
        Interests: {', '.join(userA['interests'])}
        
        User 2: {userB['name']}, {userB['age']} years old
        Bio: {userB['bio']}
        Interests: {', '.join(userB['interests'])}
        
        Generate a natural 8-message conversation (4 from each user, alternating) where they're getting to know each other.
        - Start with User 1 messaging first
        - Each message should clearly build on previous messages
        - Show genuine interest in each other's profiles
        - Keep the tone casual and conversational
        - Include some personality/humor based on their bios
        
        Format each message as "Name: message text"
        """
        
        response = openai.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=600,
            temperature=0.8,
        )
        
        # Extract and format the conversation
        ai_conversation_text = response.choices[0].message.content.strip()
        
        # Split into lines and clean up
        conversation = [line.strip() for line in ai_conversation_text.split('\n') if line.strip() and ':' in line]
        
        # Ensure we have at least two messages
        if len(conversation) < 2:
            # Create a simple placeholder conversation
            conversation = [
                f"{userA['name']}: Hey {userB['name']}, how's it going?",
                f"{userB['name']}: Hey {userA['name']}, I'm good! How are you?",
                f"{userA['name']}: Doing pretty well. I saw you're into {userA['interests'][0] if userA['interests'] else 'cool stuff'}?",
                f"{userB['name']}: Yeah! Been into that for a while. Do you like {userB['interests'][0] if userB['interests'] else 'anything fun'}?",
                f"{userA['name']}: Absolutely! We should hang out sometime.",
                f"{userB['name']}: Sounds good to me!"
            ]
            
        return conversation
    except Exception as e:
        print(f"Error using OpenAI API: {e}")
        # Create a simple placeholder conversation
        conversation = [
            f"{userA['name']}: Hey {userB['name']}, how's it going?",
            f"{userB['name']}: Hey {userA['name']}, I'm good! How are you?",
            f"{userA['name']}: Doing pretty well. I saw you're into {userA['interests'][0] if userA['interests'] else 'cool stuff'}?",
            f"{userB['name']}: Yeah! Been into that for a while. Do you like {userB['interests'][0] if userB['interests'] else 'anything fun'}?",
            f"{userA['name']}: Absolutely! We should hang out sometime.",
            f"{userB['name']}: Sounds good to me!"
        ]
        return conversation 