import pathlib
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def merge_txt_folders(folders_in: t.List[pathlib.Path], folder_out: pathlib.Path, sub_process_count: int) -> None:
    """
    Merges _several_ folders of `TXT` files into a _single_ folder of `TXT` files based on their file name.

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
        extract = u.list_merged_folder_documents, extract_args = (folders_in, u.is_txt_document),
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
    document_paths = [pathlib.Path(document_path) for document_path in document_paths]
    file_name = pathlib.Path(state).joinpath(document_paths[0].name)
    with open(file_name, 'w', encoding = 'utf-8') as fpout:
        for i in range(0, len(document_paths)):
            encoding = u.guess_encoding(document_paths[i])
            with open(document_paths[i], 'r', encoding = encoding) as fpin:
                lines = fpin.readlines()
            if encoding == 'utf-8' and lines[0][0] == '\ufeff':
                lines[0] = lines[0][1:]
            footer = ['\n'] if i < len(document_paths)-1 else []
            fpout.writelines(lines + footer)

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
    merge_txt_folders([pathlib.Path(folder) for folder in args.folders_in], args.folder_out, args.sub_process_count)
