import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import sqlite3
from pathlib import Path

class CourseDataStore:
    """
    A data storage system for managing course recommendations and user data.
    Supports both JSON file storage and SQLite database storage.
    """

    def __init__(self, storage_type: str = "json", data_dir: str = "data"):
        """
        Initialize the data store.

        Args:
            storage_type: "json" for file-based storage, "sqlite" for database storage
            data_dir: Directory to store data files
        """
        self.storage_type = storage_type
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        if storage_type == "sqlite":
            self.db_path = self.data_dir / "course_recommendations.db"
            self._init_database()
        else:
            self.courses_file = self.data_dir / "courses.json"
            self.users_file = self.data_dir / "users.json"
            self.recommendations_file = self.data_dir / "recommendations.json"

    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create courses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    platform TEXT,
                    instructor TEXT,
                    duration TEXT,
                    difficulty TEXT,
                    rating REAL,
                    price TEXT,
                    description TEXT,
                    skills_gained TEXT,  -- JSON string
                    url TEXT,
                    level TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interests TEXT,
                    current_skills TEXT,
                    career_goals TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    course_id INTEGER,
                    recommendation_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (course_id) REFERENCES courses (id)
                )
            ''')

            conn.commit()

    def save_course(self, course_data: Dict[str, Any]) -> int:
        """
        Save a course to the data store.

        Args:
            course_data: Dictionary containing course information

        Returns:
            Course ID if using database, or 0 for file storage
        """
        if self.storage_type == "sqlite":
            return self._save_course_sqlite(course_data)
        else:
            return self._save_course_json(course_data)

    def _save_course_sqlite(self, course_data: Dict[str, Any]) -> int:
        """Save course to SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO courses
                (title, platform, instructor, duration, difficulty, rating, price,
                 description, skills_gained, url, level, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                course_data.get('title'),
                course_data.get('platform'),
                course_data.get('instructor'),
                course_data.get('duration'),
                course_data.get('difficulty'),
                course_data.get('rating'),
                course_data.get('price'),
                course_data.get('description'),
                json.dumps(course_data.get('skills_gained', [])),
                course_data.get('url'),
                course_data.get('level'),
                course_data.get('source', 'AI Generated')
            ))

            course_id = cursor.lastrowid
            conn.commit()
            return course_id

    def _save_course_json(self, course_data: Dict[str, Any]) -> int:
        """Save course to JSON file."""
        courses = self._load_json_file(self.courses_file)
        course_id = len(courses) + 1
        course_data['id'] = course_id
        course_data['created_at'] = datetime.now().isoformat()
        courses.append(course_data)
        self._save_json_file(self.courses_file, courses)
        return course_id

    def save_user_profile(self, user_data: Dict[str, Any]) -> int:
        """
        Save user profile to the data store.

        Args:
            user_data: Dictionary containing user information

        Returns:
            User ID
        """
        if self.storage_type == "sqlite":
            return self._save_user_sqlite(user_data)
        else:
            return self._save_user_json(user_data)

    def _save_user_sqlite(self, user_data: Dict[str, Any]) -> int:
        """Save user to SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO users (interests, current_skills, career_goals)
                VALUES (?, ?, ?)
            ''', (
                user_data.get('interests'),
                user_data.get('current_skills'),
                user_data.get('career_goals')
            ))

            user_id = cursor.lastrowid
            conn.commit()
            return user_id

    def _save_user_json(self, user_data: Dict[str, Any]) -> int:
        """Save user to JSON file."""
        users = self._load_json_file(self.users_file)
        user_id = len(users) + 1
        user_data['id'] = user_id
        user_data['created_at'] = datetime.now().isoformat()
        users.append(user_data)
        self._save_json_file(self.users_file, users)
        return user_id

    def save_recommendation(self, user_id: int, course_id: int, score: float = 1.0):
        """
        Save a course recommendation for a user.

        Args:
            user_id: ID of the user
            course_id: ID of the recommended course
            score: Recommendation score (0-1)
        """
        if self.storage_type == "sqlite":
            self._save_recommendation_sqlite(user_id, course_id, score)
        else:
            self._save_recommendation_json(user_id, course_id, score)

    def _save_recommendation_sqlite(self, user_id: int, course_id: int, score: float):
        """Save recommendation to SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO recommendations (user_id, course_id, recommendation_score)
                VALUES (?, ?, ?)
            ''', (user_id, course_id, score))

            conn.commit()

    def _save_recommendation_json(self, user_id: int, course_id: int, score: float):
        """Save recommendation to JSON file."""
        recommendations = self._load_json_file(self.recommendations_file)
        rec_data = {
            'id': len(recommendations) + 1,
            'user_id': user_id,
            'course_id': course_id,
            'recommendation_score': score,
            'created_at': datetime.now().isoformat()
        }
        recommendations.append(rec_data)
        self._save_json_file(self.recommendations_file, recommendations)

    def get_courses(self, limit: Optional[int] = None, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve courses from the data store.

        Args:
            limit: Maximum number of courses to return
            level: Filter by difficulty level (beginner/intermediate/advanced)

        Returns:
            List of course dictionaries
        """
        if self.storage_type == "sqlite":
            return self._get_courses_sqlite(limit, level)
        else:
            return self._get_courses_json(limit, level)

    def _get_courses_sqlite(self, limit: Optional[int], level: Optional[str]) -> List[Dict[str, Any]]:
        """Get courses from SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM courses"
            params = []

            if level:
                query += " WHERE level = ?"
                params.append(level.lower())

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert to dictionaries
            courses = []
            for row in rows:
                course = {
                    'id': row[0],
                    'title': row[1],
                    'platform': row[2],
                    'instructor': row[3],
                    'duration': row[4],
                    'difficulty': row[5],
                    'rating': row[6],
                    'price': row[7],
                    'description': row[8],
                    'skills_gained': json.loads(row[9]) if row[9] else [],
                    'url': row[10],
                    'level': row[11],
                    'source': row[12],
                    'created_at': row[13]
                }
                courses.append(course)

            return courses

    def _get_courses_json(self, limit: Optional[int], level: Optional[str]) -> List[Dict[str, Any]]:
        """Get courses from JSON file."""
        courses = self._load_json_file(self.courses_file)

        if level:
            courses = [c for c in courses if c.get('level', '').lower() == level.lower()]

        if limit:
            courses = courses[:limit]

        return courses

    def get_user_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get recommendations for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List of recommended courses with recommendation data
        """
        if self.storage_type == "sqlite":
            return self._get_user_recommendations_sqlite(user_id)
        else:
            return self._get_user_recommendations_json(user_id)

    def _get_user_recommendations_sqlite(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user recommendations from SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT c.*, r.recommendation_score, r.created_at as recommended_at
                FROM courses c
                JOIN recommendations r ON c.id = r.course_id
                WHERE r.user_id = ?
                ORDER BY r.recommendation_score DESC, r.created_at DESC
            ''', (user_id,))

            rows = cursor.fetchall()
            recommendations = []

            for row in rows:
                course = {
                    'id': row[0],
                    'title': row[1],
                    'platform': row[2],
                    'instructor': row[3],
                    'duration': row[4],
                    'difficulty': row[5],
                    'rating': row[6],
                    'price': row[7],
                    'description': row[8],
                    'skills_gained': json.loads(row[9]) if row[9] else [],
                    'url': row[10],
                    'level': row[11],
                    'source': row[12],
                    'created_at': row[13],
                    'recommendation_score': row[14],
                    'recommended_at': row[15]
                }
                recommendations.append(course)

            return recommendations

    def _get_user_recommendations_json(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user recommendations from JSON files."""
        recommendations_data = self._load_json_file(self.recommendations_file)
        courses = self._load_json_file(self.courses_file)

        # Create course lookup
        course_lookup = {c['id']: c for c in courses}

        user_recommendations = []
        for rec in recommendations_data:
            if rec['user_id'] == user_id:
                course = course_lookup.get(rec['course_id'])
                if course:
                    course_copy = course.copy()
                    course_copy['recommendation_score'] = rec['recommendation_score']
                    course_copy['recommended_at'] = rec['created_at']
                    user_recommendations.append(course_copy)

        return sorted(user_recommendations, key=lambda x: x['recommendation_score'], reverse=True)

    def search_courses(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search courses by title, description, or skills.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching courses
        """
        if self.storage_type == "sqlite":
            return self._search_courses_sqlite(query, limit)
        else:
            return self._search_courses_json(query, limit)

    def _search_courses_sqlite(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search courses in SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Search in title, description, and skills
            search_query = f"%{query}%"
            cursor.execute('''
                SELECT * FROM courses
                WHERE title LIKE ? OR description LIKE ? OR skills_gained LIKE ?
                ORDER BY rating DESC
                LIMIT ?
            ''', (search_query, search_query, search_query, limit))

            rows = cursor.fetchall()
            courses = []

            for row in rows:
                course = {
                    'id': row[0],
                    'title': row[1],
                    'platform': row[2],
                    'instructor': row[3],
                    'duration': row[4],
                    'difficulty': row[5],
                    'rating': row[6],
                    'price': row[7],
                    'description': row[8],
                    'skills_gained': json.loads(row[9]) if row[9] else [],
                    'url': row[10],
                    'level': row[11],
                    'source': row[12],
                    'created_at': row[13]
                }
                courses.append(course)

            return courses

    def _search_courses_json(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search courses in JSON files."""
        courses = self._load_json_file(self.courses_file)
        query_lower = query.lower()

        matching_courses = []
        for course in courses:
            # Search in title, description, and skills
            searchable_text = (
                course.get('title', '').lower() + ' ' +
                course.get('description', '').lower() + ' ' +
                ' '.join(course.get('skills_gained', [])).lower()
            )

            if query_lower in searchable_text:
                matching_courses.append(course)

        # Sort by rating and limit results
        matching_courses.sort(key=lambda x: x.get('rating', 0), reverse=True)
        return matching_courses[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the stored data.

        Returns:
            Dictionary with various statistics
        """
        if self.storage_type == "sqlite":
            return self._get_statistics_sqlite()
        else:
            return self._get_statistics_json()

    def _get_statistics_sqlite(self) -> Dict[str, Any]:
        """Get statistics from SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            stats = {}

            # Course statistics
            cursor.execute("SELECT COUNT(*) FROM courses")
            stats['total_courses'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM users")
            stats['total_users'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM recommendations")
            stats['total_recommendations'] = cursor.fetchone()[0]

            # Courses by level
            cursor.execute("SELECT level, COUNT(*) FROM courses GROUP BY level")
            level_counts = cursor.fetchall()
            stats['courses_by_level'] = dict(level_counts)

            # Average rating
            cursor.execute("SELECT AVG(rating) FROM courses WHERE rating IS NOT NULL")
            avg_rating = cursor.fetchone()[0]
            stats['average_rating'] = round(avg_rating, 2) if avg_rating else 0

            return stats

    def _get_statistics_json(self) -> Dict[str, Any]:
        """Get statistics from JSON files."""
        courses = self._load_json_file(self.courses_file)
        users = self._load_json_file(self.users_file)
        recommendations = self._load_json_file(self.recommendations_file)

        stats = {
            'total_courses': len(courses),
            'total_users': len(users),
            'total_recommendations': len(recommendations),
            'courses_by_level': {},
            'average_rating': 0
        }

        # Count courses by level
        for course in courses:
            level = course.get('level', 'unknown')
            stats['courses_by_level'][level] = stats['courses_by_level'].get(level, 0) + 1

        # Calculate average rating
        ratings = [c.get('rating', 0) for c in courses if c.get('rating')]
        if ratings:
            stats['average_rating'] = round(sum(ratings) / len(ratings), 2)

        return stats

    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from JSON file."""
        if not file_path.exists():
            return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_json_file(self, file_path: Path, data: List[Dict[str, Any]]):
        """Save data to JSON file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def export_data(self, export_path: str):
        """
        Export all data to a JSON file.

        Args:
            export_path: Path to export the data
        """
        if self.storage_type == "sqlite":
            data = {
                'courses': self._get_courses_sqlite(None, None),
                'users': self._get_all_users_sqlite(),
                'recommendations': self._get_all_recommendations_sqlite(),
                'exported_at': datetime.now().isoformat()
            }
        else:
            data = {
                'courses': self._load_json_file(self.courses_file),
                'users': self._load_json_file(self.users_file),
                'recommendations': self._load_json_file(self.recommendations_file),
                'exported_at': datetime.now().isoformat()
            }

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _get_all_users_sqlite(self) -> List[Dict[str, Any]]:
        """Get all users from SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()

            users = []
            for row in rows:
                user = {
                    'id': row[0],
                    'interests': row[1],
                    'current_skills': row[2],
                    'career_goals': row[3],
                    'created_at': row[4]
                }
                users.append(user)

            return users

    def _get_all_recommendations_sqlite(self) -> List[Dict[str, Any]]:
        """Get all recommendations from SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recommendations")
            rows = cursor.fetchall()

            recommendations = []
            for row in rows:
                rec = {
                    'id': row[0],
                    'user_id': row[1],
                    'course_id': row[2],
                    'recommendation_score': row[3],
                    'created_at': row[4]
                }
                recommendations.append(rec)

            return recommendations


# Example usage and testing
if __name__ == "__main__":
    # Initialize data store (choose 'json' or 'sqlite')
    store = CourseDataStore(storage_type="json")

    # Example: Save a course
    sample_course = {
        'title': 'Machine Learning with Python',
        'platform': 'Coursera',
        'instructor': 'Andrew Ng',
        'duration': '11 weeks',
        'difficulty': 'Intermediate',
        'rating': 4.8,
        'price': 'Free',
        'description': 'Learn machine learning fundamentals with Python',
        'skills_gained': ['Python', 'Machine Learning', 'Data Analysis'],
        'url': 'https://coursera.org/learn/machine-learning',
        'level': 'intermediate',
        'source': 'AI Generated'
    }

    course_id = store.save_course(sample_course)
    print(f"Saved course with ID: {course_id}")

    # Example: Save user profile
    user_profile = {
        'interests': 'Artificial Intelligence, Data Science',
        'current_skills': 'Python, Statistics',
        'career_goals': 'Data Scientist'
    }

    user_id = store.save_user_profile(user_profile)
    print(f"Saved user with ID: {user_id}")

    # Example: Save recommendation
    store.save_recommendation(user_id, course_id, 0.95)

    # Example: Get courses
    courses = store.get_courses(limit=5)
    print(f"Retrieved {len(courses)} courses")

    # Example: Search courses
    search_results = store.search_courses("Python", limit=3)
    print(f"Found {len(search_results)} courses matching 'Python'")

    # Example: Get statistics
    stats = store.get_statistics()
    print("Data Statistics:", stats)
