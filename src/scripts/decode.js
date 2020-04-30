import * as Templates from './templates.js';

export function decodePyagramSnapshot(pyagramSnapshot) {
    return Templates.PYAGRAM_TEMPLATE(pyagramSnapshot);
}

export function decodeElementSnapshot(elementSnapshot) {
    return Templates.ELEMENT_TEMPLATE(elementSnapshot);
}

export function decodeFlagSnapshot(flagSnapshot) {
    return Templates.FLAG_TEMPLATE(flagSnapshot);
}

export function decodeFrameSnapshot(frameSnapshot) {
    return Templates.FRAME_TEMPLATE(frameSnapshot)
}

export function decodeReferenceSnapshot(referenceSnapshot) {
    if (referenceSnapshot === null) {
        return Templates.UNKNOWN_VALUE_TEMPLATE(referenceSnapshot);
    }
    switch (typeof referenceSnapshot) {
        case 'string':
            return Templates.PRIMITIVE_TEMPLATE(referenceSnapshot);
        case 'number':
            return Templates.REFERENT_TEMPLATE(referenceSnapshot);
    }
}

Handlebars.registerHelper('decodePyagramSnapshot', decodePyagramSnapshot);

Handlebars.registerHelper('decodeElementSnapshot', decodeElementSnapshot);

Handlebars.registerHelper('decodeFlagSnapshot', decodeFlagSnapshot);

Handlebars.registerHelper('decodeFrameSnapshot', decodeFrameSnapshot);

Handlebars.registerHelper('decodeReferenceSnapshot', decodeReferenceSnapshot);

Handlebars.registerHelper('isNull', function(object) {
    return object === null;
});

Handlebars.registerHelper('isEmpty', function(object) {
    return object.length === 0;
});

Handlebars.registerHelper('isEqual', function(operand1, operand2) {
    return operand1 === operand2;
});

Handlebars.registerHelper('mul', function(operand1, operand2) {
    return operand1 * operand2;
});

Handlebars.registerHelper('sum', function(operand1, operand2) {
    return operand1 + operand2;
});

// TODO: Finish templates.js and decode.js.
// TODO: Strip newlines and all the whitespace at the beginning / end of a line from each template?
