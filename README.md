## Table of contents

1. [Introduction](#introduction)
2. [Folder structure](#folder-structure)
3. [Features](#features)
   1. [Session based authentication](#1-session-based-authentication)
   2. [Load and update quiz sets from GCS bucket](#2-load-and-update-quiz-sets-from-gcs-bucket)
   3. [Automatically shuffle choices to randomize answers pattern](#3-automatically-shuffle-choices-to-randomize-answers-pattern)
   4. [Adaptive layout for single-choice and multiple-choices question](#4-adaptive-layout-for-single-choice-and-multiple-choices-question)
   5. [Record fail list and export for further practice](#5-record-fail-list-and-export-for-further-practice)
   6. [Record score for tracking performance](#6-record-score-for-tracking-performance)

## Introduction

Simulating a demand for practicing on certain quiz set, I create this web app, Exam Practice (EP).

Originally, app was built on Tkinter. But later I adapted it on Flask to take advantages of responsive designing.

Using Google Cloud Run for deploying, we can save expense significantly in the early stage 
as we don't have to worry about 24/7 uptime bill.

Google Cloud Run also makes it easy to scale up the infrastructures if we need.

## Folder structure

```
exam-practice-flask/
├── google_credentials/
│   └── credentials.json
├── modules/
│   ├── data_load.py
│   └── quiz_brain.py
├── static/
│   ├── function.js
│   └── style.css
├── templates/
│   ├── base.html
│   ├── finish.html
│   ├── multi_choice.html
│   └── single_choice.html
├── app.py
└── requirements.txt
```

## Features

### 1. Session based authentication

App currently uses session instead.

Session variables save states (`started`, `finish`) and progress information like `exam_name`, shuffled `question_index`, current `turn`, quiz data,
`score`, `failed_list` until user closes web browser tab running app.

After that, session is purged and will be reassigned by `reset_progress`.

```python
def reset_progress():
    """
    Reset every session variables.
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
```

### 2. Load and update quiz sets from GCS bucket

Quiz sets are loaded into app when server started and reassigned after failed exam list is exported.

```python
def load_exam(bucket):
    """
    By calling load_bucket(), files list from our bucket is updated.
    Assigned those new data to current global variables `exam_list` and `exam_library`.
    """
    # Adjust value of global variables. NOTE: Python global variable is not meant to module cross.
    global exam_list, exam_library
    bucket_data = load_bucket(bucket)
    exam_list = bucket_data['e_list']
    exam_library = bucket_data['e_library']
```

```python
@app.route('/export')
def export():
    ...
    load_exam(BUCKET)
    ...
```

```python
if __name__ == '__main__':
    load_exam(BUCKET)
    ...
```

### 3. Automatically shuffle choices to randomize answers pattern

As `exam_list` and `exam_library` is global variables, they can only be set as server connection is initiated, 
or occasionally when `load_exam()` is called to update exam list with new bucket items.

Therefore, app uses list of indices saved in session variable to manage how to load questions to users.

When user accesses app as new session, meaning `turn` zero, `question_index` will be generated from 
indices of corresponding quiz bank.

Then, these list of indices will be shuffled to make quiz order of every user
different from each other.

```python
def next_question():
    q_bank = exam_library[session['exam_name']]
    if session['turn'] == 0:
        session['question_index'] = q_bank.index.values.tolist()
        random.shuffle(session['question_index'])
```

### 4. Adaptive layout for single-choice and multiple-choices question

Depend on number of choice in `correct`, app will choose template to render on.

```python
def quiz():
    template_file = f'{session["template_name"]}.html'
    ...
    if request.method == 'GET':
        return render_template(template_file,
                               ...)
    ...
    # POST request
    return render_template(template_file,
                           ...)
```

Both `single_choice.html` and `multi_choice.html` are extended from `base.html`.

The only difference is in `input` tag where we declare `type`, `name` and `onclick` JavaScript function.

```html
`single_choice.html`

<input class="..." type="radio" name="answer" value="..." onclick="enable_single(true)" ...>
```

```html
`multi_choice.html`

<input class="..." type="checkbox" name="answer{{i}}" value="..." onclick="enable_multi({{correct|count}})" ...>
```

### 5. Record fail list and export for further practice

As the exam progresses, the questions which user failed are saved. Their indices will be appended into `failed_list`.

```python
def quiz():
    ...
    is_right = check_answer(session['correct'], choice)
    if is_right:
        session['score'] += 1
    else:
        failed_id = session['question_index'][session['turn']]
        if failed_id not in session['failed_list']:
            session['failed_list'].append(failed_id)
    ...
```

When `export()` is called, from `failed_list` it will load corresponding questions in library
and load the collected set to GCS. After that, `load_exam()` is called to update exam list in the menu.

```python
def export():
    export_gcs(exam_library=exam_library,
               exam_name=session['exam_name'],
               index_list=session['failed_list'],
               bucket=BUCKET)
    load_exam(BUCKET)
    return redirect(url_for('homepage'))
```

`export()` is also linked to `Export` button in exam list menu and in `finish` page.

The button is default disabled because of blank `failed_list`. It will be enabled as soon as
first failed question index is appended to the list.

```python
    def quiz():
        ...
        if request.method == 'GET':
            return render_template(...,
                                   for_export=not (session['failed_list'] == []))
        ...
        return render_template(...,
                               for_export=not (session['failed_list'] == []))
```

```python
    def finish():
        ...
        return render_template(...,
                               for_export=not (session['failed_list'] == []))
```

### 6. Record score for tracking performance

`score`, `turn` will be updated after each question being submitted. `finish()` derives other information and concludes.

`finish()` will be automatically called if there is no more question to load in `next_question()`.

`next_question()`, in this case, also flags session `finish` as `True` to redirect `homepage()` later.

```python
def finish():
    score = session['score']
    end_turn = session['turn']
    bank_size = len(session['question_index'])
    correct_percent = round(score / end_turn * 100)
    return render_template('finish.html',
                           score=score,
                           end_turn=end_turn,
                           size=bank_size,
                           correct_percent=correct_percent,
                           for_export=not (session['failed_list'] == []))
```

```python
def next_question():
    ...
    if is_finished(session['turn'], q_bank):
        session['finish'] = True
        return redirect(url_for('finish'))
    ...
```

```python
def homepage():
    ...
    if session['finish']:
        return redirect(url_for('finish'))
    ...
```


