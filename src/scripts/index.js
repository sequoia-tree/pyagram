import * as editor from './editor.js';
import * as slider from './slider.js';

const EDITOR_ID = 'editor';
const SLIDER_ID = 'step-slider';
const OVERLAY_ID = 'overlay';
const PYAGRAM_ID = 'pyagram';
const PRINT_OUTPUT_ID = 'print-output';
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

function loadPyagram(snapshots) {
    pgSnapshots = snapshots;
    resizeSlider();
    slider.resetSlider(pgSlider);
}

function loadSnapshot(i) {
    // TODO

    // This stuff is placeholder for now ...
    console.log('Loading snapshot '.concat(i));
    pyagramPane.innerHTML = pgSnapshots[i].program_state.global_frame;
    printOutputPane.innerHTML = 'test: line one\ntest: line two';
}

function resizeSlider() {
    pgSlider.min = 0;
    pgSlider.max = pgSnapshots.length - 1;
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
        pgOverlay.style.display = 'none';
    }
}

pgSlider.oninput = function() {
    slider.updateLabel(pgSlider);
    loadSnapshot(parseInt(pgSlider.value));
}

pgSliderLButton.onclick = function() {
    slider.incrementSlider(pgSlider, -1);
}

pgSliderRButton.onclick = function() {
    slider.incrementSlider(pgSlider, 1);
}

// TODO: Make the left / right arrow keys equivalent to using the buttons beneath the slider.

pgEditor.focus();
