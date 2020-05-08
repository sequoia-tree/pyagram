const GUTTER_SIZE = 8;

export function split(direction, panelIDs, initialSizes, minSizes) {
    Split(
        panelIDs.map(panelID => '#' + panelID),
        {
            sizes: initialSizes,
            minSize: minSizes,
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
