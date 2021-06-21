# Deliberate Export

In this tutorial we will use Tiled to export data in a variety of
common formats for use by some external software (i.e. not Python).

To follow along, start the Tiled server with the demo Catalog from a Terminal.

```
tiled serve pyobject --public tiled.examples.generated:demo
```

The Tiled server can encode its structures structures in various formats.
These are just a couple of the supported formats:

```python
# Table
catalog["dataframes"]["df"].export("table.xlsx")  # Excel
catalog["dataframes"]["df"].export("table.csv")  # CSV

# Array
catalog["arrays"]["medium"].export("numbers.csv")  # CSV
catalog["arrays"]["medium"].export("image.png")  # PNG image
catalog["arrays"]["medium"].export("image.tiff")  # TIFF image
```

It's possible to select a subset of the data to only "pay" for what you need.

```python
# Export just some of the columns...
catalog["dataframes"]["df"].export("table.csv", columns=["A", "B"])

# Export an N-dimensional slice...
catalog["arrays"]["medium"].export("numbers.csv", slice=[0])  # like arr[0]
catalog["arrays"]["medium"].export("numbers.csv", slice=numpy.s_[:10, 100:200])  # like arr[:10, 100:200]
```

In the examples above, the desired format is automatically detected from the
file extension (`table.csv` -> `csv`). It can also be specified explicitly.

```python
# Format inferred from filename...
catalog["dataframes"]["df"].export("table.csv")

# Format given as a file extension...
catalog["dataframes"]["df"].export("table.csv", format="csv")

# Format given as a media type (MIME)...
catalog["dataframes"]["df"].export("table.csv", format="text/csv")
```

## Supported Formats

To list the supported formats for a given structure:

```py
catalog["dataframes"]["df"].formats
```

**It is easy to add formats and customize the details of how they are exported,
so the list of supported formats will vary** depending on whose Tiled service
you are connected to and how it has been configured.

*Out of the box*, Tiled currently supports:

Array:

* C-ordered memory buffer `application/octet-stream`
* JSON `application/json`
* CSV `text/csv`
* PNG `image/png`
* TIFF `image/tiff`
* HTML `text/html`

DataFrame:
* Apache Arrow `vnd.apache.arrow.file`
* CSV `text/csv`
* HTML `text/html`
* Excel (xlsx) `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

Xarray Dataset:
* NetCDF `application/netcdf`
* The DataFrame formats, by transforming `to_dataframe()`, which may or may not
  be an appropriate transformation depending on your data.

```{note}
The support the full list of formats, the machine that is running `tiled serve ...`
needs to have the relevant I/O libraries installed (e.g. `tifffile` for TIFF,
`pillow` for PNG). If they aren't installed, `tiled serve ...` will detect that
and omit them from the list of supported formats.

**The *user* (client) does *not* need to have any I/O libraries.**
Because the service does all the encoding and just sends opaque bytes for the
client to save, a user can write TIFF files (for example) without actually
having any TIFF-writing Python library installed!
```

## Export to an open file or buffer 

It is also possible to export directly into an open file (or any writeable
buffer) in which case the format must be specified.

```python
# Writing directly to an open file
with open("table.csv", "wb") as file:
    catalog["dataframes"]["df"].export(file, format="csv")

# Writing to a buffer
from io import BytesIO

buffer = BytesIO()
catalog["dataframes"]["df"].export(buffer, format="csv")
```

## Limitations

While it is easy to add or change the set exporters, the user does not have
any options for customizing the output of a given exporter. For example, while
the CSV export *does* let the user choose which columns to export, it does
*not* let the user rename the column headings or choose a different value
separator from the default (`,`). Tiled focuses on getting you the precisely
data you want, not on formatting it "just so". To do more refined export, use
standard Python tools, as in:

```python
df = catalog["dataframes"]["df"].read()
# At this point we are done with Tiled. From here, we just use pandas,
# or whatever we want.
df.to_csv("table.csv", sep=";", header=["custom", "column", "headings"])
```

Or else add or change the exporters provided by the service to better suit your
needs.

## Consider: Is there a better way? 

If your data analysis is taking place in Python, then you may have
no need to export files. Your code will be faster and simpler if you
work directly with numpy, pandas, and/or xarray structures directly.

If your data analysis is in another language, can it access the data
from the Tiled server directly over HTTP? Tiled supports efficient
formats (e.g. numpy C buffers, Apache Arrow DataFrames) and universal
interchange formats (e.g. CSV, JSON) and perhaps one of those will be the
fastest way to get data into your program.

## Comparison to caching

This tutorial demonstrated *deliberate export*, where Tiled generates a file on
disk and leaves it to the user to manage that file and do something with it
outside of Tiled. This is different from {doc}`caching`, where Tiled takes
control of a local cache of data in order to improve Tiled's own operation.
