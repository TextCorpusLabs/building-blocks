# Building Blocks

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)

Below is a list of the corpus tools we use at Text Corpus Labs.
They are intended to be general purpose building blocks allowing for conversion between our different processes.
Each tool should be considered stand-alone and includes both code (`~/code`) and documentation (`~/docs`).
There is a _combined_ `requirements.txt` file for all the tools found in `~/code`.
The documentation will include both instructions as to what the code is for and how to run it.

# Prerequisites

All scripts follow our standard [prerequisite](https://github.com/TextCorpusLabs/getting-started#prerequisites) and [Python](https://github.com/TextCorpusLabs/getting-started#python) instructions.

# Scripts

All script commands are presented in PowerShell syntax.
If you use a different shell, your syntax will be different.

Adding `-O` to the front of any script runs it in "optimized" mode.
This can give as much as a 50% boost in some cases, but prevents errors from making sence.
If there is an error in a run, remove the `-O`, capture the error, and submit an [issue](https://github.com/TextCorpusLabs/building-blocks/issues).

01. [Combine](./docs/combine_json_to_jsonl.md) a folder of `JSON` files into a single `JSONL` file.
02. [Combine](./docs/combine_txt_to_jsonl.md) a folder of `TXT` files into a single `JSONL` file.
03. [Convert](./docs/convert_jsonl.md) elments from a `JSONL` file making a _smaller_ `JSONL` file.
04. [Convert](./docs/convert_txtf.md) a folder of `TXT` files into a folder of _bigger_ `TXT` files.
05. [Extract](./docs/extract_csv_from_jsonl.md) a `CSV` file from a `JSONL` file.
06. [Extract](./docs/extract_itxt_from_jsonl.md) a folder of _interleaved_ `TXT` files from a `JSONL` file.
07. [Extract](./docs/extract_json_from_jsonl.md) a folder of `JSON` files from a a `JSONL` file.
08. [Extract](./docs/extract_txt_from_jsonl.md) a folder of `TXT` files from a `JSONL` file.
09. [Merge](./docs/merge_json_folders.md) _several_ folders of `JSON` files into a _single_ folder of `JSON` files based on their file name.
10. [Merge](./docs/merge_txt_folders.md) _several_ folders of `TXT` files into a _single_ folder of `TXT` files based on their file name.
