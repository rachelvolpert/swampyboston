# [START gae_python38_app]

from flask import Flask, render_template, request

app = Flask(__name__, template_folder=".")


@app.route("/api/hello")
def hello_world():
    print("hello")
    return "Hello, World :)"


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("static/404.html"), 404


@app.route("/api/gis", methods=["POST"])
def process_coordinates():
    return request.json


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
# [END gae_python38_app]