from flask import Flask  # Import flask

app = Flask(__name__, static_url_path='')  # Setup the flask app by creating an instance of Flask


@app.route('/')  # When someone goes to / on the server, execute the following function
def home():
    return app.send_static_file('index.html')


if __name__ == '__main__':  # If the script that was run is this script (we have not been imported)
    app.run()  # Start the server
