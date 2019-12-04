import ace from 'ace-builds';
import 'ace-builds/webpack-resolver';

import { drawPyagram } from './draw.js';

const NUM_LINES = 30;

var editor = ace.edit(null, {
    mode: 'ace/mode/python',
    theme: 'ace/theme/merbivore_soft', // TODO: Support One Dark (Atom), Monokai (Sublime), and Merbivore Soft (IDEA).
    fontFamily: 'PT Mono',
    fontSize: '100%',
    minLines: NUM_LINES,
    maxLines: NUM_LINES,
});
var overlay = document.getElementById('editor-overlay');
var button = document.getElementById('editor-button');

editor.session.on('change', function(delta) {
    overlay.style.display = 'block';
});

button.onclick = function() {
    var code = editor.session.getValue();
    if (code === '') {
        alert('First write some code that you want to visualize.');
    } else {
        $.ajax({
            type: 'GET',
            url: '/draw',
            data: {'code': code},
            contentType: 'application/json',
            dataType: 'json',
            success: drawPyagram,
        });
        overlay.style.display = 'none';
    }
}

document.getElementById('editor').appendChild(editor.container);
editor.focus();
