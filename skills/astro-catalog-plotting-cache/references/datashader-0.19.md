# Datashader 0.19 density rendering

Use this reference when millions of points make Matplotlib hexbin or scatter
inappropriate and the installed Datashader API is in the 0.19 series.

## Dask-backed rendering

Project columns before reading:

```python
import dask.dataframe as dd
import datashader as ds
import datashader.transfer_functions as tf

ddf = dd.read_parquet("cache/*.parquet", columns=["bprp0", "mg0"])
ddf = ddf.dropna(subset=["bprp0", "mg0"])
canvas = ds.Canvas(
    plot_width=1200,
    plot_height=1000,
    x_range=(-1, 5),
    y_range=(15, -5),
)
aggregate = canvas.points(ddf, "bprp0", "mg0", agg=ds.count())
image = tf.shade(
    aggregate,
    cmap=["#f7fbff", "#6baed6", "#08306b"],
    how="log",
)
image.to_pil().save("cmd_datashader.png")
```

Setting a descending `y_range` expresses the astronomical magnitude convention without
post-hoc image flipping.

## Version-specific cautions

- `Canvas.points(..., agg=ds.count())` is the density path; do not assume
  `Canvas.hexbin()` exists.
- `tf.shade()` accepts a list of color strings reliably. If passing a Matplotlib
  colormap object, test it against the installed release.
- The result is a Datashader `Image`; use `.to_pil()` for a portable image conversion.
- Avoid extracting undocumented packed `uint32` channels unless profiling proves that
  conversion is a bottleneck.
- If the image will be placed inside Matplotlib, verify origin and axis orientation with
  a tiny asymmetric test dataset first.

## Verification

- Render a small known subset before the full catalog.
- Confirm low and high density regions differ visibly under log shading.
- Check axis orientation and magnitude inversion.
- Record data ranges, canvas dimensions, aggregation, colormap, and Datashader version
  in the provenance sidecar.
