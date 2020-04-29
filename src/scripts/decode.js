export function decodePyagramSnapshot(pyagramSnapshot) {
    var template = Handlebars.compile("Handlebars <b>{{doesWhat}}</b>");
    console.log(template({ doesWhat: "rocks!" }));
    // TODO: Okay it looks like Handlebars works!
    // TODO: Before moving on, switch to loading ACE via CDN instead.
    // TODO: Maybe also split.js?
}
