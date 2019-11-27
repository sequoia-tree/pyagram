import ace from 'ace-builds';
import 'ace-builds/webpack-resolver';

const NUM_LINES = 30;

var editor = ace.edit(null, {
    mode: 'ace/mode/python',
    theme: 'ace/theme/merbivore_soft', // TODO: Support One Dark (from Atom), Monokai (from Sublime), and Merbivore Soft (from IDEA).
    fontFamily: 'PT Mono',
    fontSize: '100%',
    minLines: NUM_LINES,
    maxLines: NUM_LINES,
})
var overlay = document.getElementById('editor-overlay');
var button = document.getElementById('editor-button');

editor.session.on('change', function(delta) {
    overlay.style.display = 'block';
});

button.onclick = function() {
    var code = editor.session.getValue();
    $.ajax({
        type: 'GET',
        url: '/draw',
        data: {'code': code},
        contentType: 'application/json',
        dataType: 'json',
        success: function(response) {
            alert(JSON.stringify(response)); // TODO
        }
    });
}

document.getElementById('editor').appendChild(editor.container);
editor.focus();
