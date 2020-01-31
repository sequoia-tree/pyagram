import * as Editor from './editor.js';
import * as Overlay from './overlay.js';
import * as Pyagram from './pyagram.js';
import * as Split from './split.js';

const SPLIT_PANEL_INPUT_ID = 'split-input-output-split-panel-input';
const SPLIT_PANEL_OUTPUT_ID = 'split-input-output-split-panel-output';
const SPLIT_PANEL_PYAGRAM_ID = 'split-pyagram-print-output-split-panel-pyagram';
const SPLIT_PANEL_PRINT_OUTPUT_ID = 'split-pyagram-print-output-split-panel-print-output';
const EDITOR_ID = 'editor';
const OUTPUT_OVERLAY_ID = 'overlay-output-overlay';
const DRAW_PYAGRAM_BUTTON_ID = 'button-draw-pyagram';
const NUM_LINES = 30;

Split.split(
    'horizontal',
    [
        SPLIT_PANEL_INPUT_ID,
        SPLIT_PANEL_OUTPUT_ID,
    ],
    [
        50,
        50,
    ],
    [
        15, // TODO: Change, perhaps to 0?
        15, // TODO: Change, perhaps to 0?
    ],
);

Split.split(
    'vertical',
    [
        SPLIT_PANEL_PYAGRAM_ID,
        SPLIT_PANEL_PRINT_OUTPUT_ID,
    ],
    [
        80,
        20,
    ],
    [
        15, // TODO: Change, perhaps to 0?
        15, // TODO: Change, perhaps to 0?
    ],
);

var editor = Editor.editor(EDITOR_ID, NUM_LINES);
var outputOverlay = document.getElementById(OUTPUT_OVERLAY_ID);
var drawPyagramButton = document.getElementById(DRAW_PYAGRAM_BUTTON_ID);

editor.session.on('change', function(delta) {
    Overlay.setTop(outputOverlay);
});

drawPyagramButton.onclick = function() {
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
            success: function(pyagram) {
                Pyagram.drawPyagram(pyagram);
                Overlay.setBottom(outputOverlay);
            },
        });
    }
};

editor.focus();
