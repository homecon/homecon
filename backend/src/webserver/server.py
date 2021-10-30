from flask import Flask

app = Flask(__name__, static_url_path='')


@app.route('/', defaults={'group': None, 'page': None})
@app.route('/profile')
@app.route('/states')
@app.route('/edit-pages')
@app.route('/plugins')
@app.route('/pages/<group>/<page>')
def serve(group=None, page=None):
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()
