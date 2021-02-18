# JSONL to JSON

Extracts a `CSV` file from a `JSONL` file.

# Steps

Below are the steps needed to run the _extraction_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/code` directory.
3. [Extract](../code/extract_csv_from_jsonl.py) a `CSV` file from a `JSONL` file.
   * The `-in`/`-out` parameters control the source and destination file.
     If the output folder does not exist it is created.
   * The `-e` parameter is used to select the elements to extract.
     It is a csv list.
     `List`s will be converted to by concating the values together with a space.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python extract_csv_from_jsonl.py -in d:/corpus.jsonl -out d:/corpus.csv -e id,text
   ```
