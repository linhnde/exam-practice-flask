# Import packages
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session

# Import functions in modules
from modules.data_load import *
from modules.quiz_brain import *

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials/load-quiz-bank.json'
BUCKET = "exam-banks"

exam_list = []
exam_library = {}

app = Flask(__name__)
app.secret_key = 'i12637812hd8172dyi12937'


def load_exam():
    global exam_list, exam_library
    temp = load_bucket(BUCKET)
    exam_list = temp['e_list']
    exam_library = temp['e_library']
    # print(exam_list)


def reset_progress():
    session['started'] = True
    if not session.get('exam_name'):
        session['exam_name'] = exam_list[0]
    session['question_index'] = []
    session['turn'] = 0
    session['q_text'] = ""
    session['all_choices'] = []
    session['correct'] = []
    session['score'] = 0
    session['failed_list'] = []
    session['template_name'] = ""
    session['finish'] = False


@app.route('/')
def homepage():
    if not session.get('started'):
        reset_progress()
        return redirect(url_for('next_question'))
    if session['finish']:
        return redirect(url_for('finish'))
    return redirect(url_for('quiz'))


@app.route('/exam', methods=['GET', 'POST'])
def select_exam():
    if request.method == 'POST':
        session.pop('started', None)
        session['exam_name'] = request.form.get('select_exam')
    return redirect(url_for('homepage'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # print(session['q_text'])
    current_q_num = int(session['q_text'].split('\n')[0].split()[-1])
    # print(f'Q num: {current_q_num}')
    if current_q_num <= session['turn']:
        session['turn'] = current_q_num - 1
    if request.method == 'GET':
        # print(f"Current turn: {session['turn']}")
        return render_template(f'{session["template_name"]}.html',
                               exam_list=exam_list,
                               exam_name=session['exam_name'],
                               q_text=session['q_text'],
                               all_choices=session['all_choices'],
                               correct=session['correct'],
                               go_next=False,
                               for_export=not (session['failed_list'] == []))
    if len(session['correct']) == 1:
        choice = [request.form.get('answer').replace('\r', '')]
        # print(choice)
    else:
        choice = [request.form.get(f'answer{i}').replace('\r', '') for i in range(len(session['all_choices']))
                  if request.form.get(f'answer{i}') is not None]
    checked = "checked" if [request.form.get('answer')] else ""
    disabled = "disabled" if checked else ""
    is_right = check_answer(session['correct'], choice)
    if is_right:
        session['score'] += 1
    else:
        # print(session['question_index'])
        # print(session['turn'])
        # print(session['question_index'][session['turn']])
        failed_id = session['question_index'][session['turn']]
        if failed_id not in session['failed_list']:
            session['failed_list'].append(failed_id)
        print(session['failed_list'])
    session['turn'] += 1
    # print(session['turn'])
    return render_template(f'{session["template_name"]}.html',
                           exam_list=exam_list,
                           exam_name=session['exam_name'],
                           q_num=session['turn'] + 1,
                           q_text=session['q_text'],
                           all_choices=session['all_choices'],
                           correct=session['correct'],
                           choice=choice,
                           checked=checked,
                           disabled=disabled,
                           go_next=True,
                           for_export=not (session['failed_list'] == []))


@app.route('/next', methods=['GET'])
def next_question():
    q_bank = exam_library[session['exam_name']]
    if session['turn'] == 0:
        # Extract indices of quiz set to list
        session['question_index'] = q_bank.index.values.tolist()
        # Shuffle the indices list to randomize quiz
        random.shuffle(session['question_index'])
    if has_next(q_bank, session['turn']):
        # Pick next quiz, use `turn` to pick in quiz indices list
        next_q_index = session['question_index'][session['turn']]
        new_q = load_next(q_bank, next_q_index, session['turn'])
        # Assign session variables to new values
        session['q_text'] = new_q['q_text']
        session['correct'] = new_q['correct']
        session['all_choices'] = new_q['all_choices']
        session['template_name'] = new_q['template_name']
        # Shuffle order of choices
        random.shuffle(session['all_choices'])
        return redirect(url_for('quiz'))
    session['finish'] = True
    return redirect(url_for('finish'))


@app.route('/export')
def export():
    q_bank = exam_library[session['exam_name']]
    failed_bank = q_bank.loc[session['failed_list']]
    size = len(session['failed_list'])
    filename = combine_file_name(session["exam_name"], size)
    failed_bank.to_json(f"gs://{BUCKET}/{filename}")
    load_exam()
    return redirect(url_for('homepage'))


@app.route('/finish')
def finish():
    score = session['score']
    question_completed = session['turn']
    bank_size = len(session['question_index'])
    percent = round(score / question_completed * 100)
    return render_template('finish.html',
                           score=score,
                           question_completed=question_completed,
                           size=bank_size,
                           percent=percent,
                           for_export=not (session['failed_list'] == []))


if __name__ == '__main__':
    load_exam()
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=True, port=server_port, host='0.0.0.0')
