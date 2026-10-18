from dataclasses import dataclass


@dataclass
class ExampleSentence:
    """
    Components of an example sentence
    """

    japanese: str
    translation: str
    explanation: str


@dataclass
class PracticeSentence:
    """
    Components of a practice sentence
    """

    english: str
    answers: list[str]
    explanation: str


@dataclass
class RespondingSentence:
    """
    Components of a Responding sentence
    a statement in Japanese,
    the context in English
    possible answers
    the explanation of how the grammar topic is used in the reference response
    """

    statement: str
    context: str
    answers: list[str]
    explanation: str


# get the reference answers:
def _ref_ans(example):
    ref = example.get("3 Reference Answers")
    if ref is None:
        ref = example["Reference Answers"]
    return ref


class Lesson:
    """
    A class of Lessons, that is made from a JSON
    """

    def __init__(self, lesson_json: dict, ix: str):
        self.ix: str = ix
        self.topic: str = self.try_get_topic(lesson_json)
        self.explanation: str = self.try_get_explanation(lesson_json)
        self.examples: list[ExampleSentence] = self.try_get_examples(lesson_json)
        self.practices: list[PracticeSentence] = self.try_get_practices(lesson_json)
        self.responding: list[RespondingSentence] = self.try_get_responding(lesson_json)

    # ______________________________________________________
    @staticmethod
    def try_get_topic(lesson_json: dict) -> str:
        """
        try to extract the topic from the json. probably raising a key error
        """
        return lesson_json["Lesson"]

    # ______________________________________________________
    @staticmethod
    def try_get_explanation(lesson_json: dict) -> str:
        """
        try to extract the topic from the json. probably raising a key error
        """
        return lesson_json["Explanation"]

    # ______________________________________________________
    @staticmethod
    def try_get_examples(lesson_json: dict) -> list[ExampleSentence]:
        """
        try to extract the examples from the json. probably raising a key error
        """
        return [
            ExampleSentence(
                example["Japanese"], example["Translation"], example["Explanation"]
            )
            for example in lesson_json["10 Example Sentences"]
        ]

    # ______________________________________________________
    @staticmethod
    def try_get_practices(lesson_json: dict) -> list[PracticeSentence]:
        """
        try to extract the practice_translations from the json. probably raising a key error
        """
        return [
            PracticeSentence(
                translation["English"],
                _ref_ans(translation),
                translation["Explanation"],
            )
            for translation in lesson_json["15 Practice Sentences"]
        ]

    # ______________________________________________________
    @staticmethod
    def try_get_responding(lesson_json: dict) -> list[RespondingSentence]:
        """
        try to extract the practice_responding from the json. probably raising a key error
        """
        return [
            RespondingSentence(
                responding["Respond-able statement"],
                responding["Context"],
                _ref_ans(responding),
                responding["Explanation"],
            )
            for responding in lesson_json["15 Japanese Response Sentences"]
        ]
