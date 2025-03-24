# profiles.py
import random
import openai
import os
import json
from typing import List, Dict, Any

# Define the Hinge prompts
HINGE_PROMPTS = [
    "A shower thought I recently had...",
    "My most irrational fear is...",
    "I get along best with people who...",
    "Dating me is like...",
    "The hallmark of a good relationship is...",
    "Don't hate me if I...",
    "Truth or dare?",
    "I go crazy for...",
    "I know the best spot in town for...",
    "My love language is...",
    "One thing I'll never do again...",
    "Let's make sure to...",
    "I'm overly competitive about...",
    "The last time I cried...",
    "My ideal weekend includes...",
    "I want someone who...",
    "I'm known for...",
    "My biggest date fail...",
    "Change my mind about...",
    "Unusual skills:",
    "Green flags I look for...",
    "The way to win me over is...",
    "My greatest strength...",
    "Most spontaneous thing I've done...",
    "We'll get along if..."
]

# Define diverse personality types
PERSONALITY_PROMPTS = [
    "Extroverted adventurer who loves thrills and taking risks. Very spontaneous and lives in the moment. Energetic and sometimes overwhelming, but always genuine.",
    "Analytical introvert who prefers deep one-on-one conversations. Values logic, intellectual discussions, and quiet reflection. May seem reserved at first but has strong opinions.",
    "Creative free spirit with eccentric tastes. Highly imaginative and sees beauty in unusual places. Can be flaky about plans but extremely passionate about their interests.",
    "Ambitious professional who is career-driven and disciplined. Values structure, achievement, and efficiency. May struggle with work-life balance but is loyal and reliable.",
    "Nurturing empath who prioritizes others' feelings. Extremely compassionate and supportive, often working in helping professions. Needs a partner who can offer emotional reciprocity.",
    "Witty comedian who uses humor as their primary social tool. Quick with jokes but may use them to avoid vulnerability. Values laughter and lightness in all situations.",
    "Spiritual seeker focused on personal growth and mindfulness. Values authenticity, emotional awareness, and meaningful connections. May be into alternative lifestyles.",
    "Practical homebody who values stability and comfort. Prefers quiet nights in over wild adventures. Reliable, grounded, and nurturing but can be resistant to change.",
    "Socially conscious activist passionate about making the world better. Strong values and convictions guide their choices. Can be intensely passionate about social causes.",
    "Refined aesthete with expensive taste and appreciation for luxury. Cultured and sophisticated with high standards. Knows quality and isn't afraid to be selective."
]

def generate_prompt_answers(personality: str, selected_prompts: List[str]) -> List[Dict[str, str]]:
    """Generate answers to Hinge prompts based on personality using OpenAI."""
    try:
        # Prepare the system prompt
        system_prompt = """
        You are creating dating profile answers for a dating app like Hinge.
        Create authentic, interesting responses based on the personality description provided.
        Keep responses relatively brief (1-3 sentences) and conversational, as if written by the user themselves.
        Make sure the answers reflect the personality traits described and feel like they come from the same person.
        Add subtle humor or authenticity where appropriate.
        """
        
        # Prepare the user prompt
        user_prompt = f"""
        Personality description: {personality}

        Please write responses to the following prompts for this dating profile:
        {selected_prompts[0]}
        {selected_prompts[1]}
        {selected_prompts[2]}
        
        Format your response as a JSON array of objects with 'prompt' and 'answer' fields.
        """
        
        response = openai.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        
        # Extract and parse the response
        answer_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON
        try:
            # Find JSON array in the text if it's not formatted perfectly
            start_idx = answer_text.find('[')
            end_idx = answer_text.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = answer_text[start_idx:end_idx]
                answers = json.loads(json_str)
                return answers
            
            # If we can't find brackets, try parsing the whole response
            answers = json.loads(answer_text)
            return answers
        except json.JSONDecodeError:
            # If parsing fails, create a structured response manually
            fallback_answers = []
            for i, prompt in enumerate(selected_prompts):
                # Look for the prompt in the text and extract the answer
                prompt_idx = answer_text.find(prompt)
                if prompt_idx >= 0:
                    next_prompt_idx = answer_text.find(selected_prompts[i+1]) if i < len(selected_prompts)-1 else len(answer_text)
                    answer = answer_text[prompt_idx + len(prompt):next_prompt_idx].strip()
                    fallback_answers.append({"prompt": prompt, "answer": answer})
                else:
                    # If we can't find the prompt, use a generic answer
                    fallback_answers.append({"prompt": prompt, "answer": "Sorry, I'll fill this in later!"})
            
            return fallback_answers
            
    except Exception as e:
        print(f"Error generating prompt answers: {e}")
        # Provide fallback answers if OpenAI fails
        return [
            {"prompt": selected_prompts[0], "answer": "I'll answer this soon!"},
            {"prompt": selected_prompts[1], "answer": "Still thinking about this one..."},
            {"prompt": selected_prompts[2], "answer": "Ask me about this!"}
        ]

def generate_user_profiles(num_profiles=10):
    names = ["Alex", "Sam", "Jordan", "Taylor", "Casey", "Morgan", "Drew", "Jesse", "Quinn", "Dana"]
    bios = [
        "Love traveling and cooking", 
        "Fitness enthusiast", 
        "Tech geek into AI", 
        "Music lover and aspiring DJ",
        "Dog parent, coffee addict"
    ]
    
    interests_pool = [
        "Movies", "Sports", "Art", "Music", "Travel", "Reading", 
        "Hiking", "Photography", "Cooking", "Gaming", "Yoga", 
        "Dancing", "Fashion", "Writing", "Fitness", "Meditation",
        "Camping", "Skiing", "Languages", "Cycling", "Painting",
        "Volunteering", "Astronomy", "Gardening", "Podcasts"
    ]
    
    profiles = []
    
    # Ensure we don't run out of personalities if num_profiles > len(PERSONALITY_PROMPTS)
    personalities = PERSONALITY_PROMPTS.copy()
    if num_profiles > len(personalities):
        # Add random personalities if we need more
        for i in range(num_profiles - len(personalities)):
            personalities.append(random.choice(PERSONALITY_PROMPTS))
    
    # Shuffle personalities to ensure variety
    random.shuffle(personalities)
    
    for i in range(num_profiles):
        # Randomly select 3-5 interests for each user
        user_interests = random.sample(interests_pool, random.randint(3, 5))
        
        # Select a personality
        personality = personalities[i % len(personalities)]
        
        # Select 3 random prompts from the list
        selected_prompts = random.sample(HINGE_PROMPTS, 3)
        
        # Generate answers to the prompts
        prompt_answers = generate_prompt_answers(personality, selected_prompts)
        
        profile = {
            'id': i,
            'name': names[i % len(names)] + str(i),
            'age': random.randint(20, 40),
            'bio': random.choice(bios),
            'interests': user_interests,
            'personality': personality,
            'prompt_answers': prompt_answers
        }
        profiles.append(profile)
    
    return profiles 