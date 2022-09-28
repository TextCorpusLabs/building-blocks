import pathlib
import utils_jsonl as ul
import utils_jsont as ut
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def convert_jsonl_to_jsont(jsonl_in: pathlib.Path, jsont_out: pathlib.Path) -> None:
    """
    Converts a `JSONL` file into a `JSONT` file.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        JSONL file containing the aggregated corpus
    jsont_out : pathlib.Path
        JSONT file containing the aggregated corpus
    """
    if jsont_out.exists():
        jsont_out.unlink()
    documents = ul.list_documents(jsonl_in)
    ut.save_documents(jsont_out, documents)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL file containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsont-out',
        help = 'The JSONT file containing all the documents',
        type = pathlib.Path,
        required = True)
    args = parser.parse_args()
    print(' --- convert_jsonl ---')
    print(f'jsonl in: {args.jsonl_in}')
    print(f'jsont out: {args.jsont_out}')
    print(' ---------')
    convert_jsonl_to_jsont(args.jsonl_in, args.jsont_out)
