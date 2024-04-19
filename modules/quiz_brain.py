import pandas as pd
import re
from collections import Counter


def still_has_questions(df, question_index: int):
    return question_index < len(df)


def get_next(df, question_index):
    current_question = df.loc[question_index]
    q_text = current_question['question']

    incorrect_cols = [col for col in df.columns if re.search(r'^incorrect', col)]
    incorrect_ans = current_question[incorrect_cols].to_list()

    correct_cols = [col for col in df.columns if re.search(r'^correct', col)]
    correct_ans = current_question[correct_cols].to_list()

    full_question = {'question': q_text,
                     'incorrect': incorrect_ans,
                     'correct': correct_ans}
    return full_question


def check_answer(correct_clean, user_ans):
    counter_correct = Counter(correct_clean)
    # print(counter_correct)
    counter_user = Counter(user_ans)
    # print(counter_user)
    return counter_user == counter_correct

