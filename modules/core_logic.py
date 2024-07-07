from collections import Counter


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
