export function setSlider(slider, newValue) {
    slider.value = newValue;
    slider.oninput();
}

export function resetSlider(slider) {
    setSlider(slider, slider.min);
}

export function incrementSlider(slider, delta) {
    var value = parseInt(slider.value);
    var newValue = value + delta;
    if (parseInt(slider.min) <= newValue && newValue <= parseInt(slider.max) && value !== newValue) {
        setSlider(slider, newValue);
    }
}

export function updateLabel(slider) {
    var label = getSliderLabel(slider.id);
    label.innerHTML = slider.value;
}

export function getSlider(id) {
    return document.getElementById(id);
}

export function getSliderLabel(id) {
    return document.getElementById(id.concat('-label'));
}

export function getSliderLButton(id) {
    return document.getElementById(id.concat('-l-button'));
}

export function getSliderRButton(id) {
    return document.getElementById(id.concat('-r-button'));
}
