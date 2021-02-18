# JSONL to TXT

Convert a `JSONL` file into a folder of `TXT` files.

# Steps

Below are the steps needed to run the _conversion_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/code` directory.
3. [Convert](../code/jsonl_to_txt.py) the `JSONL` file into a folder of `TXT` files.
   * The `-in`/`-out` parameters control the source file and destination folder.
     If the output folder does not exist it is created.
     **WARNING**: If the output folder _does exist AND is not empty_, new `TXT` files will overwrite old ones.
   * The `-id` parameter is used to select the file name.
     I.E. `f'./{id}.json'`.
     If the `id` element can not be found the file will not be created.
     It defaults to 'id'.
   * The `-e` parameter is used to select the elements to extract.
     It is a csv list.
     Each non-`List` element will go on one line.
     Each `List` element will be one line per item.
     `List` of `List` will be concatinated into a un-nested `List`, seperated by a ' '.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python jsonl_to_txt.py -in d:/corpus.jsonl -out d:/separated_files -e text
   ```
