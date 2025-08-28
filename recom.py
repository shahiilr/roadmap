import google.generativeai as genai
import json
import re

# Configure the API key
genai.configure(api_key="AIzaSyB_P-MQBagaMSVt1snTZRjT8-eJePQO_ys")

def recommend_courses(user_interests, current_skills=None, career_goals=None, include_web_search=False):
    """
    Generate course recommendations using Gemini AI only.
    Pure AI-driven recommendations without web search.

    Args:
        user_interests (str): User's interests or preferred subjects
        current_skills (str, optional): User's current skills
        career_goals (str, optional): User's career goals
        include_web_search (bool): Always False for AI-only system

    Returns:
        dict: Dictionary containing AI recommendations only
    """
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Create the prompt for AI recommendations
    prompt = f"""
    You are an expert AI course recommender. Generate personalized course recommendations based on the user's profile.

    User Profile:
    - Interests: {user_interests}
    - Current Skills: {current_skills or 'Not specified'}
    - Career Goals: {career_goals or 'Not specified'}

    Generate EXACTLY 10 high-quality, relevant online courses distributed as follows:
    - 3 Beginner level courses
    - 4 Intermediate level courses
    - 3 Advanced level courses

    For each course, provide realistic and current information:
    {{
        "courses": [
            {{
                "title": "Specific, real course title",
                "platform": "Coursera/Udemy/edX/LinkedIn Learning/MIT OpenCourseWare/etc",
                "instructor": "Real instructor name or organization",
                "duration": "Realistic duration (e.g., '8 weeks', '3 months', '40 hours')",
                "difficulty": "Beginner/Intermediate/Advanced",
                "rating": "Realistic rating between 4.0-5.0/5",
                "price": "Realistic price (Free, $49/month, $99, etc.)",
                "description": "Compelling 2-3 sentence description of what they'll learn",
                "skills_gained": ["3-5 specific skills they'll master"],
                "url": "Realistic course URL from the platform",
                "level": "beginner/intermediate/advanced"
            }}
        ]
    }}

    IMPORTANT REQUIREMENTS:
    1. Use REAL, EXISTING courses from reputable platforms
    2. Ensure variety in platforms and instructors
    3. Make descriptions specific and compelling
    4. Provide accurate pricing and realistic ratings
    5. Focus on current, popular courses that actually exist
    6. Distribute difficulty levels appropriately
    7. Ensure URLs are realistic (don't use placeholder URLs)
    8. Skills should be specific and actionable

    Return ONLY the JSON object, no additional text or explanation.
    """

    ai_courses = []

    # Get AI-generated recommendations only
    try:
        print(f"🤖 Generating AI recommendations for: {user_interests}")
        response = model.generate_content(prompt)
        print(f"✅ AI Response received: {len(response.text) if response.text else 0} characters")

        # Parse the JSON response
        try:
            json_start = response.text.find('{')
            json_end = response.text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response.text[json_start:json_end]
                print(f"📄 Extracted JSON: {json_str[:200]}...")
                data = json.loads(json_str)
                ai_courses = data.get('courses', [])
                print(f"📚 Found {len(ai_courses)} courses")
                # Mark as AI-generated
                for course in ai_courses:
                    course['source'] = 'AI Generated'
            else:
                print("❌ No JSON found in response")
                ai_courses = []
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"🔍 Raw response: {response.text[:500]}...")
            ai_courses = []
    except Exception as e:
        print(f"❌ AI Recommendation Error: {e}")
        ai_courses = []

    # Return AI-only results
    return {
        'ai_courses': ai_courses,
        'web_courses': [],  # Always empty for AI-only system
        'all_courses': ai_courses
    }

def main():
    print("Course Recommendation System using Gemini API")
    print("=" * 50)

    # Get user input
    interests = input("What are your interests or preferred subjects? ")
    skills = input("What are your current skills? (optional) ")
    goals = input("What are your career goals? (optional) ")

    # Generate recommendations
    print("\nGenerating recommendations...")
    recommendations = recommend_courses(interests, skills, goals)

    # Display results
    print("\nRecommended Courses:")
    print("=" * 50)
    print(recommendations)

if __name__ == "__main__":
    main()
