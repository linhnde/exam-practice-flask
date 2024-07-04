import pandas as pd
import re
from collections import Counter
from modules.data_load import *


def load_bucket(bucket):
    e_list = []
    e_library = {}
    file_list = list_blobs(bucket)
    for full_name in file_list:
        if full_name.split('.')[-1] == 'json':
            exam_name = extract_exam_name(full_name)
            e_list.append(exam_name)
            e_library[exam_name] = compose_data(bucket, full_name).copy()
    return {'e_list': e_list,
            'e_library': e_library}


def has_next(df, question_index):
    return question_index < len(df)


def load_next(df, question_index, turn):
    current_question = df.loc[question_index]
    q_text = f"Question {turn + 1}\n" \
             f"{current_question['question']}"
    all_choices = current_question['correct'] + current_question['incorrect']
    template_name = "single_choice" if len(current_question['correct']) == 1 else "multi_choice"
    return {'q_text': q_text,
            'correct': current_question['correct'],
            'all_choices': all_choices,
            'template_name': template_name}


def check_answer(correct_clean, user_ans):
    counter_correct = Counter(correct_clean)
    # print(counter_correct)
    counter_user = Counter(user_ans)
    # print(counter_user)
    return counter_user == counter_correct
