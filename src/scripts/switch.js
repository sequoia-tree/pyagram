import { decodeElementSnapshot } from "./decode";

const ACTIVE_CLASS_NAME = 'active';

export function select(parent, childIndex) {
    var child;
    for (child of parent.children) {
        child.classList.remove(ACTIVE_CLASS_NAME);
    }
    parent.children[childIndex].classList.add(ACTIVE_CLASS_NAME);
}
