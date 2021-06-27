# JSONL to TXT

Extracts a folder of `TXT` files from a `JSONL` file.

# Steps

Below are the steps needed to run the _extraction_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/src` directory.
3. [Extract](../src/extract_txt_from_jsonl.py) a folder of `TXT` files from a `JSONL` file.
   * The `-in`/`-out` parameters control the source file and destination folder.
     If the output folder does not exist it is created.
     **WARNING**: If the output folder _does exist AND is not empty_, new `TXT` files will overwrite old ones.
   * The `-id` parameter is used to select the file name.
     I.E. `f'./{id}.txt'`.
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
   python extract_txt_from_jsonl.py -in d:/corpus.jsonl -out d:/separated_files -e text
   ```
