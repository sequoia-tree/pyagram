import * as Editor from './editor.js';
import * as Overlay from './overlay.js';
import * as Pyagram from './pyagram.js';
import * as Slider from './slider.js';
import * as Split from './split.js';

const SPLIT_PANEL_INPUT_ID = 'split-input-output-split-panel-input';
const SPLIT_PANEL_OUTPUT_ID = 'split-input-output-split-panel-output';
const SPLIT_PANEL_PYAGRAM_ID = 'split-pyagram-print-output-split-panel-pyagram';
const SPLIT_PANEL_PRINT_OUTPUT_ID = 'split-pyagram-print-output-split-panel-print-output';
const EDITOR_ID = 'editor';
const SLIDER_ID = 'slider-snapshot-slider';
const SLIDER_LABEL_ID = 'slider-snapshot-slider-label';
const SLIDER_L_BUTTON_ID = 'slider-snapshot-slider-button-l';
const SLIDER_R_BUTTON_ID = 'slider-snapshot-slider-button-r';
const OUTPUT_OVERLAY_ID = 'overlay-output-overlay';
const DRAW_PYAGRAM_BUTTON_ID = 'button-draw-pyagram';
const PYAGRAM_ID = 'pyagram';
const PRINT_OUTPUT_ID = 'print-output';
const PYAGRAM_STATE_TABLE_ID = 'pyagram-state-table';
const PYAGRAM_SVG_CANVAS_ID = 'pyagram-svg-canvas';
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
var slider = document.getElementById(SLIDER_ID);
var sliderLabel = document.getElementById(SLIDER_LABEL_ID);
var sliderButtonL = document.getElementById(SLIDER_L_BUTTON_ID);
var sliderButtonR = document.getElementById(SLIDER_R_BUTTON_ID);
var outputOverlay = document.getElementById(OUTPUT_OVERLAY_ID);
var drawPyagramButton = document.getElementById(DRAW_PYAGRAM_BUTTON_ID);
var pyagram = document.getElementById(PYAGRAM_ID);
var printOutput = document.getElementById(PRINT_OUTPUT_ID);

editor.session.on('change', function(delta) {
    Overlay.setTop(outputOverlay);
});

Slider.initializeSlider(slider, sliderLabel, sliderButtonL, sliderButtonR, function(newValue) {
    Pyagram.drawSnapshot(newValue, pyagram, printOutput, PYAGRAM_STATE_TABLE_ID, PYAGRAM_SVG_CANVAS_ID);
});

drawPyagramButton.onclick = function() {
    var code = editor.session.getValue();
    if (code === '') {
        alert('First write some code that you want to visualize.');
    } else {
        $.ajax({
            type: 'GET',
            url: '/draw',
            data: {
                'code': code,
            },
            contentType: 'application/json',
            dataType: 'json',
            success: function(pyagram) {
                Pyagram.drawPyagram(slider, pyagram);
                Overlay.setBottom(outputOverlay);
            },
        });
    }
};

editor.focus();
