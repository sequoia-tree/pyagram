const ACTIVE_INIT_CLASS_NAME = 'active-init';
const ACTIVE_CLASS_NAME = 'active';

export function setTop(overlay) {
    if (!overlay.classList.contains(ACTIVE_INIT_CLASS_NAME) && !overlay.classList.contains(ACTIVE_CLASS_NAME)) {
        overlay.classList.add(ACTIVE_CLASS_NAME);
    }
}

export function setBottom(overlay) {
    overlay.classList.remove(ACTIVE_INIT_CLASS_NAME);
    overlay.classList.remove(ACTIVE_CLASS_NAME);
}
