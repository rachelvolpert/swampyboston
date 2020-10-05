# [START gae_python38_app]

from flask import Flask, render_template, request, jsonify
import rasterio

app = Flask(__name__, template_folder=".")


@app.route("/api/hello")
def hello_world():
    print("hello")
    return "Hello, World :)"


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("static/404.html"), 404


dataset = rasterio.open("commonwealth_q524n561v_georectifiedMaster.tif")


@app.route("/api/gis", methods=["POST"])
def process_coordinates():
    lat = request.json["lat"]
    lng = request.json["lng"]

    map_bounds = dataset.bounds

    if (
        lat < map_bounds.bottom
        or lat > map_bounds.top
        or lng > map_bounds.right
        or lng < map_bounds.left
    ):
        return 400

    pixels = dataset.index(lng, lat)
    rgb = [dataset.read(x)[pixels] for x in range(1, 4)]

    map_legend = {
        "original_land_1630": [0, 55, 46],
        "added_1795": [0, 103, 92],
        "added_1852": [74, 126, 115],
        "added_1880": [129, 138, 135],
        "added_1916": [165, 150, 141],
        "added_1934": [194, 150, 137],
        "added_1950": [255, 198, 164],
        "added_1995": [234, 218, 153],
        "water": [152, 197, 215],
        "shoreline_no_changes": [215, 215, 215],
    }

    for k, v in map_legend.items():
        results = [
            True if rgb[a] - 5 <= v[a] <= rgb[a] + 5 else False for a in range(3)
        ]

        if False not in results:
            return jsonify(k)


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