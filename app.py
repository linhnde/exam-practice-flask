import random
from google.cloud import storage
from flask import Flask, render_template, request, redirect, url_for, session
from modules.data import *
from modules.quiz_brain import *


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_credentials/exam-practice-404408-22a26d6c4fff.json'
bucket = "exam-banks"


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    # bucket_name = "your-bucket-name"
    storage_client = storage.Client()

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    # Note: The call returns a response only when the iterator is consumed.
    file_list = [blob.name for blob in blobs]
    # print(file_list)
    return file_list


exam_list = []
exam_library = {}

app = Flask(__name__)
app.secret_key = 'i12637812hd8172dyi12937'


def load_exam():
    global exam_list, exam_library
    file_list = list_blobs(bucket)
    exam_list = [filename[:-9] for filename in file_list]
    exam_library = {exam: compose_data(exam).copy() for exam in exam_list}


def reset_progress():
    session['started'] = True
    if not session.get('exam_name'):
        session['exam_name'] = 'pde'
    session['question_index'] = []
    session['turn'] = 0
    session['q_text'] = ""
    session['a_text_clean'] = []
    session['incorrect_clean'] = []
    session['correct_clean'] = []
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
                               question=session['q_text'],
                               answers=session['a_text_clean'],
                               correct=session['correct_clean'],
                               go_next=False,
                               for_export=not (session['failed_list'] == []))
    if len(session['correct_clean']) == 1:
        choice = [request.form.get('answer').replace('\r', '')]
        # print(choice)
    else:
        choice = [request.form.get(f'answer{i}').replace('\r', '') for i in range(len(session['a_text_clean']))
                  if request.form.get(f'answer{i}') is not None]
    checked = "checked" if [request.form.get('answer')] else ""
    disabled = "disabled" if checked else ""
    is_right = check_answer(session['correct_clean'], choice)
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
                           question=session['q_text'],
                           answers=session['a_text_clean'],
                           correct=session['correct_clean'],
                           choice=choice,
                           checked=checked,
                           disabled=disabled,
                           go_next=True,
                           for_export=not (session['failed_list'] == []))


@app.route('/next', methods=['GET'])
def next_question():
    q_bank = exam_library[session['exam_name']]
    if session['turn'] == 0:
        session['question_index'] = q_bank.index.values.tolist()
        random.shuffle(session['question_index'])
    if still_has_questions(q_bank, session['turn']):
        new_q = get_next(q_bank, session['question_index'][session['turn']])
        session['q_text'] = (f"Question {session['turn'] + 1}\n"
                             f"{new_q['question']}")
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
        session['finish'] = True
        return redirect(url_for('finish'))


@app.route('/export')
def export():
    q_bank = exam_library[session['exam_name']]
    failed_bank = q_bank.iloc[session['failed_list']]
    filename = f'failed_{session["exam_name"]}_bank.csv'
    failed_bank.to_csv(f"gs://{bucket}/{filename}", index=False)
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
