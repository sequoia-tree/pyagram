import flask
import json

from src.packages.pyagram import pyagram as pg

def render_endpoints(app):
    render_root(app)
    render_draw(app)

def render_root(app):
    @app.route('/')
    def root():
        return flask.render_template(
            'index.html',
            split_panels=[
                ('input', 'template', None),
                ('output', 'template', None),
            ],
            output_panels=[
                ('pyagram', 'template', None),
                ('print-output', 'template', None),
            ],
            # TODO: Most of your templating kwargs are scattered in various HTML files. Consolidate them here.
            # TODO: Refactor the front-end stuff too!
            # TODO: You have pyagram.html and pyagram-unified.html; you should have a pyagram-divided.html too.
        )
    return root

def render_draw(app):
    @app.route('/draw')
    def draw(methods=['GET', 'POST']):
        code = flask.request.values.get('code')
        pyagram = pg.Pyagram(code, debug=True) # TODO: Set debug=False.
        return json.dumps(pyagram.serialize())
    return draw

if __name__ == '__main__':
    app = flask.Flask(__name__)
    render_endpoints(app)
    app.run()
