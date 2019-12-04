function incrementSlider(id, n) {
    var slider = document.getElementById(id);
    var newValue = parseInt(slider.value) + n;
    if (parseInt(slider.min) <= newValue <= parseInt(slider.max)) {
        // TODO
    }
}
