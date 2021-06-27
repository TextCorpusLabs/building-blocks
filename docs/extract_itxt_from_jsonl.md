# JSONL to iTXT

Extracts a folder of _interleaved_ `TXT` files from a `JSONL` file.

The normal [extract](./extract_txt_from_jsonl.md) prints all of one element then all of the next and so on.
This script prints the _ith_ value from _each_ element before print the _i+1_ value.
Therefore, this script is only valid on elements that are `List`s and are the same length.
Any document that does not meet those two conditions is not created.

An _error.log_ file will be made of any offending documents.

# Steps

Below are the steps needed to run the _extraction_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/src` directory.
3. [Extract](../src/extract_itxt_from_jsonl.py) a folder of _interleaved_ `TXT` files from a `JSONL` file.
   * The `-in`/`-out` parameters control the source file and destination folder.
     If the output folder does not exist it is created.
     **WARNING**: If the output folder _does exist AND is not empty_, new `TXT` files will overwrite old ones.
   * The `-id` parameter is used to select the file name.
     I.E. `f'./{id}.json'`.
     If the `id` element can not be found the file will not be created.
     It defaults to 'id'.
   * The `-e` parameter is used to select the elements to extract.
     It is a csv list.
     All elements must be of type `List` and those lists must be the same length.
     `List` of `List` will be concatenated into a un-nested `List`, separated by a ' '.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python extract_itxt_from_jsonl.py -in d:/corpus.jsonl -out d:/separated_files -e text
   ```
