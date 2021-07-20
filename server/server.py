import os
from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path='')


@app.route('/', defaults={'path': ''})
@app.route('/<path>')
def serve(path):
    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()
