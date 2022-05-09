from threading import Thread

from flask import Flask
from werkzeug.serving import make_server


app = Flask(__name__, static_url_path='')


@app.route('/', defaults={'group': None, 'page': None})
@app.route('/profile')
@app.route('/states')
@app.route('/edit-pages')
@app.route('/plugins')
@app.route('/pages/<group>/<page>')
def serve(group=None, page=None):
    return app.send_static_file('index.html')


class AppServer:
    def __init__(self, port=None):
        self.server = make_server('0.0.0.0', port, app, threaded=True)
        self.context = app.app_context()
        self.context.push()

        self.thread = Thread(target=self.server.serve_forever)

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.thread.join()


if __name__ == '__main__':
    app.run()
