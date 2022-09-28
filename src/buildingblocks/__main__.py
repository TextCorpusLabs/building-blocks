import buildingblocks.tools as tools
import buildingblocks.tools.utils as utils
import pathlib
import sys
from argparse import ArgumentParser, Namespace

def main() -> None:
    parser = ArgumentParser(prog = 'buildingblocks', description = "Building blocks for text processing")
    subparsers = parser.add_subparsers(help = 'block-commands')
    extract_block(subparsers.add_parser('extract', help = "pull part of a thing into another"))
    args = parser.parse_args()
    args.run(args)

def extract_block(parser: ArgumentParser) -> None:
    def jsonl_to_csv(parser: ArgumentParser) -> None:
        def run(args: Namespace) -> None:
            tools.extract_csv_from_jsonl(args.source, args.dest, args.e, 1)
        parser.add_argument('-source', type = pathlib.Path, required = True, help = 'The root folder of the folders containing JSONL files')
        parser.add_argument('-dest', type = pathlib.Path, required = True, help = 'The folder to store the converted CSV file')
        parser.add_argument('-e',  type = utils.csv_list, default = 'id', help = 'The format of the JSON file name')
        parser.set_defaults(run = run)
    subparsers = parser.add_subparsers(help = 'sub-commands')
    jsonl_to_csv(subparsers.add_parser('jsonl_to_csv', help = "Pull fields from every JSON object in a JSONL file into a CSV file"))

if __name__ == "__main__":
    sys.exit(main())
