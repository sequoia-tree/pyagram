import * as Decode from './decode.js';
import * as Slider from './slider.js';

const POINTERS_SVG_GROUP_ID = 'pointers';
const OBJECT_CLASS_NAME = 'pyagram-object';
const POINTER_CLASS_NAME = 'pyagram-pointer';
const FRAME_VALUE_CLASS_NAME = 'pyagram-frame-value';
const REFERENCE_CLASS_NAME = 'pyagram-reference';

const ARROWHEAD_WIDTH = 10;
const ARROWHEAD_PADDING = 2;
const POINTER_BUFFER_X = 100;
const POINTER_BUFFER_Y = 0;

var snapshots;
var globalData;

export function drawPyagram(slider, pyagram) {
    switch (pyagram.encoding) {
        case 'pyagram':
            snapshots = pyagram.data.snapshots;
            globalData = pyagram.data.global_data;
            slider.min = 0;
            slider.max = snapshots.length - 1;
            Slider.reset(slider);
            break;
        case 'syntax_error':
            // TODO
            break;
        case 'pyagram_error':
            // TODO
            break;
        default:
            break;
    }
}

export function drawSnapshot(snapshotIndex, visOptions, pyagramStack, pyagramHeap, pyagramException, printOutput, stateTableID, SVGCanvasID) {
    if (typeof snapshots !== 'undefined') {
        var snapshot = snapshots[snapshotIndex];
        var pyagramHTML = Decode.decodePyagramSnapshot(
            snapshot,
            globalData,
            visOptions,
        );
        pyagramStack.innerHTML = pyagramHTML.stackHTML;
        pyagramHeap.innerHTML = pyagramHTML.heapHTML;
        pyagramException.innerHTML = pyagramHTML.exceptionHTML;
        printOutput.innerHTML = pyagramHTML.printOutputHTML;
        // TODO: Use snapshot.curr_line_no.
        // if (!visOptions.textPointers.checked) {
        //     var stateTable = $('#'.concat(stateTableID));
        //     var SVGCanvas = $('#'.concat(SVGCanvasID));
        //     drawSVGCanvas(stateTable, SVGCanvas);
        //     drawPointers(SVGCanvas);
        // };
    }
}

function drawSVGCanvas(stateTable, SVGCanvas) {
    SVGCanvas.css('height', stateTable.height());
    SVGCanvas.css('width', stateTable.width());
    $(
        `.${FRAME_VALUE_CLASS_NAME}:has(.${REFERENCE_CLASS_NAME})`
    ).removeClass('text-left').addClass('text-center');
}

function drawPointers(SVGCanvas) {
    var references;
    var reference;
    var objects;
    var object;
    var id;
    objects = document.getElementsByClassName(OBJECT_CLASS_NAME);
    for (object of objects) {
        id = object.id.replace(/^object-/, '');
        references = document.getElementsByClassName('reference-'.concat(id));
        for (reference of references) {
            drawPointer(SVGCanvas, $(reference), $(object));
        }
    }
}

function drawPointer(SVGCanvas, reference, object) {
    var nullCoordinate = {
        x: SVGCanvas.offset().left,
        y: SVGCanvas.offset().top,
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
    var pointer = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pointer.setAttribute('class', POINTER_CLASS_NAME);
    pointer.setAttribute('d', pathStr);
    document.getElementById(POINTERS_SVG_GROUP_ID).appendChild(pointer);
}
