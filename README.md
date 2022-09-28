# Building Blocks

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![MIT license](https://img.shields.io/badge/License-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-2022.09.28-success.svg)

Below is a list of the corpus tools we use at Text Corpus Labs.
They are intended to be general purpose building blocks allowing for conversion between our different processes.

**NOTE**: This project is currently in the process of undergoing a retrofit.
The below checklist now shows conversion status.
While in progress, the old cold will still work, it is just nested in a subfolder.

# Operation

## Install

You can install the package using the following steps:

1. `pip` install using an _admin_ prompt.
   ```{ps1}
   pip uninstall buildingblocks
   pip install -v git+https://github.com/TextCorpusLabs/building-blocks.git
   ```

## Run

You can run the package in the following ways:

### Extract

01. Pull fields from every JSON object in a JSONL file into a CSV file
   ```{ps1}
   buildingblocks extract jsonl_to_csv `
      -source d:/data/corpus `
      -dest d:/data/corpus.csv `
      -e id,text
   ```


# TODO

All script commands are presented in PowerShell syntax.
If you use a different shell, your syntax will be different.

Adding `-O` to the front of any script runs it in "optimized" mode.
This can give as much as a 50% boost in some cases, but prevents errors from making sense.
If there is an error in a run, remove the `-O`, capture the error, and submit an [issue](https://github.com/TextCorpusLabs/building-blocks/issues).

## Combine
01. - [x] [Combine](./docs/combine_json_to_jsonl.md) a folder of `JSON` files into a single `JSONL` file.
02. - [x] [Combine](./docs/combine_txt_to_jsonl.md) a folder of `TXT` files into a single `JSONL` file.

## Convert
01. - [x] [Convert](./docs/convert_jsonl.md) a `JSONL` file into a _smaller_ `JSONL` file by keeping only some elements.
02. - [x] [Convert](./docs/convert_txt.md) a folder of `TXT` files into a folder of _bigger_ `TXT` files.
03. - [x] [Convert](./docs/convert_jsonl_to_jsont.md) a `JSONL` file into a `JSONT` file.
03. - [x] [Convert](./docs/convert_jsont_to_jsonl.md) a `JSONT` file into a `JSONL` file.

## Extract
02. - [x] [Extract](./docs/extract_itxt_from_jsonl.md) a folder of _interleaved_ `TXT` files from a `JSONL` file.
03. - [x] [Extract](./docs/extract_json_from_jsonl.md) a folder of `JSON` files from a a `JSONL` file.
04. - [x] [Extract](./docs/extract_txt_from_jsonl.md) a folder of `TXT` files from a `JSONL` file.

## Merge
01. - [x] [Merge](./docs/merge_json_folders.md) _several_ folders of `JSON` files into a _single_ folder of `JSON` files based on their file name.
02. - [x] [Merge](./docs/merge_txt_folders.md) _several_ folders of `TXT` files into a _single_ folder of `TXT` files based on their file name.

## Transform
01. - [x] [Count](./docs/count_ngrams.md) the n-grams for a `JSONL` file.
02. - [x] [Tokenize](./docs/tokenize_jsonl.md) a `JSONL` file using the NLTK defaults (Punkt + Penn Treebank).

# Development

## Prerequisites

Install the required modules for each of the repositories.

1. Clone this repository then open an _Admin_ shell to the `~/` directory.
2. Install the required modules.
   ```{shell}
   pip uninstall buildingblocks
   pip install -e c:/repos/TextCorpusLabs/building-blocks
   ```
3. Setup the `~/.vscode/launch.json` file (VS Code only)
   1. Click the "Run and Debug Charm"
   2. Click the "create a launch.json file" link
   3. Select "Python"
   4. Select "module" and enter _buildingblocks_
   5. Select one of the following modes and add the below `args` to the launch.json file.
      The `args` node should be a sibling of the `module` node.
      They may need to be changed for your pathing.
      1. Download
         ```{json}
         "args" : [
           "extract", "jsonl_to_csv",
           "-source", "d:/data/corpus",
           "-dest", "d:/data/corpus.csv",
           "-e", "id,text"]
         ```
