import google.generativeai as genai
import json
import random
import time
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("🔧 Using environment variables from system or default values")

# Configuration
@dataclass
class Config:
    """Configuration settings for the AI course recommender"""
    max_retries: int = None
    retry_delay: float = None
    cache_size: int = None
    request_timeout: int = None
    max_courses_per_level: Dict[str, int] = None

    def __post_init__(self):
        # Load from environment variables with fallbacks
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.retry_delay = float(os.getenv('RETRY_DELAY', 2.0))
        self.cache_size = int(os.getenv('CACHE_SIZE', 50))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', 30))

        if self.max_courses_per_level is None:
            self.max_courses_per_level = {
                'beginner': 3,
                'intermediate': 4,
                'advanced': 3
            }

# Global configuration
config = Config()

# Load API Keys from environment variables
def load_api_keys() -> List[str]:
    """Load API keys from environment variables"""
    api_keys = []

    # Primary API Key
    key1 = os.getenv('GEMINI_API_KEY_1')
    if key1:
        api_keys.append(key1)
        print("✅ Primary API key loaded")
    else:
        print("⚠️  Primary API key (GEMINI_API_KEY_1) not found in environment")

    # Secondary API Key
    key2 = os.getenv('GEMINI_API_KEY_2')
    if key2:
        api_keys.append(key2)
        print("✅ Secondary API key loaded")
    else:
        print("⚠️  Secondary API key (GEMINI_API_KEY_2) not found in environment")

    if not api_keys:
        raise ValueError(
            "❌ No API keys found! Please set GEMINI_API_KEY_1 and/or GEMINI_API_KEY_2 in your .env file\n"
            "Example .env file:\n"
            "GEMINI_API_KEY_1=your_api_key_here\n"
            "GEMINI_API_KEY_2=your_backup_api_key_here"
        )

    print(f"🔑 Loaded {len(api_keys)} API key(s) for Gemini AI")
    return api_keys

# API Keys for redundancy and load balancing
API_KEYS = load_api_keys()

class GeminiAPIClient:
    """Efficient Gemini API client with key rotation and error handling"""

    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.max_retries = config.max_retries
        self.retry_delay = config.retry_delay
        self.request_count = 0
        self.error_count = 0

    def _get_next_api_key(self) -> str:
        """Rotate through available API keys"""
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def _configure_api(self, api_key: str):
        """Configure the API with the given key"""
        genai.configure(api_key=api_key)

    def generate_content(self, prompt: str) -> str:
        """Generate content with automatic retry and key rotation"""
        self.request_count += 1
        last_error = None

        for attempt in range(self.max_retries):
            try:
                api_key = self._get_next_api_key()
                self._configure_api(api_key)

                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)

                return response.text

            except Exception as e:
                self.error_count += 1
                last_error = e
                if attempt < self.max_retries - 1:
                    print(f"⚠️  API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                    print(f"🔄 Retrying with next API key in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"❌ All API keys failed after {self.max_retries} attempts")

        raise last_error

    def get_stats(self) -> Dict[str, float]:
        """Get API usage statistics"""
        success_rate = ((self.request_count - self.error_count) / self.request_count * 100) if self.request_count > 0 else 0
        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'success_rate': round(success_rate, 2)
        }

# Initialize the API client
api_client = GeminiAPIClient(API_KEYS)

class SimpleCache:
    """Simple in-memory cache for API responses"""

    def __init__(self, max_size: int = None):
        self.max_size = max_size or config.cache_size
        self.cache = {}
        self.access_order = []

    def _generate_key(self, interests: str, skills: str, goals: str) -> str:
        """Generate a cache key from user inputs"""
        return f"{interests.lower().strip()}_{skills.lower().strip()}_{goals.lower().strip()}"

    def get(self, interests: str, skills: str, goals: str) -> Optional[List[Dict]]:
        """Get cached results if available"""
        key = self._generate_key(interests, skills or "", goals or "")
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, interests: str, skills: str, goals: str, courses: List[Dict]):
        """Cache the results"""
        key = self._generate_key(interests, skills or "", goals or "")

        # Remove oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]

        self.cache[key] = courses
        self.access_order.append(key)

    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
        self.access_order.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'cached_queries': len(self.cache),
            'max_size': self.max_size,
            'cache_hit_rate': 0  # Could be improved with hit/miss tracking
        }

# Initialize cache
cache = SimpleCache()

def display_system_stats():
    """Display system performance statistics"""
    api_stats = api_client.get_stats()
    cache_stats = cache.get_stats()

    print("\n📊 SYSTEM STATISTICS:")
    print("=" * 40)
    print(f"🤖 API Requests: {api_stats['total_requests']}")
    print(f"❌ API Errors: {api_stats['total_errors']}")
    print(f"✅ Success Rate: {api_stats['success_rate']}%")
    print(f"💾 Cached Queries: {cache_stats['cached_queries']}/{cache_stats['max_size']}")
    print(f"🔄 API Keys Available: {len(API_KEYS)}")
    print("=" * 40)

