# Professional AI Course Recommender & Learning Roadmap Generator

A comprehensive Python application that generates personalized course recommendations and visual learning roadmaps using AI.

## Features

- 🤖 AI-powered course recommendations (8 courses across beginner, intermediate, advanced levels)
- 🗺️ Professional 8-step learning roadmap visualization
- 🎨 Beautiful matplotlib-based roadmap graphics
- 📊 Career outcomes and salary information
- 🚀 Quick command-line interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shahiilr/roadmap.git
cd roadmap
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys (optional - see Usage section):
Create a `.env` file in the root directory (copy from `.env.example`):
```
cp .env.example .env
# Then edit .env and add your actual API keys
```

Get your API keys from: https://makersuite.google.com/app/apikey

## Usage

### Interactive Mode
```bash
python pro_int_courses.py
```

### Quick Mode
```bash
python pro_int_courses.py --quick "Machine Learning"
```

### Without API Keys
If you don't have Gemini API keys, the application will display a message with instructions to obtain them.

## Requirements

- Python 3.7+
- Google Gemini API keys (optional but recommended for full functionality)
- matplotlib
- numpy
- python-dotenv

## Output

The application generates:
- A visual roadmap image (PNG file)
- Detailed course recommendations
- 8-step learning progression
- Career guidance information

## License

MIT License - feel free to use and modify.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
