export function initializeSlider(slider, sliderLabel, sliderButtonL, sliderButtonR, shouldBindKeys, emitValue) {
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
    if (shouldBindKeys) {
        bindArrowKeys(sliderButtonL, sliderButtonR);
    }
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

function bindArrowKeys(sliderButtonL, sliderButtonR) {
    document.onkeydown = function(event) {
        switch (event.keyCode) {
            case 37:
                sliderButtonL.onclick();
                break;
            case 39:
                sliderButtonR.onclick();
                break;
            default:
                break;
        }
    }
}
