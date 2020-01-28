const ACTIVE_CLASS_NAME = 'active';

export function setTop(overlay) {
    overlay.classList.add(ACTIVE_CLASS_NAME);
}

export function setBottom(overlay) {
    overlay.classList.remove(ACTIVE_CLASS_NAME);
}
