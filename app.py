# Import packages
import os
import random
from flask import Flask, render_template, request, redirect, url_for, session

# Import necessary modules
from modules.quiz_brain import *

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials/load-quiz-bank.json'
BUCKET = "exam-banks"

# Use global variables to store list of exam names and corresponding datasets
exam_list = []
exam_library = {}

app = Flask(__name__, instance_relative_config=True)
# Default value during development
app.secret_key = 'dev'
# Overridden if this file exists in the instance folder
app.config.from_pyfile('config.py')


def collect_choice(correct_list):
    """
    Check current type of question, and collect list of choice(s) from POST request
    """
    if len(correct_list) == 1:
        # Strip '\r' from html render for proper comparing with `correct` set
        choice_list = [request.form.get('answer').replace('\r', '')]
    else:
        # Only load value if it's not empty
        choice_list = [request.form.get(f'answer{i}').replace('\r', '') for i in range(len(session['all_choices']))
                       if request.form.get(f'answer{i}') is not None]
    return choice_list


def load_exam():
    """
    By calling load_bucket(), files list from our bucket is updated
    Assigned those new data to current `exam_list` and `exam_library`
    """
    # Adjust value of global variables
    global exam_list, exam_library
    b_load = load_bucket(BUCKET)
    exam_list = b_load['e_list']
    exam_library = b_load['e_library']


def reset_progress():
    """
    Reset every session variables
    """
    session['started'] = True
    # Set default exam name to load
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
    # If `started` is empty (or popped), reset_process() will be called
    if not session.get('started'):
        reset_progress()
        return redirect(url_for('next_question'))
    if session['finish']:
        return redirect(url_for('finish'))
    return redirect(url_for('quiz'))


@app.route('/exam', methods=['GET', 'POST'])
def select_exam():
    if request.method == 'POST':
        # Pop value of `started` so that reset_progress() would trigger when homepage() load
        session.pop('started', None)
        session['exam_name'] = request.form.get('select_exam')
    return redirect(url_for('homepage'))


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """
    Render page to display one single question
    Arguments for render_template:
    - exam_list, exam_name: use to display drop menu of all available exams
    - q_text, all_choices, correct
    """
    template_file = f'{session["template_name"]}.html'
    # Extract current quiz number from `q_text`
    current_q_num = int(session['q_text'].split('\n')[0].split()[-1])

    # Match `turn` with `current_q_num` in case of loading defect
    if session['turn'] >= current_q_num:
        session['turn'] = current_q_num - 1

    # Process for GET request
    if request.method == 'GET':
        return render_template(template_file,
                               exam_list=exam_list,
                               exam_name=session['exam_name'],
                               q_text=session['q_text'],
                               all_choices=session['all_choices'],
                               correct=session['correct'],
                               go_next=False,
                               for_export=not (session['failed_list'] == []))

    # Collect selected choice(s)
    choice = collect_choice(session['correct'])

    # Flag form id `quiz_form` if POST request
    is_submitted = "submitted" if [request.form.get('answer')] else ""

    # Flag in HTML attribute to disable choices
    disabled = "disabled" if is_submitted else ""

    is_right = check_answer(session['correct'], choice)
    if is_right:
        # Increase score if right
        session['score'] += 1
    else:
        # Record the failed question
        failed_id = session['question_index'][session['turn']]

        # Append to the failed list if not duplicated
        if failed_id not in session['failed_list']:
            session['failed_list'].append(failed_id)

    session['turn'] += 1
    return render_template(template_file,
                           exam_list=exam_list,
                           exam_name=session['exam_name'],
                           q_num=session['turn'] + 1,
                           q_text=session['q_text'],
                           all_choices=session['all_choices'],
                           correct=session['correct'],
                           choice=choice,
                           is_submitted=is_submitted,
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
