import buildingblocks.tools as tools
import buildingblocks.tools.utils as utils
import pathlib
import sys
from argparse import ArgumentParser, Namespace

def main() -> None:
    parser = ArgumentParser(prog = 'buildingblocks', description = "Building blocks for text processing")
    subparsers = parser.add_subparsers(help = 'block-commands')
    extract_block(subparsers.add_parser('extract', help = "pull part of a thing into another"))
    transform_block(subparsers.add_parser('transform', help = "transform one thing into another"))
    args = parser.parse_args()
    args.run(args)

def extract_block(parser: ArgumentParser) -> None:
    def jsonl_to_csv(parser: ArgumentParser) -> None:
        def run(args: Namespace) -> None:
            tools.extract_csv_from_jsonl(args.source, args.dest, args.fields)
        parser.add_argument('-source', type = pathlib.Path, required = True, help = 'The root folder of the folders containing JSONL files')
        parser.add_argument('-dest', type = pathlib.Path, required = True, help = 'The folder to store the converted CSV file')
        parser.add_argument('-fields',  type = utils.csv_list, default = 'id', help = 'The names of the fields to extract')
        parser.set_defaults(run = run)
    subparsers = parser.add_subparsers(help = 'sub-commands')
    jsonl_to_csv(subparsers.add_parser('jsonl_to_csv', help = "Pull fields from every JSON object in a JSONL file into a CSV file"))

def transform_block(parser: ArgumentParser) -> None:
    def ngram(parser: ArgumentParser) -> None:
        def run(args: Namespace) -> None:
            tools.count_ngrams(args.source, args.dest, args.fields, args.size, args.top, args.chunk, args.keep_case, args.keep_punct)
        parser.add_argument('-source', type = pathlib.Path, required = True, help = 'The root folder of the folders containing JSONL files')
        parser.add_argument('-dest', type = pathlib.Path, required = True, help = 'The folder to store the converted CSV file')
        parser.add_argument('-fields',  type = utils.csv_list, default = 'text', help = 'The names of the fields to process')
        parser.add_argument('-size', type = int, default = 1, help = 'The length of the n-gram')
        parser.add_argument('-top', type = int, default = 10000, help = 'The number of n-grams to save')
        parser.add_argument('-chunk', type = int, default = 10000000, help = 'Controls the amount of n-grams to chunk to disk to prevent OOM')
        parser.add_argument('-keep_case', action = 'store_true', help = 'Keeps the casing of the fields as-is before converting to tokens')
        parser.add_argument('-keep_punct', action = 'store_true', help = 'Keeps all punctuation of the fields as-is before converting to tokens')
        parser.set_defaults(run = run)
    subparsers = parser.add_subparsers(help = 'sub-commands')
    ngram(subparsers.add_parser('ngram', help = "Counts the n-grams in a JSONL file"))

if __name__ == "__main__":
    sys.exit(main())
