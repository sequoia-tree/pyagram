import * as editor from './editor.js';
import * as slider from './slider.js';

const EDITOR_ID = 'editor';
const SLIDER_ID = 'step-slider';
const OVERLAY_ID = 'overlay';
const PYAGRAM_ID = 'pyagram';
const PRINT_OUTPUT_ID = 'print-output';
const STATE_TABLE_ID = 'state-table'; // TODO: Don't hard-code this constant below.
const SVG_CANVAS_ID = 'svg-canvas'; // TODO: Don't hard-code this constant below.
const ARROWHEAD_WIDTH = 10;
const ARROWHEAD_PADDING = 2;
const POINTER_BUFFER_X = 100;
const POINTER_BUFFER_Y = 35;
const NUM_LINES = 30;

var pgEditor = editor.newEditor(EDITOR_ID, NUM_LINES);
var pgEditorButton = editor.getEditorButton(EDITOR_ID);
var pgSlider = slider.getSlider(SLIDER_ID);
var pgSliderLButton = slider.getSliderLButton(SLIDER_ID);
var pgSliderRButton = slider.getSliderRButton(SLIDER_ID);
var pgOverlay = document.getElementById(OVERLAY_ID);
var pyagramPane = document.getElementById(PYAGRAM_ID);
var printOutputPane = document.getElementById(PRINT_OUTPUT_ID);

var pgSnapshots;

function loadPyagram(pyagram) {
    if (pyagram.is_error) {
        alert(pyagram.data);
    } else {
        pgSnapshots = pyagram.data;
        pgSlider.min = 0;
        pgSlider.max = pgSnapshots.length - 1;
        slider.resetSlider(pgSlider);
        pgOverlay.style.display = 'none';    
    }
}

function loadSnapshot(i) {
    pyagramPane.innerHTML = pgSnapshots[i].state;
    printOutputPane.innerHTML = '[TODO] curr line no.: '.concat(pgSnapshots[i].curr_line_no); // TODO: Add support for the print output.
    $('#svg-canvas').css('height', $('#state-table').height());
    $('#svg-canvas').css('width', $('#state-table').width());
    drawPointers();
}

function drawPointers() {
    var references;
    var reference;
    var objects;
    var object;
    var id;
    objects = document.getElementsByClassName('pyagram-object');
    for (object of objects) {
        id = parseInt(object.id.replace(/^object-/, ''));
        references = document.getElementsByClassName('reference-'.concat(id));
        for (reference of references) {
            drawPointer(reference, object);
        }
    }
}

function drawPointer(reference, object) {
    var canvas = $('#svg-canvas');
    var reference = $(reference);
    var object = $(object);
    var nullCoordinate = {
        x: canvas.offset().left,
        y: canvas.offset().top,
    }
    var startCoordinate = {
        x: reference.offset().left + reference.width() / 2,
        y: reference.offset().top + reference.height() / 2,
    };
    var endCoordinate = {
        x: object.offset().left,
        y: object.offset().top + object.height() / 2,
    };
    startCoordinate.x -= nullCoordinate.x;
    startCoordinate.y -= nullCoordinate.y;
    endCoordinate.x -= nullCoordinate.x;
    endCoordinate.y -= nullCoordinate.y;
    var pathStr = 
        'M' +
        startCoordinate.x + ',' + startCoordinate.y + ' ' +
        'Q' +
        (endCoordinate.x - POINTER_BUFFER_X) + ',' + (endCoordinate.y + POINTER_BUFFER_Y) + ' ' +
        (endCoordinate.x - (ARROWHEAD_WIDTH - ARROWHEAD_PADDING)) + ',' + endCoordinate.y;
    var pointer = document.createElementNS("http://www.w3.org/2000/svg", 'path');
    pointer.setAttribute('class', 'pyagram-pointer');
    pointer.setAttribute('d', pathStr);
    document.getElementById('pointers').appendChild(pointer);
}

pgEditor.session.on('change', function(delta) {
    pgOverlay.style.display = 'block';
});

pgEditorButton.onclick = function() {
    var code = pgEditor.session.getValue();
    if (code === '') {
        alert('First write some code that you want to visualize.');
    } else {
        $.ajax({
            type: 'GET',
            url: '/draw',
            data: {'code': code},
            contentType: 'application/json',
            dataType: 'json',
            success: loadPyagram,
        });
    }
};

pgSlider.oninput = function() {
    slider.updateLabel(pgSlider);
    loadSnapshot(parseInt(pgSlider.value));
};

pgSliderLButton.onclick = function() {
    slider.incrementSlider(pgSlider, -1);
};

pgSliderRButton.onclick = function() {
    slider.incrementSlider(pgSlider, 1);
};

pgEditor.focus();
