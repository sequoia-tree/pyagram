const ACTIVE_CLASS_NAME = 'active';

export function select(parent, childId) {
    var child;
    for (child of parent.children) {
        child.classList.remove(ACTIVE_CLASS_NAME);
        if (child.id === childId) {
            child.classList.add(ACTIVE_CLASS_NAME);
        }
    }
}
