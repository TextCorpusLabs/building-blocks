import pathlib
import json
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def extract_json_from_jsonl(jsonl_in: pathlib.Path, folder_out: pathlib.Path, id_element: str, sub_process_count: int) -> None:
    """
    Extracts a folder of `JSON` files from a a `JSONL` file.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    folder_out : pathlib.Path
        The folder containing all the documents after being extracted
    id_element : str
        The name of the element to use as a file name
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    folder_out.mkdir(parents = True, exist_ok = True)

    worker = mpb.EPTS(
        extract = u.list_jsonl_documents, extract_args = (jsonl_in),
        transform = _save_json_document, transform_init = _passthrough, transform_init_args = (str(folder_out), id_element),
        save = _no_op,
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _save_json_document(state:t.Tuple[str, str], document: dict) -> int:
    """
    Saves the `JSON` document

    Parameters
    ----------
    state : tuple
        [0] The output folder
        [1] The element to use as a file name
    document : dict
        The document to be saved
    """
    if state[1] in document:
        file_name = pathlib.Path(state[0]).joinpath(f'./{document[state[1]]}.json')
        with open(file_name, 'w', encoding = 'utf-8') as fp:
            json.dump(document, fp, sort_keys = True, indent = None)
    return 0

@typechecked
def _passthrough(folder_out: str, id_element: str) -> t.Tuple[str, str]:
    """
    Pass the state from the main thread to the single document processing function
    """
    result = (folder_out, id_element)
    return result

@typechecked
def _no_op(completes: t.Iterator[int]) -> None:
    """
    Does nothing.
    We are abusing the "transform" step to do all the writing
    """
    for _ in completes:
        pass

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--folder-out',
        help = 'The folder containing all the documents after being extracted',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-id', '--id-element',
        help = 'The name of the element to use as a file name',
        type = str,
        default = 'id')
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'jsonl in: {args.jsonl_in}')
    print(f'folder out: {args.folder_out}')
    print(f'id element: {args.id_element}')
    print(f'sub process count: {args.sub_process_count}')
    extract_json_from_jsonl(args.jsonl_in, args.folder_out, args.id_element, args.sub_process_count)
