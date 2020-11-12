# Building Blocks

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)

Below is a list of the corpus tools we use at QWikIntelligence.
They are intended to be general purpose building blocks allowing for conversion between our different processes.
Each tool should be considered stand-alone and includes both code (`~/code`) and documentation (`~/docs`).
There is a _combined_ `requirements.txt` file for all the tools found in `~/code`.
The documentation will include both instructions as to what the code is for and how to run it.

## Scripts

Unless otherwise noted, all scripts follow the same execution path.

1. Open a command prompt
2. Change into the `~/code` folder.
3. Run `python {{scriptname}}.py -in d:/corpus_in -out d:/corpus_out`.
   You should change the input and output paths as desired.

The list of current scripts is below.

**Formatting**

1. [aggregate-files](./docs/aggregate-files.md)
2. [corpus-to-json](./docs/corpus-to-json.md)
