# Aggregate files

A corpus is a collection of documents.
When embodied in electronic form, this usually means a folder with one document per file.
When a corpus is large (millions of documents), a non-trivial amount of time may be required to open the file and start processing.

This process seeks to reduce that overhead by combining several files into a single much larger file.
The hope is that a single large file can be moved through our other processes more efficiently than a million small files.

## Run the script

The script is run in accordance with the [general form](../README.md#scripts)
