import pathlib
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def combine_txt_to_jsonl(folder_in: pathlib.Path, jsonl_out: pathlib.Path, sub_process_count: int) -> None:
    """
    Combines a folder of `TXT` files into a single `JSONL` file.

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
        extract = u.list_folder_documents, extract_args = (folder_in, _is_txt_document),
        transform = _process_document,
        save = _save_documents_to_jsonl, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _is_txt_document(file_path: pathlib.Path) -> bool:
    """
    Determins if the file should be included in the processing
    """
    result = \
        file_path.is_file() and \
        file_path.suffix.lower() == '.txt' and \
        not file_path.stem.startswith('_')
    return result

@typechecked
def _process_document(document_path: str) -> dict:
    """
    Converts the flat text file into a JSON object containing the base elements we use in our processes
    """
    document_path = pathlib.Path(document_path)
    encoding = u.guess_encoding(document_path)
    with open(document_path, 'r', encoding = encoding) as fp:
        lines = fp.readlines()
    if encoding == 'utf-8' and lines[0][0] == '\ufeff':
        lines[0] = lines[0][1:]
    lines = [line.strip() for line in lines]
    json = { 'id' : document_path.name, 'text' : lines }
    return json

@typechecked
def _save_documents_to_jsonl(results: t.Iterator[dict], jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant data to disk
    """
    with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for item in results:
                if len(item['text']) > 0:
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
    combine_txt_to_jsonl(args.folder_in, args.jsonl_out, args.sub_process_count)
