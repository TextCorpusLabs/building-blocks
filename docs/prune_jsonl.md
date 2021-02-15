# JSONL to JSON

Extract elments from a `JSONL` file making a _smaller_ `JSONL` file.

# Steps

Below are the steps needed to run the _extraction_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/code` directory.
3. [Extract](../code/prune_jsonl.md) elments from a `JSONL` file making a _smaller_ `JSONL` file.
   * The `-in`/`-out` parameters control the source and destination file.
     If the output folder does not exist it is created.
   * The `-e` parameter is used to select the elements to extract.
     It is a csv list.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python prune_jsonl.py -in d:/corpus_in.jsonl -out d:/corpus_out.jsonl -e id,text
   ```
