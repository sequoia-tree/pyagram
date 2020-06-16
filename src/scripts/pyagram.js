import * as Constants from './constants.js';
import * as Decode from './decode.js';
import * as Slider from './slider.js';
import * as Switch from './switch.js';

var dataType;
var snapshots;
var globalData;
var pgErrorInfo;

export function drawPyagram(slider, pyagram) {
    switch (pyagram.encoding) {
        case 'pyagram':
            dataType = 'pyagram';
            snapshots = pyagram.data.snapshots;
            globalData = pyagram.data.global_data;
            pgErrorInfo = undefined;
            slider.min = 0;
            slider.max = snapshots.length - 1;
            break;
        case 'syntax_error':
            dataType = 'error';
            snapshots = undefined;
            globalData = undefined;
            pgErrorInfo = pyagram.data;
            slider.min = 0;
            slider.max = 0;
            break;
        case 'pyagram_error':
            dataType = 'error';
            snapshots = undefined;
            globalData = undefined;
            pgErrorInfo = pyagram.data;
            slider.min = 0;
            slider.max = 0;
            break;
    }
    Slider.reset(slider);
}

export function drawSnapshot(snapshotIndex, visOptions, pyagramStack, pyagramHeap) {
    switch (dataType) {
        case undefined:
            break;
        case 'pyagram':
            Switch.select(Constants.PYAGRAM_DATA_SWITCH, Constants.PG_DATA_RESULT_VIEW_ID);
            var snapshot = snapshots[snapshotIndex];
            var pyagramHTML = Decode.decodePyagramSnapshot(
                snapshot,
                globalData,
                visOptions,
            );
            pyagramStack.innerHTML = pyagramHTML.stackHTML;
            pyagramHeap.innerHTML = pyagramHTML.heapHTML;
            Constants.EXCEPTION_VIEW.innerHTML = pyagramHTML.exceptionHTML;
            Constants.PRINT_OUTPUT_VIEW.innerHTML = pyagramHTML.printOutputHTML;
            // TODO: Use snapshot.curr_line_no.
            drawSVGs(visOptions);
            break;
        case 'error':
            Switch.select(Constants.PYAGRAM_DATA_SWITCH, Constants.PG_DATA_ERROR_VIEW_ID);
            var pyagramHTML = Decode.decodePyagramError(pgErrorInfo);
            Constants.PG_DATA_ERROR_VIEW.innerHTML = pyagramHTML;
            break;
    }
}

function drawSVGs(visOptions) {
    var SVGCanvas = document.getElementById(Constants.PYAGRAM_SVG_CANVAS_ID);
    clearSVGCanvas(SVGCanvas);
    SVGCanvas = $(SVGCanvas);
    if (!visOptions.splitView.checked) {
        $(
            `.${Constants.FRAME_VALUE_CLASS_NAME}:has(.${Constants.REFERENCE_CLASS_NAME})`
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
    objects = document.getElementsByClassName(Constants.OBJECT_CLASS_NAME);
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
            x: -Constants.POINTER_BUFFER_X,
            y: -Constants.POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left - Constants.ARROWHEAD_DIAG_PADDING,
            y: object.offset().top + Constants.DIAGONAL_PADDING - Constants.ARROWHEAD_DIAG_PADDING,
        },
    };
    var endCoordinateL = {
        pre: {
            x: -Constants.POINTER_BUFFER_X,
            y: 0,
        },
        loc: {
            x: object.offset().left - Constants.ARROWHEAD_PADDING,
            y: object.offset().top + object.height() / 2,
        },
    };
    var endCoordinateBL = {
        pre: {
            x: -Constants.POINTER_BUFFER_X,
            y: +Constants.POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left - Constants.ARROWHEAD_DIAG_PADDING,
            y: object.offset().top + object.height() - Constants.DIAGONAL_PADDING + Constants.ARROWHEAD_DIAG_PADDING,
        },
    };
    var endCoordinateT = {
        pre: {
            x: 0,
            y: -Constants.POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left + object.width() / 2,
            y: object.offset().top - Constants.ARROWHEAD_PADDING,
        },
    };
    var endCoordinateB = {
        pre: {
            x: 0,
            y: +Constants.POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left + object.width() / 2,
            y: object.offset().top + object.height() + Constants.ARROWHEAD_PADDING,
        },
    };
    var endCoordinateM = {
        pre: {
            x: 0,
            y: +Constants.POINTER_BUFFER_Y,
        },
        loc: {
            x: object.offset().left + object.width() / 3,
            y: object.offset().top + object.height() + Constants.ARROWHEAD_PADDING,
        },
    }
    var endCoordinateR = {
        pre: {
            x: +Constants.POINTER_BUFFER_X,
            y: 0,
        },
        loc: {
            x: object.offset().left + object.width() + Constants.ARROWHEAD_PADDING,
            y: object.offset().top + object.height() / 2,
        },
    };
    var isL = startCoordinate.x < endCoordinateL.loc.x;
    var isR = endCoordinateR.loc.x < startCoordinate.x;
    var isT = startCoordinate.y < endCoordinateT.loc.y;
    var isB = endCoordinateB.loc.y < startCoordinate.y;
    var endCoordinate;
    if (startCoordinate.x + Constants.R_HPTR_MARGIN > endCoordinateR.loc.x) {
        endCoordinate = endCoordinateR;
    } else if (isL && !isB && startCoordinate.y + Constants.L_VPTR_MARGIN > endCoordinateT.loc.y) {
        endCoordinate = endCoordinateL;
    } else if (isL && !isT && startCoordinate.y - Constants.L_VPTR_MARGIN < endCoordinateB.loc.y) {
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
    pointer.setAttribute('class', Constants.POINTER_CLASS_NAME);
    pointer.setAttribute('d', pathStr);
    document.getElementById(Constants.POINTERS_SVG_GROUP_ID).appendChild(pointer);
}
