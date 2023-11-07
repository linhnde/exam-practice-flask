import os
import random

from modules.data import *
from modules.quiz_brain import *
from flask import Flask, render_template, request, redirect, url_for, session

exam_list = [filename[:-9] for filename in os.listdir('data')]
ace_bank = compose_data("ace").copy()
pca_bank = compose_data("pca").copy()
exam_library = {'ace': ace_bank,
                'pca': pca_bank}

app = Flask(__name__)
app.secret_key = 'i12637812hd8172dyi12937'


def reset_progress():
    if not session.get('exam_name'):
        session['exam_name'] = 'pca'
    session['question_index'] = 0
    session['q_text'] = ""
    session['a_text_clean'] = []
    session['incorrect_clean'] = []
    session['correct_clean'] = []
    session['score'] = 0
    session['failed_list'] = []
    session['template_name'] = ""


@app.route('/')
def homepage():
    if not session.get('started'):
        session['started'] = True
        reset_progress()
        return redirect(url_for('next_question'))
    return redirect(url_for('quiz'))


@app.route('/exam', methods=['GET', 'POST'])
def select_exam():
    if request.method == 'POST':
        session['started'] = False
        session['exam_name'] = request.form.get('select_exam')
    return redirect(url_for('homepage'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'GET':
        return render_template(f'{session["template_name"]}.html',
                               exam_list=exam_list,
                               exam_name=session['exam_name'],
                               question=session['q_text'],
                               answers=session['a_text_clean'],
                               correct=session['correct_clean'])
    if len(session['correct_clean']) == 1:
        choice = [request.form.get('answer')]
    else:
        choice = [request.form.get(f'answer{i}') for i in range(len(session['a_text_clean']))
                  if request.form.get(f'answer{i}') is not None]
    checked = "checked" if [request.form.get('answer')] else ""
    disabled = "disabled" if checked else ""
    is_right = check_answer(session['question_index'], session['correct_clean'], choice,
                            session['score'], session['failed_list'])
    if is_right:
        session['score'] += 1
    else:
        session['failed_list'].append(session['question_index'])
    print(session['question_index'])
    print(session['score'])
    print(session['failed_list'])
    session['question_index'] += 1
    return render_template(f'{session["template_name"]}.html',
                           exam_list=exam_list,
                           exam_name=session['exam_name'],
                           question=session['q_text'],
                           answers=session['a_text_clean'],
                           correct=session['correct_clean'],
                           choice=choice,
                           is_right=is_right,
                           checked=checked,
                           disabled=disabled)


@app.route('/next', methods=['GET'])
def next_question():
    q_bank = exam_library[session['exam_name']]
    if still_has_questions(q_bank, session['question_index']):
        new_q = get_next(q_bank, session['question_index'])
        session['q_text'] = new_q['question']
        session['incorrect_clean'] = [text for text in new_q['incorrect'] if text == text]
        session['correct_clean'] = [text for text in new_q['correct'] if text == text]
        session['a_text_clean'] = session['incorrect_clean'] + session['correct_clean']
        if len(session['correct_clean']) == 1:
            session['template_name'] = "single_choice"
        else:
            session['template_name'] = "multi_choice"
        random.shuffle(session['a_text_clean'])
        return redirect(url_for('quiz'))
    else:
        return redirect(url_for('finish'))


@app.route('/export')
def export():
    q_bank = exam_library[session['exam_name']]
    failed_bank = q_bank.iloc[session['failed_list']]
    filename = f'data/failed_{session["exam_name"]}_bank.csv'
    failed_bank.to_csv(filename, mode='w', index=False)
    return redirect(url_for('homepage'))


@app.route('/finish')
def finish():
    score = session['score']
    bank_size = len(ace_bank) if session['exam_name'] == 'ace' else len(pca_bank)
    percent = round(score / bank_size * 100)
    return render_template('finish.html',
                           score=score,
                           size=bank_size,
                           percent=percent)


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
