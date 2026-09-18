"""
Configuration settings for MCQ Runner
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
QUESTIONS_DIR = DATA_DIR / "questions"
PROGRESS_DIR = DATA_DIR / "user_progress"

# Create directories if they don't exist
for directory in [DATA_DIR, QUESTIONS_DIR, PROGRESS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Quiz settings
DEFAULT_QUESTIONS_PER_QUIZ = 10
TIME_LIMIT_PER_QUESTION = 60  # seconds (0 for no limit)
PASS_PERCENTAGE = 70

# Display settings
SHOW_EXPLANATION = True
SHOW_CORRECT_ANSWER_ON_WRONG = True

# Topics available
TOPICS = {
    "ml-basics": "Machine Learning Basics",
    "deep-learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "reinforcement-learning": "Reinforcement Learning",
    "statistics": "Statistics & Probability",
    "algorithms": "ML Algorithms",
    "evaluation": "Model Evaluation",
    "deployment": "Model Deployment",
    "mixed": "Mixed Topics"
}

# Difficulty levels
DIFFICULTY_LEVELS = ["easy", "medium", "hard"]

# Scoring
POINTS = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}

# Colors (for terminal output)
COLORS = {
    "correct": "green",
    "incorrect": "red",
    "warning": "yellow",
    "info": "cyan",
    "header": "magenta"
}
