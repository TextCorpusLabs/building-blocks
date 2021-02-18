# JSON to JSONL

Combine a folder of `JSON` files into a single `JSONL` file.

# Steps

Below are the steps needed to run the _combination_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/code` directory.
3. [Combine](../code/combine_json_to_jsonl.py) a folder of `JSON` files into a single `JSONL` file.
   If the `id` element is not present, the file's name will be added as `id`.
   Files without a BOM are assumed to be 'utf-8'.
   * The `-in`/`-out` parameters control the source folder and destination file.
     If the output folder does not exist it is created.
     **NOTE**: only `JSON` files that do not start with `_` will be combined.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python combine_json_to_jsonl.py -in d:/separated_files -out d:/corpus.jsonl
   ```
