import hashlib
import json
from pathlib import Path

from lesson_structure import Lesson

BASE_DIR = Path(__file__).resolve().parent
LESSONS_FILE = BASE_DIR / "lessons.json"


def key_from_topic(topic: str) -> str:
    """Returns SHA-256 hash of whitespace-trimmed topic."""
    return hashlib.sha256(topic.strip().encode("utf-8")).hexdigest()

def read_lessons() -> dict:
    """Read in lessons.json."""
    if not LESSONS_FILE.exists():
        return {}
        
    with open(LESSONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def write_lessons(lessons:dict):
    """Write the lessons to lessons.json"""
    with open(LESSONS_FILE, "w") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)

def try_check_json(lesson_json: str, grammar_topic: str):
    """
    tests if the jason string has the correct attributes
    writes the lesson to lesson.json if it was correct

    Raises an error if the json isn't in the correct format
    """
    # checks both if it's valid json, and if it has the correct keys
    lesson = json.loads(lesson_json)
    # check if the main lesson was generated correctly
    Lesson.try_get_topic(lesson)
    Lesson.try_get_explanation(lesson)
    Lesson.try_get_examples(lesson)
    Lesson.try_get_practices(lesson)
    Lesson.try_get_responding(lesson)

    # if no errors were raised, then write the lesson to the file
    key = key_from_topic(grammar_topic)

    lessons = read_lessons()
    lessons[key] = lesson
    write_lessons(lessons)
