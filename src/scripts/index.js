import * as Editor from './editor.js';
import * as Overlay from './overlay.js';
import * as Pyagram from './pyagram.js';
import * as Slider from './slider.js';
import * as Split from './split.js';
import * as Switch from './switch.js';

const SPLIT_PANEL_INPUT_ID = 'split-io-panel-input';
const SPLIT_PANEL_OUTPUT_ID = 'split-io-panel-output';
const SPLIT_PANEL_PYAGRAM_ID = 'split-runtime-panel-vm';
const SPLIT_PANEL_PRINT_OUTPUT_ID = 'split-runtime-panel-sys';
const SPLIT_PANEL_STACK_ID = 'split-vm-panel-stack';
const SPLIT_PANEL_HEAP_ID = 'split-vm-panel-heap';
const EDITOR_ID = 'editor-code';
const SLIDER_ID = 'slider-snapshots';
const SLIDER_LABEL_ID = 'slider-snapshots-label';
const SLIDER_L_BUTTON_ID = 'slider-snapshots-l';
const SLIDER_R_BUTTON_ID = 'slider-snapshots-r';
const VIS_OPTIONS_TEXT_POINTERS_ID = 'options-vis-option-text-ptrs';
const VIS_OPTIONS_SHOW_FLAGS_ID = 'options-vis-option-show-flags';
const OUTPUT_OVERLAY_ID = 'overlay-output';
const DRAW_PYAGRAM_BUTTON_ID = 'button-draw';
const PYAGRAM_STACK_HEAP_SWITCH_ID = 'switch-vm';
const PYAGRAM_TRACK_UNIFIED_VIEW_ID = 'switch-vm-track-unified';
const PYAGRAM_TRACK_DIVIDED_VIEW_ID = 'switch-vm-track-divided';
const PYAGRAM_UNIFIED_VIEW_STACK_ID = 'unified-stack';
const PYAGRAM_UNIFIED_VIEW_HEAP_ID = 'unified-heap';
const PYAGRAM_DIVIDED_VIEW_STACK_ID = 'divided-stack';
const PYAGRAM_DIVIDED_VIEW_HEAP_ID = 'divided-heap';
const PYAGRAM_EXCEPTION_ID = 'pyagram-exception';
const PRINT_OUTPUT_ID = 'print-output';
const DRAW_PYAGRAM_BUTTON_WAIT_TEXT = 'Drawing ...'
const NUM_LINES = 20;

var editor = Editor.editor(EDITOR_ID, NUM_LINES);
var slider = document.getElementById(SLIDER_ID);
var sliderLabel = document.getElementById(SLIDER_LABEL_ID);
var sliderButtonL = document.getElementById(SLIDER_L_BUTTON_ID);
var sliderButtonR = document.getElementById(SLIDER_R_BUTTON_ID);
var visOptionsTextPointers = document.getElementById(VIS_OPTIONS_TEXT_POINTERS_ID);
var visOptionsShowFlags = document.getElementById(VIS_OPTIONS_SHOW_FLAGS_ID);
var outputOverlay = document.getElementById(OUTPUT_OVERLAY_ID);
var drawPyagramButton = document.getElementById(DRAW_PYAGRAM_BUTTON_ID);
var pyagramStackHeapSwitch = document.getElementById(PYAGRAM_STACK_HEAP_SWITCH_ID);
var unifiedViewPyagramStack = document.getElementById(PYAGRAM_UNIFIED_VIEW_STACK_ID);
var unifiedViewPyagramHeap = document.getElementById(PYAGRAM_UNIFIED_VIEW_HEAP_ID);
var dividedViewPyagramStack = document.getElementById(PYAGRAM_DIVIDED_VIEW_STACK_ID);
var dividedViewPyagramHeap = document.getElementById(PYAGRAM_DIVIDED_VIEW_HEAP_ID);
var pyagramException = document.getElementById(PYAGRAM_EXCEPTION_ID);
var printOutput = document.getElementById(PRINT_OUTPUT_ID);

var pyagramStack = unifiedViewPyagramStack;
var pyagramHeap = unifiedViewPyagramHeap;

var visOptions = {
    'textPointers': visOptionsTextPointers,
    'showFlags': visOptionsShowFlags,
};

function drawSnapshot(snapshotIndex) {
    Pyagram.drawSnapshot(
        snapshotIndex,
        visOptions,
        pyagramStack,
        pyagramHeap,
        pyagramException,
        printOutput,
    );
}

function visOptionClick() {
    drawSnapshot(slider.value);
}

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
    [65, 35],
    [0, 0],
);

editor.session.on('change', function(delta) {
    Overlay.setTop(outputOverlay);
});

Slider.initializeSlider(slider, sliderLabel, sliderButtonL, sliderButtonR, function(newValue) {
    drawSnapshot(newValue);
});

Object.keys(visOptions).forEach(function(visOptionID) {
    visOptions[visOptionID].onclick = visOptionClick;
});

visOptions.textPointers.onclick = function() {
    if (visOptions.textPointers.checked) {
        Switch.select(pyagramStackHeapSwitch, PYAGRAM_TRACK_DIVIDED_VIEW_ID);
        pyagramStack = dividedViewPyagramStack;
        pyagramHeap = dividedViewPyagramHeap;
    } else {
        Switch.select(pyagramStackHeapSwitch, PYAGRAM_TRACK_UNIFIED_VIEW_ID);
        pyagramStack = unifiedViewPyagramStack;
        pyagramHeap = unifiedViewPyagramHeap;
    }
    visOptionClick();
};

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

editor.focus();
