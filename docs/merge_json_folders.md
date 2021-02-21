# JSON to JSON

Merges _several_ folders of `JSON` files into a _single_ folder of `JSON` files based on their file name.

# Steps

Below are the steps needed to run the _merge_ process.
The pathing can be changed by updating the parameters.

Elements are merged in folder order with later folders taking presedence.
I.E. element `id` in file 1 folder 1 will be overwritten by the `id` element in file 1 folder2.
Files that only exist in some, but not all, of the folders will still be merged.

1. Clone this repository.
2. Open a PowerShell window to the `~/code` directory.
3. [Merge](../code/merge_json_folders.py) _several_ folders of `JSON` files into a _single_ folder of `JSON` files based on their file name.
   * The `-in` parameter controls the source folders.
     It is a csv list.
     **NOTE**: only `JSON` files that do not start with `_` will be merged.     
   * The `-out` parameter controls the destination folder.
     If the folder does not exist it is created.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python merge_json_folders.py -in d:/foo,d:/bar -out d:/baz
   ```
