import rasterio
from rasterio.windows import Window
import time
import zarr


def convert(raster_filepath, chunk_mbs=1):
    """
    Converts raster file to chunked and compressed zarr array. Tested
    with GeoTIFF format, but should work with other raster formats
    compatible with rasterio
    Parameters
    ----------
    raster_filepath : string
        Path and filename of input raster
    chunk_mbs : float, optional
        Desired size (MB) of chunks in zarr file
    """

    # Open the raster file
    raster = rasterio.open(raster_filepath)

    # Extract metadata we need for initializing the zarr array
    width = raster.width
    height = raster.height
    n_bands = raster.count
    dtype = raster.dtypes[0].lower()

    # Specify the number of bytes for common raster
    # datatypes so we can compute chunk shape
    dtype_bytes = {
        "byte": 1,
        "uint8": 1,
        "uint16": 2,
        "int16": 2,
        "uint32": 4,
        "int32": 4,
        "float32": 4,
        "float64": 8,
    }

    # Compute the chunk shape
    chunk_shape = (int((1e6 / dtype_bytes[dtype]) ** 0.5),) * 2

    # Setup zarr file
    zarray_filepath = f"{'.'.join(raster_filepath.split('.')[:-1])}.zarr"
    zarray = zarr.open(
        zarray_filepath,
        mode="w",
        shape=(height, width, n_bands),
        chunks=chunk_shape,
        dtype=dtype,
    )

    # Let's add the metadata to the zarr file
    zarray.attrs["width"] = width
    zarray.attrs["height"] = height
    zarray.attrs["count"] = n_bands
    zarray.attrs["dtype"] = dtype
    zarray.attrs["bounds"] = raster.bounds
    # zarray.attrs["transform"] = raster.transform
    # zarray.attrs["crs"] = raster.crs.to_string()

    # Loop through bands; raster band indecies starts at 1
    for k in raster.indexes:

        # Now we'll read and write the data according to the chuck size
        # to prevent memory saturation
        for j in range(0, width + chunk_shape[1], chunk_shape[1]):
            print(f"column {j} of {width}")
            j = width if j > width else j
            for i in range(0, height + chunk_shape[0], chunk_shape[0]):
                i = height if i > height else i
                data = raster.read(
                    k, window=Window(j, i, chunk_shape[1], chunk_shape[0])
                )
                zarray[i : i + chunk_shape[0], j : j + chunk_shape[1], k - 1] = data

    # Close the raster dataset; no need to close the zarr file
    raster.close()


convert("9531.tif")
