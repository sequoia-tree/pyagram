import * as Templates from './templates.js';

var objNumbers;

var textPointers;
var hideFlags;

Handlebars.registerHelper('decodePyagramSnapshot', decodePyagramSnapshot);
export function decodePyagramSnapshot(pyagramSnapshot, globalData, visOptions) {
    objNumbers = globalData.obj_numbers;
    textPointers = visOptions.textPointers.checked;
    hideFlags = visOptions.hideFlags.checked;
    return {
        'stackHTML': decodeStackSnapshot(pyagramSnapshot.global_frame),
        'heapHTML': decodeHeapSnapshot(pyagramSnapshot.memory_state),
        'exceptionHTML': decodeExceptionSnapshot(pyagramSnapshot.exception),
        'printOutputHTML': decodePrintOutputSnapshot(pyagramSnapshot.print_output),
    };
}

Handlebars.registerHelper('decodeStackSnapshot', decodeStackSnapshot);
export function decodeStackSnapshot(stackSnapshot) {
    return Templates.STACK_TEMPLATE(stackSnapshot);
}

Handlebars.registerHelper('decodeElementSnapshot', decodeElementSnapshot);
export function decodeElementSnapshot(elementSnapshot) {
    return Templates.ELEMENT_TEMPLATE(elementSnapshot);
}

Handlebars.registerHelper('decodeFlagSnapshot', decodeFlagSnapshot);
export function decodeFlagSnapshot(flagSnapshot) {
    return Templates.FLAG_TEMPLATE(flagSnapshot);
}

Handlebars.registerHelper('decodeFrameSnapshot', decodeFrameSnapshot);
export function decodeFrameSnapshot(frameSnapshot) {
    return Templates.FRAME_TEMPLATE(frameSnapshot);
}

Handlebars.registerHelper('decodeHeapSnapshot', decodeHeapSnapshot);
export function decodeHeapSnapshot(heapSnapshot) {
    if (textPointers) {
        return Templates.HEAP_TEMPLATE_TEXTPOINTERS_T(heapSnapshot);
    } else {
        return Templates.HEAP_TEMPLATE_TEXTPOINTERS_F(heapSnapshot);
    }
}

Handlebars.registerHelper('decodeUnknownSnapshot', decodeUnknownSnapshot);
export function decodeUnknownSnapshot(unknownSnapshot) {
    return Templates.UNKNOWN_TEMPLATE(unknownSnapshot);
}

Handlebars.registerHelper('decodeReferenceSnapshot', decodeReferenceSnapshot);
export function decodeReferenceSnapshot(referenceSnapshot) {
    switch (typeof referenceSnapshot) {
        case 'object':
            return Templates.UNKNOWN_TEMPLATE(referenceSnapshot);
        case 'string':
            return Templates.PRIMITIVE_TEMPLATE(referenceSnapshot);
        case 'number':
            if (textPointers) {
                return Templates.REFERENT_TEMPLATE_TEXTPOINTERS_T(referenceSnapshot);
            } else {
                return Templates.REFERENT_TEMPLATE_TEXTPOINTERS_F(referenceSnapshot);
            }
    }
}

Handlebars.registerHelper('decodeObjectIdSnapshot', decodeObjectIdSnapshot);
export function decodeObjectIdSnapshot(objectIdSnapshot) {
    objectIdSnapshot = objNumbers[objectIdSnapshot];
    return Templates.OBJECT_ID_TEMPLATE(objectIdSnapshot);
}

Handlebars.registerHelper('decodeEncodedObjectSnapshot', decodeEncodedObjectSnapshot);
export function decodeEncodedObjectSnapshot(encodedObjectSnapshot) {
    switch (encodedObjectSnapshot.encoding) {
        case 'primitive':
            return Templates.PRIMITIVE_TEMPLATE(encodedObjectSnapshot.data);
        case 'function':
            return Templates.FUNCTION_TEMPLATE(encodedObjectSnapshot.data);
        case 'builtin':
            return Templates.BUILTIN_TEMPLATE(encodedObjectSnapshot.data);
        case 'ordered_collection':
            return Templates.ORDERED_COLLECTION_TEMPLATE(encodedObjectSnapshot.data);
        case 'unordered_collection':
            return Templates.UNORDERED_COLLECTION_TEMPLATE(encodedObjectSnapshot.data);
        case 'mapping':
            return Templates.MAPPING_TEMPLATE(encodedObjectSnapshot.data);
        case 'iterator':
            return Templates.ITERATOR_TEMPLATE(encodedObjectSnapshot.data);
        case 'generator':
            return Templates.FRAME_TEMPLATE(encodedObjectSnapshot.data);
        case 'obj_class':
            return Templates.FRAME_TEMPLATE(encodedObjectSnapshot.data);
        case 'obj_inst':
            return Templates.FRAME_TEMPLATE(encodedObjectSnapshot.data);
        case 'other':
            return Templates.OTHER_TEMPLATE(encodedObjectSnapshot.data);
    }
}

Handlebars.registerHelper('decodeExceptionSnapshot', decodeExceptionSnapshot);
export function decodeExceptionSnapshot(exceptionSnapshot) {
    return Templates.EXCEPTION_TEMPLATE(exceptionSnapshot);
}

Handlebars.registerHelper('decodePrintOutputSnapshot', decodePrintOutputSnapshot);
export function decodePrintOutputSnapshot(printOutputSnapshot) {
    return Templates.PRINT_OUTPUT_TEMPLATE(printOutputSnapshot);
}

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
