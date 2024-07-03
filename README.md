## Introduction

Simulating a demand for practicing on certain quiz set, I create this web app.

Originally, the app was built on Tkinter. But later I adapted it on Flask to take advantages of responsive designing.

Using Google Cloud Run and their flexible model for deploying, expense is saved significantly in the early stage.

I can freely share it with friends without worry much about 24/7 backend bill.
Considering further use with public access, Google Cloud Run also make it easily to scale up the infrastructures.

## Folder structure

```
exam-practice-flask/
├── google_credentials/
│   └── credentials.json
├── modules/
│   ├── data.py
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

### User-session based

### Load quiz set available in bucket

### Automatically shuffle choices to randomize answers pattern

### Adaptive layout for single-choice and multiple-choices question

### Record score for tracking performance

### Record fail list and export for further practice

