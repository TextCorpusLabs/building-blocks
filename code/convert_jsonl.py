import pathlib
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def convert_jsonl(jsonl_in: pathlib.Path, jsonl_out: pathlib.Path, keep: t.List[str], sub_process_count: int) -> None:
    """
    Converts a `JSONL` file into a _smaller_ `JSONL` file by keeping only some elements.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    jsonl_out : pathlib.Path
        The JSONL file containing all the documents
    keep : List[str]
        The name(s) of the elements to keep
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = u.list_jsonl_documents, extract_args = (jsonl_in),
        transform = _convert_document, transform_init = _passthrough, transform_init_args = (keep),
        save = _save_documents, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _convert_document(state: t.List[str], document: dict) -> dict:
    """
    Converts parts of the document 

    Parameters
    ----------
    state : List[str]
        The elements to keep
    document : dict
        The document to be saved
    """
    result = {}
    for elm in state:
        if elm in document:
            result[elm] = document[elm]
    return result

@typechecked
def _passthrough(keep: t.List[str]) -> t.List[str]:
    """
    Pass the state from the main thread to the single document processing function
    """
    return keep

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
    with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
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
        '-k', '--keep',
        help = 'The name(s) of the elements to keep',
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
    print(f'keep: {args.keep}')
    print(f'sub process count: {args.sub_process_count}')
    convert_jsonl(args.jsonl_in, args.jsonl_out, args.keep, args.sub_process_count)
