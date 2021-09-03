# [START gae_python38_app]

from flask import Flask, render_template, request, jsonify
from affine import Affine
import folium
import math
import zarr

app = Flask(__name__, template_folder=".")


@app.route("/api/hello")
def hello_world():
    print("hello")
    return "Hello, World :)"


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template("static/404.html"), 404


dataset = zarr.open("data/dataset.zarr")

# Hard-code the transformation and bounds to increase speed
inverse_transformation = Affine(
    62174.537385176256,
    0.0,
    4420592.416608675,
    0.0,
    -62174.537385176256,
    2636156.5724939094,
)


DATASET_BOUNDS = {
    "left": -71.09972349649745,
    "right": -70.97668277401313,
    "top": 42.39929532829022,
    "bottom": 42.25259540282886,
}


@app.route("/api/gis", methods=["POST"])
def process_coordinates():
    lat = request.json["lat"]
    lng = request.json["lng"]

    if (
        lat < DATASET_BOUNDS["bottom"]
        or lat > DATASET_BOUNDS["top"]
        or lng > DATASET_BOUNDS["right"]
        or lng < DATASET_BOUNDS["left"]
    ):
        return jsonify({"status": "Not Found"})

    x, y = inverse_transformation * (lng, lat)
    pixel_x, pixel_y = (math.floor(x), math.floor(y))
    rgb = dataset[0:3, pixel_x, pixel_y]

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
        results = ((rgb[a] - 5 <= v[a] <= rgb[a] + 5) for a in range(3))

        if False not in results:
            folium_map = folium.Map(
                location=(lat, lng),
                zoom_start=14,
                max_zoom=16,
                min_zoom=12,
                width="70%",
                height="70%",
                left="15%",
            )
            folium.Marker([lat, lng], popup=k).add_to(folium_map)

            folium.raster_layers.ImageOverlay(
                image="static/layers/{}_warped.png".format(k),
                name=k,
                bounds=[
                    [42.28165548654934, -71.100524097098],
                    [42.398047612900534, -70.98068762905207],
                ],
                opacity=0.75,
                interactive=False,
                cross_origin=False,
                zindex=1,
            ).add_to(folium_map)

            folium.LayerControl().add_to(folium_map)

            return jsonify(
                {"status": "OK", "data": k, "folium_map": folium_map._repr_html_()}
            )

    return jsonify({"status": "Not Found"})


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
