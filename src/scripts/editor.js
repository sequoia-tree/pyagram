import ace from 'ace-builds';
import 'ace-builds/webpack-resolver';

export function editor(id, num_lines) {
    var editor = ace.edit(null, {
        mode: 'ace/mode/python',
        theme: 'ace/theme/merbivore_soft',
        fontFamily: 'Source Code Pro',
        fontSize: '100%',
        minLines: num_lines,
        maxLines: num_lines,
    });
    document.getElementById(id).appendChild(editor.container);
    return editor;
}
