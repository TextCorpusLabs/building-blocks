# JSONL to JSONL

Convert a `JSONL` file into a _smaller_ `JSONL` file by keeping only some elements.

# Steps

Below are the steps needed to run the _conversion_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/code` directory.
3. [Convert](../code/convert_jsonl.md) a `JSONL` file into a _smaller_ `JSONL` file by keeping only some elements.
   * The `-in`/`-out` parameters control the source and destination file.
     If the output folder does not exist it is created.
   * The `-k` parameter is used to select the elements to keep.
     It is a csv list.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python convert_jsonl.py -in d:/corpus_in.jsonl -out d:/corpus_out.jsonl -k id,text
   ```
