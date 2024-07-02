import pandas as pd
import re
from collections import Counter


def still_has_questions(df, question_index: int):
    return question_index < len(df)


def get_next(df, question_index):
    current_question = df.loc[question_index]
    return {'question': current_question['question'],
            'incorrect': current_question['incorrect'],
            'correct': current_question['correct']}


def check_answer(correct_clean, user_ans):
    counter_correct = Counter(correct_clean)
    # print(counter_correct)
    counter_user = Counter(user_ans)
    # print(counter_user)
    return counter_user == counter_correct
