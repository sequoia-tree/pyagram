import flask

import src.modules.pyagram.pyagram as pg

app = flask.Flask(__name__)

@app.route('/')
def root():
    return flask.render_template('index.html')

@app.route('/draw')
def draw(methods=['GET', 'POST']):
    code = flask.request.values.get('code')
    pyagram = pg.Pyagram(code, debug=False)
    serialized_pyagram = pyagram.serialize()
    return serialized_pyagram

if __name__ == '__main__':
    app.run()
