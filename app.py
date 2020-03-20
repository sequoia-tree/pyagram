import flask
import json

from src.packages.pyagram import pyagram as pg
from src.packages.renderer import render as rd

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
        )
    return root

def render_draw(app):
    @app.route('/draw')
    def draw(methods=['GET', 'POST']):
        code = flask.request.values.get('code')
        pyagram = pg.Pyagram(code, debug=True) # TODO: Set debug=False.
        if pyagram.encoding == 'pyagram':
            rd.render_components(pyagram.data)
        return json.dumps(pyagram.serialize())
    return draw

app = flask.Flask(__name__)
render_endpoints(app)
app.run()
