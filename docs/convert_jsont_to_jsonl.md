# JSONT to JSONL

Convert a `JSONT` file into a `JSONL` file.
A `JSONL` file is a single file with the extension of `.jsonl` that contains several _individual_ `JSON` documents, one per line.
A `JSONT` file is a single `tar` file that contains only _individual_ `JSON` documents, one per file.

# Steps

Below are the steps needed to run the _conversion_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/src` directory.
3. [Convert](../src/convert_jsont_to_jsonl.py) a `JSONT` file into a `JSONL` file.
   * The `-in`/`-out` parameters control the source and destination files.
     **WARNING**: If the output file exists, it is deleted.
   ```{ps1}
   python convert_jsont_to_jsonl.py -in d:/corpus_in.jsont -out d:/corpus_out.jsonl
   ```
