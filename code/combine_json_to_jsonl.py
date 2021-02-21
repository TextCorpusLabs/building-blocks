import json
import pathlib
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def combine_json_to_jsonl(folder_in: pathlib.Path, jsonl_out: pathlib.Path, sub_process_count: int) -> None:
    """
    Combines a folder of `JSON` files into a single `JSONL` file.

    Parameters
    ----------
    folder_in : pathlib.Path
        Folder containing the source documents
    jsonl_out : pathlib.Path
        JSONL containing the aggregated corpus
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = u.list_folder_documents, extract_args = (folder_in, u.is_json_document),
        transform = _process_document,
        save = _save_documents_to_jsonl, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _process_document(document_path: str) -> dict:
    """
    Converts the JSON file into a JSON object containing the base elements we use in our processes
    """
    document_path = pathlib.Path(document_path)
    encoding = u.guess_encoding(document_path)
    with open(document_path, 'r', encoding = encoding) as fp:
        obj = json.load(fp)
    if 'id' not in obj:
        obj['id'] = document_path.stem
    return obj

@typechecked
def _save_documents_to_jsonl(results: t.Iterator[dict], jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant data to disk
    """
    with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for item in results:
                writer.write(item)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--folder-in',
        help = 'Folder containing the source documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'JSONL containing the aggregated corpus',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()
    print(f'folder in: {args.folder_in}')
    print(f'JSONL out: {args.jsonl_out}')
    print(f'sub process count: {args.sub_process_count}')
    combine_json_to_jsonl(args.folder_in, args.jsonl_out, args.sub_process_count)
