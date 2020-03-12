export function initializeSlider(slider, sliderLabel, sliderButtonL, sliderButtonR, emitValue) {
    slider.oninput = function() {
        emitValue(parseInt(slider.value));
        sliderLabel.innerHTML = slider.value;
    };
    sliderButtonL.onclick = function() {
        incrementSlider(slider, -1);
    };
    sliderButtonR.onclick = function() {
        incrementSlider(slider, 1);
    };
}

export function reset(slider) {
    setValue(slider, slider.min);
}

function setValue(slider, newValue) {
    slider.value = newValue;
    slider.oninput();
}

function incrementSlider(slider, delta) {
    var value = parseInt(slider.value);
    var newValue = value + delta;
    if (parseInt(slider.min) <= newValue && newValue <= parseInt(slider.max) && value != newValue) {
        setValue(slider, newValue);
    }
}
