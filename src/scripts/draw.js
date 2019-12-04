export function drawPyagram(snapshots) {
    var pyagramPane = document.getElementById('pyagram');
    var printOutputPane = document.getElementById('print-output');

    // TODO: Make a slider with left / right arrows to navigate through snapshots.

    // TODO: Draw pyagram.
    // TODO: Draw print output.

    // This stuff is placeholder ... :
    pyagramPane.innerHTML = snapshots[snapshots.length - 1].program_state.global_frame;
    printOutputPane.innerHTML = 'test: line one\ntest: line two';
}
