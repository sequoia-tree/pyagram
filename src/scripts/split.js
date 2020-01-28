import Split from 'split.js';

const GUTTER_SIZE = 8;

export function split(direction, panelIDs, minSize) {
    Split(
        panelIDs.map(panelID => '#' + panelID),
        {
            minSize: minSize,
            gutterSize: GUTTER_SIZE,
            snapOffset: 0,
            direction: direction,
            elementStyle: (dimension, size, gutterSize) => ({
                'flex-basis': `calc(${size}% - ${gutterSize}px)`,
            }),
            gutterStyle: (dimension, gutterSize) => ({
                'flex-basis': `${gutterSize}px`,
            }),
        },
    );
}
