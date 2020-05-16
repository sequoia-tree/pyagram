import * as Decode from './decode.js';
import * as Slider from './slider.js';

const PYAGRAM_SVG_CANVAS_ID = 'pyagram-svg-canvas';
const POINTERS_SVG_GROUP_ID = 'pointers';

const OBJECT_CLASS_NAME = 'pyagram-object';
const POINTER_CLASS_NAME = 'pyagram-pointer';
const FRAME_VALUE_CLASS_NAME = 'pyagram-frame-value';
const REFERENCE_CLASS_NAME = 'pyagram-reference';

const ARROWHEAD_PADDING = 12;
const ARROWHEAD_DIAG_PADDING = ARROWHEAD_PADDING / Math.sqrt(2);
const DIAGONAL_PADDING = 10;
const LEFT_VPTR_MARGIN = 50;
const POINTER_BUFFER_X = 25;
const POINTER_BUFFER_Y = 25;

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
    var endCoordinateTL = {
        pre: {
            x: -POINTER_BUFFER_X,
            y: -POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left - ARROWHEAD_DIAG_PADDING,
            y: object.offset().top - ARROWHEAD_DIAG_PADDING + DIAGONAL_PADDING,
        },
    };
    var endCoordinateL = {
        pre: {
            x: -POINTER_BUFFER_X,
            y: 0,
        },
        loc: {
            x: object.offset().left - ARROWHEAD_PADDING,
            y: object.offset().top + object.height() / 2,
        },
    };
    var endCoordinateBL = {
        pre: {
            x: -POINTER_BUFFER_X,
            y: +POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left - ARROWHEAD_DIAG_PADDING,
            y: object.offset().top + object.height() + ARROWHEAD_DIAG_PADDING - DIAGONAL_PADDING,
        },
    };
    var endCoordinateT = {
        pre: {
            x: 0,
            y: -POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left + object.width() / 2,
            y: object.offset().top - ARROWHEAD_PADDING,
        },
    };
    var endCoordinateB = {
        pre: {
            x: 0,
            y: +POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left + object.width() / 2,
            y: object.offset().top + object.height() + ARROWHEAD_PADDING,
        },
    };
    var endCoordinateM = {
        pre: {
            x: 0,
            y: +POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left + object.width() / 3,
            y: object.offset().top + object.height() + ARROWHEAD_PADDING,
        },
    }
    var endCoordinateR = {
        pre: {
            x: +POINTER_BUFFER_X,
            y: 0,
        },
        loc: {
            x: object.offset().left + object.width() + ARROWHEAD_PADDING,
            y: object.offset().top + object.height() / 2,
        },
    };
    var isL = startCoordinate.x < endCoordinateL.loc.x;
    var isR = endCoordinateR.loc.x < startCoordinate.x;
    var isT = startCoordinate.y < endCoordinateT.loc.y;
    var isB = endCoordinateB.loc.y < startCoordinate.y;
    var endCoordinate;
    if (isR) {
        endCoordinate = endCoordinateR;
    } else if (isL && !isB && startCoordinate.y + LEFT_VPTR_MARGIN > endCoordinateT.loc.y) {
        endCoordinate = endCoordinateL;
    } else if (isL && !isT && startCoordinate.y - LEFT_VPTR_MARGIN < endCoordinateB.loc.y) {
        endCoordinate = endCoordinateL;
    } else if (isL && isT) {
        endCoordinate = endCoordinateTL;
    } else if (isL && isB) {
        endCoordinate = endCoordinateBL;
    } else if (isT) {
        endCoordinate = endCoordinateT;
    } else if (isB) {
        endCoordinate = endCoordinateB;
    } else {
        endCoordinate = endCoordinateM;
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
        (endCoordinate.loc.x) + ',' +
        (endCoordinate.loc.y);
    var pointer = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    pointer.setAttribute('class', POINTER_CLASS_NAME);
    pointer.setAttribute('d', pathStr);
    document.getElementById(POINTERS_SVG_GROUP_ID).appendChild(pointer);
}
