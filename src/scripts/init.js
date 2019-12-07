import * as slider from './slider.js';

var sliderElement;
for (sliderElement of document.getElementsByClassName('slider')) {
    slider.updateLabel(sliderElement);
}
