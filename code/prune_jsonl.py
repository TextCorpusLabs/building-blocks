import csv
import pathlib
import json
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def prune_jsonl(jsonl_in: pathlib.Path, jsonl_out: pathlib.Path, extract: t.List[str], sub_process_count: int) -> None:
    """
    Extract elments from a `JSONL` file making a _smaller_ `JSONL` file.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    jsonl_out : pathlib.Path
        The JSONL file containing all the documents
    extract : List[str]
        The name(s) of the elements to extract
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = u._list_jsonl_documents, extract_args = (jsonl_in),
        transform = _extract_document, transform_init = _passthrough, transform_init_args = (extract),
        save = _save_documents, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _extract_document(state: t.List[str], document: dict) -> dict:
    """
    Extracts parts of the document 

    Parameters
    ----------
    state : List[str]
        The elements to extract
    document : dict
        The document to be saved
    """
    result = {}
    for elm in state:
        if elm in document:
            result[elm] = document[elm]
    return result

@typechecked
def _passthrough(extract: t.List[str]) -> t.List[str]:
    """
    Pass the state from the main thread to the single document processing function
    """
    return extract

@typechecked
def _save_documents(documents: t.Iterator[dict], jsonl_out: pathlib.Path) -> None:
    """
    Saves the documents to JSONL
    
    Parameters
    ----------
    documents : Iterator[dict]
        The `dict`s to save
    jsonl_out : pathlib.Path
        The JSONL file containing all the documents
    """
    with open(jsonl_out, 'w', encoding = 'utf-16') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for document in documents:
                writer.write(document)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'The JSONL file containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-e', '--extract',
        help = 'The name(s) of the elements to extract',
        type = u.csv_list,
        default = 'id')
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'jsonl in: {args.jsonl_in}')
    print(f'jsonl out: {args.jsonl_out}')
    print(f'extract: {args.extract}')
    print(f'sub process count: {args.sub_process_count}')
    prune_jsonl(args.jsonl_in, args.jsonl_out, args.extract, args.sub_process_count)
