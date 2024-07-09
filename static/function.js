function enable_single(enabled) {
    var submit = document.getElementById('ans_submit');
    if (enabled) {
        submit.removeAttribute('disabled');
    } else {
        submit.setAttribute('disabled','disabled');
    }
}

function enable_multi(num) {
    var form = document.getElementById('quiz_form'),
        submit = document.getElementById('ans_submit'),
        checked_num = form.querySelectorAll(':checked').length,
        enabled = (num === checked_num);
    if (enabled) {
        submit.removeAttribute('disabled');
    } else {
        submit.setAttribute('disabled','disabled');
    }
}