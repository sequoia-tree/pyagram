import * as Decode from './decode.js';
import * as Slider from './slider.js';

const PYAGRAM_SVG_CANVAS_ID = 'pyagram-svg-canvas';
const POINTERS_SVG_GROUP_ID = 'pointers';

const OBJECT_CLASS_NAME = 'pyagram-object';
const POINTER_CLASS_NAME = 'pyagram-pointer';
const FRAME_VALUE_CLASS_NAME = 'pyagram-frame-value';
const REFERENCE_CLASS_NAME = 'pyagram-reference';

const ARROWHEAD_WIDTH = 10;
const ARROWHEAD_PADDING = 2;
const POINTER_BUFFER = 100;
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

export function drawSnapshot(snapshotIndex, visOptions, pyagramStack, pyagramHeap, pyagramException, printOutput) {
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
        drawSVGs(visOptions);
    }
}

function drawSVGs(visOptions) {
    var SVGCanvas = document.getElementById(PYAGRAM_SVG_CANVAS_ID);
    clearSVGCanvas(SVGCanvas);
    SVGCanvas = $(SVGCanvas);
    if (!visOptions.textPointers.checked) {
        $(
            `.${FRAME_VALUE_CLASS_NAME}:has(.${REFERENCE_CLASS_NAME})`
        ).removeClass('text-left').addClass('text-center');
        drawPointers(SVGCanvas);
    }
}

function clearSVGCanvas(SVGCanvas) {
    var SVGGroup;
    for (SVGGroup of SVGCanvas.getElementsByTagName('g')) {
        $(SVGGroup).empty();
    }
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
    // var endCoordinate = [
    //     {
    //         pre: {
    //             x: -POINTER_BUFFER,
    //             y: 0,
    //         },
    //         loc: {
    //             x: object.offset().left,
    //             y: object.offset().top + object.height() / 2,
    //         },
    //     },
    //     {
    //         pre: {
    //             x: POINTER_BUFFER,
    //             y: 0,
    //         },
    //         loc: {
    //             x: object.offset().left + object.width(),
    //             y: object.offset().top + object.height() / 2,
    //         },
    //     },
    //     {
    //         pre: {
    //             x: 0,
    //             y: -POINTER_BUFFER,
    //         },
    //         loc: {
    //             x: object.offset().left + object.width() / 2,
    //             y: object.offset().top,
    //         },
    //     },
    //     {
    //         pre: {
    //             x: 0,
    //             y: POINTER_BUFFER,
    //         },
    //         loc: {
    //             x: object.offset().left + object.width() / 2,
    //             y: object.offset().top + object.height(),
    //         },
    //     },
    // ].reduce(function(bestCoordinate, currCoordinate) {
    //     var toBest = manhattanDistance(startCoordinate, bestCoordinate.loc);
    //     var toCurr = manhattanDistance(startCoordinate, currCoordinate.loc);
    //     return toBest < toCurr ? bestCoordinate : currCoordinate;
    // }, {
    //     pre: {x: Infinity, y: Infinity},
    //     loc: {x: Infinity, y: Infinity}
    // });
    var endCoordinateL = {
        pre: {
            x: -POINTER_BUFFER,
            y: 0,
        },
        loc: {
            x: object.offset().left,
            y: object.offset().top + object.height() / 2,
        },
    };
    var endCoordinateR = {
        pre: {
            x: POINTER_BUFFER,
            y: 0,
        },
        loc: {
            x: object.offset().left + object.width(),
            y: object.offset().top + object.height() / 2,
        },
    };
    var endCoordinateU = {
        pre: {
            x: 0,
            y: -POINTER_BUFFER,
        },
        loc: {
            x: object.offset().left + object.width() / 2,
            y: object.offset().top,
        },
    };
    var endCoordinateD = {
        pre: {
            x: 0,
            y: POINTER_BUFFER,
        },
        loc: {
            x: object.offset().left + object.width() / 2,
            y: object.offset().top + object.height(),
        },
    };
    var endCoordinate;
    if (startCoordinate.x >= endCoordinateR.loc.x) {
        endCoordinate = endCoordinateR;
    } else if (startCoordinate.y < endCoordinateU.loc.y) {
        endCoordinate = endCoordinateU;
    } else if (startCoordinate.y > endCoordinateD.loc.y) {
        endCoordinate = endCoordinateD;
    } else {
        endCoordinate = endCoordinateL;
    }
    startCoordinate.x -= nullCoordinate.x;
    startCoordinate.y -= nullCoordinate.y;
    endCoordinate.loc.x -= nullCoordinate.x;
    endCoordinate.loc.y -= nullCoordinate.y;
    var pathStr =
        'M' +
        startCoordinate.x + ',' +
        startCoordinate.y + ' ' +
        'Q' +
        (endCoordinate.loc.x + endCoordinate.pre.x) + ',' +
        (endCoordinate.loc.y + endCoordinate.pre.y) + ' ' +
        (endCoordinate.loc.x) + ',' + (endCoordinate.loc.y);
    //  (endCoordinate.x - (ARROWHEAD_WIDTH - ARROWHEAD_PADDING)) + ',' + endCoordinate.y;
    var pointer = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pointer.setAttribute('class', POINTER_CLASS_NAME);
    pointer.setAttribute('d', pathStr);
    document.getElementById(POINTERS_SVG_GROUP_ID).appendChild(pointer);
}
// TODO: I think the buffer in the x-axis should be 100, and the buffer in the y-axis should be 50.
