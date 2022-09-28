import pathlib
import utils_jsonl as ul
import utils_jsont as ut
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def convert_jsont_to_jsonl(jsont_in: pathlib.Path, jsonl_out: pathlib.Path) -> None:
    """
    Converts a `JSONT` file into a `JSONL` file.

    Parameters
    ----------
    jsont_in : pathlib.Path
        JSONT file containing the aggregated corpus
    jsonl_out : pathlib.Path
        JSONL file containing the aggregated corpus
    """
    if jsonl_out.exists():
        jsonl_out.unlink()
    documents = ut.list_documents(jsont_in)
    ul.save_documents(jsonl_out, documents)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsont-in',
        help = 'The JSONT file containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'The JSONL file containing all the documents',
        type = pathlib.Path,
        required = True)
    args = parser.parse_args()
    print(' --- convert_jsonl ---')
    print(f'jsont in: {args.jsont_in}')
    print(f'jsonl out: {args.jsonl_out}')
    print(' ---------')
    convert_jsont_to_jsonl(args.jsont_in, args.jsonl_out)
