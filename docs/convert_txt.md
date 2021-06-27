# TXT to TXT

Convert a folder of `TXT` files into a folder of _bigger_ `TXT` files.

Files are foramtted as "--- {source file stem} --- \n\n{source file body}'.
The source file's body will retain line breaks.

# Steps

Below are the steps needed to run the _conversion_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/src` directory.
3. [Convert](../src/convert_txt.py) a folder of `TXT` files into a folder of _bigger_ `TXT` files.
   * The `-in`/`-out` parameters control the source and destination folders.
     If the output folder does not exist it is created.
     **WARNING**: If the output folder _does exist AND is not empty_, new `TXT` files will overwrite old ones.
   * The `-s` parameter controls the output file name's stem.
     I.E. `f'./{stem}.{count}.txt'`.
     It defaults to 'stacked'.
   * The `-l` parameter controls how many lines (approxmitly) per new file.
     It defaults to 100k.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python convert_txt.py -in d:/corpus_in -out d:/corpus_out
   ```
