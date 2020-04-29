import * as Templates from './templates.js';

export function decodePyagramSnapshot(pyagramSnapshot) {
    return Templates.FRAME_TEMPLATE(pyagramSnapshot.global_frame);
}

// TODO: Finish templates.js and decode.js.
// TODO: Strip newlines and all the whitespace at the beginning / end of a line from each template?
