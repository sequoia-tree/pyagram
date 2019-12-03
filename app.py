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
    # TODO: Wrap the next two lines in a try-except-then clause.
    pyagram = pg.Pyagram(code, debug=False)
    rd.render_components(pyagram.snapshots)
    return json.dumps(pyagram.snapshots)

if __name__ == '__main__':
    app.run()
