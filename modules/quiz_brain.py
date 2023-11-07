import pandas as pd
import re
from collections import Counter


def still_has_questions(df, question_index: int):
    return question_index < len(df) - 1


def get_next(df, question_index):
    current_question = df.iloc[question_index]
    q_text = current_question['question']
    display_question = (f"Question {question_index + 1}\n"
                        f"===\n"
                        f"{q_text}")

    incorrect_cols = [col for col in df.columns if re.search(r'^incorrect', col)]
    incorrect_ans = current_question[incorrect_cols].to_list()

    correct_cols = [col for col in df.columns if re.search(r'^correct', col)]
    correct_ans = current_question[correct_cols].to_list()

    full_question = {'question': display_question,
                     'incorrect': incorrect_ans,
                     'correct': correct_ans}
    return full_question


def check_answer(question_index, correct_clean, user_ans, score, failed_list):
    counter_correct = Counter(correct_clean)
    counter_user = Counter(user_ans)
    return counter_user == counter_correct

