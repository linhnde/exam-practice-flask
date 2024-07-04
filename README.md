## Table of contents

1. [Introduction](#introduction)
2. [Folder structure](#folder-structure)
3. [Features](#features)

## Introduction

Simulating a demand for practicing on certain quiz set, I create this web app, Exam Practice (EP).

Originally, the app was built on Tkinter. But later I adapted it on Flask to take advantages of responsive designing.

Using Google Cloud Run for deploying, we can save expense significantly in the early stage 
as we don't have to worry about 24/7 uptime bill.

Google Cloud Run also makes it easy to scale up the infrastructures if we need.

## Folder structure

`app.py` is the engine of the app where we declare and call the main functions.

`modules` folder stores modules support the main engine: 
* `data_load.py` includes functions help with listing Google Cloud Storage blobs, read data from files and compose into dataframes. 
* `quiz_brain.py` 
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

### Session based authentication

```
def reset_progress():
    session['started'] = True
    if not session.get('exam_name'):
        session['exam_name'] = exam_list[0]
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
```

### Load quiz set available in bucket

### Automatically shuffle choices to randomize answers pattern

### Adaptive layout for single-choice and multiple-choices question

### Record score for tracking performance

### Record fail list and export for further practice

