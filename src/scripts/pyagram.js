import * as Slider from './slider.js';

var snapshots;

export function drawPyagram(slider, pyagram) {
    switch (pyagram.encoding) {
        case 'pyagram':
            snapshots = pyagram.data.snapshots;
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
            // TODO
            break;
    }
}

export function drawSnapshot(snapshotIndex, pyagram, printOutput) {
    pyagram.innerHTML = snapshots[snapshotIndex].state;
    // TODO: Get pointers to show up!
    // TODO: Use the other attributes of snapshots[snapshotIndex].
}

// TODO: Once everything works like it did before winter break, delete the directory pyagram/src/REMOVE-THIS-OLD-STUFF.

// TODO: Instead of having layout.scss, just use jQuery to get the height of the editor + scrollbar, and set that element to have min-height: X + "px".





// function loadSnapshot(i) {
//     pyagramPane.innerHTML = pgSnapshots[i].state;
//     printOutputPane.innerHTML = pgSnapshots[i].print_output;
//     $('#svg-canvas').css('height', $('#state-table').height());
//     $('#svg-canvas').css('width', $('#state-table').width());
//     drawPointers();
// }





// function drawPointers() {
//     var references;
//     var reference;
//     var objects;
//     var object;
//     var id;
//     objects = document.getElementsByClassName('pyagram-object');
//     for (object of objects) {
//         id = parseInt(object.id.replace(/^object-/, ''));
//         references = document.getElementsByClassName('reference-'.concat(id));
//         for (reference of references) {
//             drawPointer(reference, object);
//         }
//     }
// }

// function drawPointer(reference, object) {
//     var canvas = $('#svg-canvas');
//     var reference = $(reference);
//     var object = $(object);
//     var nullCoordinate = {
//         x: canvas.offset().left,
//         y: canvas.offset().top,
//     }
//     var startCoordinate = {
//         x: reference.offset().left + reference.width() / 2,
//         y: reference.offset().top + reference.height() / 2,
//     };
//     var endCoordinate = {
//         x: object.offset().left,
//         y: object.offset().top + object.height() / 2,
//     };
//     startCoordinate.x -= nullCoordinate.x;
//     startCoordinate.y -= nullCoordinate.y;
//     endCoordinate.x -= nullCoordinate.x;
//     endCoordinate.y -= nullCoordinate.y;
//     var pathStr = 
//         'M' +
//         startCoordinate.x + ',' + startCoordinate.y + ' ' +
//         'Q' +
//         (endCoordinate.x - POINTER_BUFFER_X) + ',' + (endCoordinate.y + POINTER_BUFFER_Y) + ' ' +
//         (endCoordinate.x - (ARROWHEAD_WIDTH - ARROWHEAD_PADDING)) + ',' + endCoordinate.y;
//     var pointer = document.createElementNS("http://www.w3.org/2000/svg", 'path');
//     pointer.setAttribute('class', 'pyagram-pointer');
//     pointer.setAttribute('d', pathStr);
//     document.getElementById('pointers').appendChild(pointer);
// }
