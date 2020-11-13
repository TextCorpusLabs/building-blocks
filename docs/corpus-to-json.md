# Corpus to JSON

A corpus is a collection of documents.
When embodied in electronic form, this usually means a folder with one document per file.
When a corpus is large (millions of documents), a non-trivial amount of time may be required to open the file and start processing.

This process seeks to reduce that overhead by combining several files into a single much larger JSON file.
The hope is that a single large file can be moved through our other processes more efficiently than a million small files.
This has the added benefit over [aggregate-files](./aggregate-files.md) in that other processes have an easet time integrating.

## Run the script

The script is run in a similar manor to the [general form](../README.md#scripts).
Run `python corpus-to-json.py -in d:/corpus_in -out d:/corpus.jsonl` where `corpus_in` is a folder and `corpus.jsonl` will be overwritten.
