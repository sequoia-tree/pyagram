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
    # TODO: Wrap the next few lines in a try-except-then clause, in case you encounter an error that is not a PyagramError.
    pyagram = pg.Pyagram(code, debug=False)
    if not pyagram.is_error:
        rd.render_components(pyagram.data)
    return json.dumps(pyagram.serialize())

if __name__ == '__main__':
    app.run()