def recommend_courses(user_interests: str, current_skills: Optional[str] = None, career_goals: Optional[str] = None) -> List[Dict]:
    """
    Generate course recommendations using Gemini AI with efficient API management and caching.

    Args:
        user_interests (str): User's interests or preferred subjects
        current_skills (str, optional): User's current skills
        career_goals (str, optional): User's career goals

    Returns:
        List[Dict]: List of AI-generated course dictionaries
    """
    # Check cache first
    cached_result = cache.get(user_interests, current_skills or "", career_goals or "")
    if cached_result:
        print("📋 Using cached recommendations for faster response!")
        return cached_result

    print("🤖 Generating fresh AI recommendations...")

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
    7. Provide realistic URLs (don't use placeholder URLs)
    8. Skills should be specific and actionable

    Return ONLY the JSON object, no additional text or explanation.
    """

    # Get AI-generated recommendations with efficient API handling
    try:
        response_text = api_client.generate_content(prompt)

        # Parse the JSON response
        try:
            # Extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                ai_courses = data.get('courses', [])

                # Mark as AI-generated and validate courses
                validated_courses = []
                for course in ai_courses:
                    if all(key in course for key in ['title', 'platform', 'url']):
                        course['source'] = 'AI Generated'
                        validated_courses.append(course)

                # Cache the results for future use
                if validated_courses:
                    cache.set(user_interests, current_skills or "", career_goals or "", validated_courses)

                return validated_courses
            else:
                print("⚠️  No valid JSON found in response")
                return []
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse AI response as JSON: {e}")
            return []
    except Exception as e:
        print(f"❌ AI Recommendation Error: {e}")
        return []

def main():
    """Main function with efficient course recommendation system"""
    print("🎓 AI Course Recommendation System")
    print("=" * 60)
    print("🚀 Powered by Google Gemini AI with intelligent caching")
    print("🔑 Multiple API keys for maximum reliability")
    print("=" * 60)

    # Get user input with validation
    try:
        interests = input("What are your interests or preferred subjects? ").strip()
        if not interests:
            print("❌ Please enter your interests to get recommendations.")
            return

        skills = input("What are your current skills? (optional) ").strip()
        goals = input("What are your career goals? (optional) ").strip()

        # Generate recommendations
        start_time = time.time()
        courses = recommend_courses(interests, skills, goals)
        end_time = time.time()

        # Display results
        if not courses:
            print("\n❌ No courses found. Please try again with different keywords.")
            return

        print(f"\n📚 Found {len(courses)} AI-generated courses in {end_time - start_time:.2f} seconds:")
        print("=" * 60)

        # Display system stats
        display_system_stats()

    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user. Goodbye!")
        return
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        return

    # Categorize courses by difficulty
    beginner_courses = [course for course in courses if course.get('level', '').lower() == 'beginner']
    intermediate_courses = [course for course in courses if course.get('level', '').lower() == 'intermediate']
    advanced_courses = [course for course in courses if course.get('level', '').lower() == 'advanced']

    def display_course_section(courses, level_name, level_icon):
        if not courses:
            return

        print(f"\n{level_icon} {level_name} Level Courses ({len(courses)} courses)")
        print("-" * 40)

        for i, course in enumerate(courses, 1):
            print(f"\n{i}. 📖 {course.get('title', 'Unknown Title')}")
            print(f"   🏫 Platform: {course.get('platform', 'Unknown')}")
            print(f"   👨‍🏫 Instructor: {course.get('instructor', 'Unknown')}")
            print(f"   ⏱️  Duration: {course.get('duration', 'Unknown')}")
            print(f"   ⭐ Rating: {course.get('rating', 'N/A')}/5")
            print(f"   💰 Price: {course.get('price', 'Unknown')}")
            print(f"   🔗 Course Link: {course.get('url', 'No link available')}")

            print(f"   📝 Description: {course.get('description', 'No description available')}")

            skills = course.get('skills_gained', [])
            if skills:
                print(f"   🎯 Skills you'll gain: {', '.join(skills)}")

            print(f"   🤖 Source: {course.get('source', 'AI Generated')}")
            print("-" * 40)

    # Display courses by difficulty level
    display_course_section(beginner_courses, "Beginner", "🟢")
    display_course_section(intermediate_courses, "Intermediate", "🟡")
    display_course_section(advanced_courses, "Advanced", "🔴")

    # Summary
    print("\n📊 SUMMARY:")
    print(f"   🟢 Beginner: {len(beginner_courses)} courses")
    print(f"   🟡 Intermediate: {len(intermediate_courses)} courses")
    print(f"   🔴 Advanced: {len(advanced_courses)} courses")
    print(f"   🎯 Total: {len(courses)} courses")

    print("\n💡 TIPS:")
    print("   • Copy and paste the course links into your browser to enroll")
    print("   • Start with beginner courses if you're new to the topic")
    print("   • Check course ratings and reviews before enrolling")
    print("   • Consider your schedule when choosing course duration")
    print("   • All courses are AI-generated based on your interests!")

    print("\n🚀 Happy Learning!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        print("❌ Web interface is not available. Use terminal mode instead.")
        print("� Run: python ai_course_recommender.py")
    else:
        # Run command line interface
        main()
