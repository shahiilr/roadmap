from ai_course_recommender import recommend_courses

print('Testing AI course recommendations...')
courses = recommend_courses('Machine Learning', 'Python', 'Data Scientist')
print(f'Generated {len(courses)} courses successfully!')

for i, course in enumerate(courses[:3], 1):
    print(f'{i}. {course.get("title", "Unknown")} - {course.get("platform", "Unknown")}')

print('\nTest completed!')
