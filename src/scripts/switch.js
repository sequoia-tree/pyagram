const ACTIVE_CLASS_NAME = 'active';
const INACTIVE_CLASS_NAME = 'inactive';

export function select(parent, childId) {
    var child;
    for (child of parent.children) {
        child.classList.remove(ACTIVE_CLASS_NAME);
        child.classList.remove(INACTIVE_CLASS_NAME);
        if (child.id === childId) {
            child.classList.add(ACTIVE_CLASS_NAME);
        } else {
            child.classList.add(INACTIVE_CLASS_NAME);
        }
    }
}
