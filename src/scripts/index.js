import * as Constants from './constants.js';
import * as Editor from './editor.js';
import * as Overlay from './overlay.js';
import * as Pyagram from './pyagram.js';
import * as Slider from './slider.js';
import * as Split from './split.js';
import * as Switch from './switch.js';

const editor = Editor.editor(Constants.EDITOR_ID, Constants.NUM_LINES); // TODO: ??

var visOptions = {
    'splitView': Constants.VIS_OPTIONS_SPLIT_VIEW,
    'completedFlags': Constants.VIS_OPTIONS_COMPLETED_FLAGS,
    'oldObjects': Constants.VIS_OPTIONS_OLD_OBJECTS,
};

var pyagramStack = Constants.DIAGRAM_UNIFIED_STACK;
var pyagramHeap = Constants.DIAGRAM_UNIFIED_HEAP;

function drawSnapshot(snapshotIndex) {
    Pyagram.drawSnapshot(
        snapshotIndex,
        visOptions,
        pyagramStack,
        pyagramHeap,
        Constants.EXCEPTION_VIEW,
        Constants.PRINT_OUTPUT_VIEW,
    );
}

function visOptionClick() {
    drawSnapshot(Constants.SLIDER.value);
}

Split.split(
    'horizontal',
    [
        Constants.SPLIT_PANEL_INPUT_ID,
        Constants.SPLIT_PANEL_OUTPUT_ID,
    ],
    [35, 65],
    [0, 0],
);

Split.split(
    'vertical',
    [
        Constants.SPLIT_PANEL_PYAGRAM_ID,
        Constants.SPLIT_PANEL_PRINT_OUTPUT_ID,
    ],
    [80, 20],
    [0, 0],
);

Split.split(
    'horizontal',
    [
        Constants.SPLIT_PANEL_STACK_ID,
        Constants.SPLIT_PANEL_HEAP_ID,
    ],
    [55, 45],
    [0, 0],
);

editor.session.on('change', function(delta) {
    Overlay.setTop(Constants.OUTPUT_OVERLAY);
});

Slider.initializeSlider(
    Constants.SLIDER,
    Constants.SLIDER_LABEL,
    Constants.SLIDER_L_BUTTON,
    Constants.SLIDER_R_BUTTON,
    true,
    drawSnapshot,
);

Object.keys(visOptions).forEach(function(visOptionID) {
    visOptions[visOptionID].onclick = visOptionClick;
});

visOptions.splitView.onclick = function() {
    if (visOptions.splitView.checked) {
        Switch.select(Constants.DIAGRAM_VIEW_SWITCH, Constants.DIAGRAM_DIVIDED_VIEW_ID);
        pyagramStack = Constants.DIAGRAM_DIVIDED_STACK;
        pyagramHeap = Constants.DIAGRAM_DIVIDED_HEAP;
    } else {
        Switch.select(Constants.DIAGRAM_VIEW_SWITCH, Constants.DIAGRAM_UNIFIED_VIEW_ID);
        pyagramStack = Constants.DIAGRAM_UNIFIED_STACK;
        pyagramHeap = Constants.DIAGRAM_UNIFIED_HEAP;
    }
    visOptionClick();
};

Constants.DRAW_PYAGRAM_BUTTON.onclick = function() {
    var code = editor.session.getValue();
    if (code === '') {
        alert(Constants.EMPTY_EDITOR_SANITY_CHECK_MSG);
    } else {
        var drawPyagramButtonEffect = Constants.DRAW_PYAGRAM_BUTTON.onclick;
        var drawPyagramButtonText = Constants.DRAW_PYAGRAM_BUTTON.innerHTML;
        Constants.DRAW_PYAGRAM_BUTTON.onclick = function() {};
        Constants.DRAW_PYAGRAM_BUTTON.innerHTML = Constants.DRAW_PYAGRAM_BUTTON_WAIT_TEXT;
        $.ajax({
            type: 'GET',
            url: '/draw',
            data: {
                'code': code,
            },
            contentType: 'application/json',
            dataType: 'json',
            success: function(pyagram) {
                Pyagram.drawPyagram(Constants.SLIDER, pyagram);
                Overlay.setBottom(Constants.OUTPUT_OVERLAY);
                Constants.DRAW_PYAGRAM_BUTTON.onclick = drawPyagramButtonEffect;
                Constants.DRAW_PYAGRAM_BUTTON.innerHTML = drawPyagramButtonText;
            },
        });
    }
};

editor.focus();
