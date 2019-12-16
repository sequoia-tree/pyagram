import flask
import json

from src.packages.pyagram import pyagram as pg
from src.packages.renderer import render as rd

app = flask.Flask(__name__)

@app.route('/')
def root():
    return flask.render_template('index.html')

@app.route('/draw')
def draw(methods=['GET', 'POST']):
    code = flask.request.values.get('code')
    pyagram = pg.Pyagram(code, debug=True) # TODO: Set debug=False.
    if pyagram.encoding == 'pyagram':
        rd.render_components(pyagram.data)
    return json.dumps(pyagram.serialize())

if __name__ == '__main__':
    app.run()
