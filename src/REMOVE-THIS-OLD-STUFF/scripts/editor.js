import ace from 'ace-builds';
import 'ace-builds/webpack-resolver';

export function newEditor(id, num_lines) {
    var editor = ace.edit(null, {
        mode: 'ace/mode/python',
        theme: 'ace/theme/merbivore_soft',
        fontFamily: 'PT Mono',
        fontSize: '100%',
        minLines: num_lines,
        maxLines: num_lines,
    });
    document.getElementById(id).appendChild(editor.container);
    return editor;
}

export function getEditorButton(id) {
    return document.getElementById(id.concat('-button'));
}
