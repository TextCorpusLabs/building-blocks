import pathlib
import json
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def extract_txt_from_jsonl(jsonl_in: pathlib.Path, folder_out: pathlib.Path, id_element: str, extract: t.List[str], sub_process_count: int) -> None:
    """
    Extracts a folder of `TXT` files from a `JSONL` file.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    folder_out : pathlib.Path
        The folder containing all the documents after being extracted
    id_element : str
        The name of the element to use as a file name
    extract : List[str]
        The name(s) of the elements to extract
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    folder_out.mkdir(parents = True, exist_ok = True)

    worker = mpb.EPTS(
        extract = u.list_jsonl_documents, extract_args = (jsonl_in),
        transform = _save_txt_document, transform_init = _passthrough, transform_init_args = (str(folder_out), id_element, extract),
        save = u.drain_iterator,
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _save_txt_document(state:t.Tuple[str, str, t.List[str]], document: dict) -> int:
    """
    Saves the `TXT` document

    Parameters
    ----------
    state : tuple
        [0] The output folder
        [1] The element to use as a file name
        [2] The elements to extract
    document : dict
        The document to be saved
    """
    if state[1] in document:
        file_name = pathlib.Path(state[0]).joinpath(f'./{document[state[1]]}.txt')
        with open(file_name, 'w', encoding = 'utf-8') as fp:
            for elm in state[2]:
                if elm in document:
                    lines = _value_to_lines(document[elm])
                else:
                    lines = _value_to_lines(None)
                fp.writelines(lines)
    return 0

@typechecked
def _value_to_lines(value: t.Any) -> t.List[str]:
    """
    Converts a value of unknow type into lines for the `TXT` file
    """
    if value == None:
        value = ''
    if type(value) == list:
        if len(value) == 0:
            value = ['']
        v1 = value[0]
        if type(v1) == list:
            value = [' '.join(vn) for vn in value]
        return [f'{vn}\n' for vn in value]
    else:
        return [f'{value}\n']

@typechecked
def _passthrough(folder_out: str, id_element: str, extract: t.List[str]) -> t.Tuple[str, str, t.List[str]]:
    """
    Pass the state from the main thread to the single document processing function
    """
    result = (folder_out, id_element, extract)
    return result

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
        '-e', '--extract',
        help = 'The name(s) of the elements to extract',
        type = u.csv_list,
        required = True)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'jsonl in: {args.jsonl_in}')
    print(f'folder out: {args.folder_out}')
    print(f'id element: {args.id_element}')
    print(f'extract: {args.extract}')
    print(f'sub process count: {args.sub_process_count}')
    extract_txt_from_jsonl(args.jsonl_in, args.folder_out, args.id_element, args.extract, args.sub_process_count)
