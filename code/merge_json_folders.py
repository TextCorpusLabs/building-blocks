import json
import pathlib
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def merge_json_folders(folders_in: t.List[pathlib.Path], folder_out: pathlib.Path, sub_process_count: int) -> None:
    """
    Merges _several_ folders of `JSON` files into a _single_ folder of `JSON` files based on their file name.

    Parameters
    ----------
    folders_in : List[pathlib.Path]
        Folders containing the documents to merge 
    folder_out : pathlib.Path
        Folder containing the merged documents
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    folder_out.mkdir(parents = True, exist_ok = True)

    worker = mpb.EPTS(
        extract = u.list_merged_folder_documents, extract_args = (folders_in, u.is_json_document),
        transform = _merge_documents, transform_init = _passthrough, transform_init_args = (str(folder_out)),
        save = u.drain_iterator,
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _merge_documents(state: str, document_paths: t.List[str]) -> int:
    """
    Merges the documents 

    Parameters
    ----------
    state : str
        The output folder
    document_paths : list[str]
        The documents to be merged
    """
    result = {}
    document_paths = [pathlib.Path(document_path) for document_path in document_paths]
    for document_path in document_paths:
        encoding = u.guess_encoding(document_path)
        with open(document_path, 'r', encoding = encoding) as fp:
            obj = json.load(fp)
        for k, v in obj.items():
            result[k] = v
    file_name = pathlib.Path(state).joinpath(document_paths[0].name)
    with open(file_name, 'w', encoding = 'utf-8') as fp:
        json.dump(result, fp, sort_keys = True, indent = None)

    return 0

@typechecked
def _passthrough(folder_out: str) -> str:
    """
    Pass the state from the main thread to the mergeing function
    """
    return folder_out

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--folders-in',
        help = 'Folders containing the documents to merge ',
        type = u.csv_list,
        required = True)
    parser.add_argument(
        '-out', '--folder-out',
        help = 'Folder containing the merged documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()
    print(f'folders in: {args.folders_in}')
    print(f'folder out: {args.folder_out}')
    print(f'sub process count: {args.sub_process_count}')
    merge_json_folders([pathlib.Path(folder) for folder in args.folders_in], args.folder_out, args.sub_process_count)
