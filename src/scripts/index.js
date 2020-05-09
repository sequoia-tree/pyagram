import * as Editor from './editor.js';
import * as Overlay from './overlay.js';
import * as Pyagram from './pyagram.js';
import * as Slider from './slider.js';
import * as Split from './split.js';

const SPLIT_PANEL_INPUT_ID = 'split-input-output-split-panel-input';
const SPLIT_PANEL_OUTPUT_ID = 'split-input-output-split-panel-output';
const SPLIT_PANEL_PYAGRAM_ID = 'split-pyagram-print-output-split-panel-pyagram';
const SPLIT_PANEL_PRINT_OUTPUT_ID = 'split-pyagram-print-output-split-panel-print-output';
const SPLIT_PANEL_STACK_ID = 'split-stack-heap-split-panel-stack';
const SPLIT_PANEL_HEAP_ID = 'split-stack-heap-split-panel-heap';
const EDITOR_ID = 'editor';
const SLIDER_ID = 'slider-snapshot-slider';
const SLIDER_LABEL_ID = 'slider-snapshot-slider-label';
const SLIDER_L_BUTTON_ID = 'slider-snapshot-slider-button-l';
const SLIDER_R_BUTTON_ID = 'slider-snapshot-slider-button-r';
const VIS_OPTIONS_TEXT_POINTERS_ID = 'visualization-options-option-text-pointers';
const VIS_OPTIONS_HIDE_FLAGS_ID = 'visualization-options-option-hide-flags';
const OUTPUT_OVERLAY_ID = 'overlay-output-overlay';
const DRAW_PYAGRAM_BUTTON_ID = 'button-draw-pyagram';
const PYAGRAM_STACK_ID = 'pyagram-stack';
const PYAGRAM_HEAP_ID = 'pyagram-heap';
const PYAGRAM_EXCEPTION_ID = 'pyagram-exception';
const PRINT_OUTPUT_ID = 'print-output';
const PYAGRAM_STATE_TABLE_ID = 'pyagram-state-table';
const PYAGRAM_SVG_CANVAS_ID = 'pyagram-svg-canvas';
const DRAW_PYAGRAM_BUTTON_WAIT_TEXT = 'Drawing ...'
const NUM_LINES = 20;

Split.split(
    'horizontal',
    [
        SPLIT_PANEL_INPUT_ID,
        SPLIT_PANEL_OUTPUT_ID,
    ],
    [35, 65],
    [0, 0],
);

Split.split(
    'vertical',
    [
        SPLIT_PANEL_PYAGRAM_ID,
        SPLIT_PANEL_PRINT_OUTPUT_ID,
    ],
    [80, 20],
    [0, 0],
);

Split.split(
    'horizontal',
    [
        SPLIT_PANEL_STACK_ID,
        SPLIT_PANEL_HEAP_ID,
    ],
    [75, 25],
    [0, 0],
);

var editor = Editor.editor(EDITOR_ID, NUM_LINES);
var slider = document.getElementById(SLIDER_ID);
var sliderLabel = document.getElementById(SLIDER_LABEL_ID);
var sliderButtonL = document.getElementById(SLIDER_L_BUTTON_ID);
var sliderButtonR = document.getElementById(SLIDER_R_BUTTON_ID);
var visOptionsTextPointers = document.getElementById(VIS_OPTIONS_TEXT_POINTERS_ID);
var visOptionsHideFlags = document.getElementById(VIS_OPTIONS_HIDE_FLAGS_ID);
var outputOverlay = document.getElementById(OUTPUT_OVERLAY_ID);
var drawPyagramButton = document.getElementById(DRAW_PYAGRAM_BUTTON_ID);
var pyagramStack = document.getElementById(PYAGRAM_STACK_ID);
var pyagramHeap = document.getElementById(PYAGRAM_HEAP_ID);
var pyagramException = document.getElementById(PYAGRAM_EXCEPTION_ID);
var printOutput = document.getElementById(PRINT_OUTPUT_ID);

var visOptions = {
    'textPointers': visOptionsTextPointers,
    'hideFlags': visOptionsHideFlags,
};

function drawSnapshot(snapshotIndex) {
    Pyagram.drawSnapshot(
        snapshotIndex,
        visOptions,
        pyagramStack,
        pyagramHeap,
        pyagramException,
        printOutput,
        PYAGRAM_STATE_TABLE_ID,
        PYAGRAM_SVG_CANVAS_ID,
    );
}

editor.session.on('change', function(delta) {
    Overlay.setTop(outputOverlay);
});

Slider.initializeSlider(slider, sliderLabel, sliderButtonL, sliderButtonR, function(newValue) {
    drawSnapshot(newValue);
});

drawPyagramButton.onclick = function() {
    var code = editor.session.getValue();
    if (code === '') {
        alert('First write some code that you want to visualize.');
    } else {
        var drawPyagramButtonEffect = drawPyagramButton.onclick;
        drawPyagramButton.onclick = function() {};
        var drawPyagramButtonText = drawPyagramButton.innerHTML;
        drawPyagramButton.innerHTML = DRAW_PYAGRAM_BUTTON_WAIT_TEXT;
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
                drawPyagramButton.onclick = drawPyagramButtonEffect;
                drawPyagramButton.innerHTML = drawPyagramButtonText;
            },
        });
    }
};

Object.keys(visOptions).forEach(function(visOptionID) {
    visOptions[visOptionID].onclick = function() {
        drawSnapshot(slider.value);
    }
});

editor.focus();
