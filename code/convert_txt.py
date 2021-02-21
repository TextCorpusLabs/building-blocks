import pathlib
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def convert_txt(folder_in: pathlib.Path, folder_out: pathlib.Path, stem: str, max_lines: int, sub_process_count: int) -> None:
    """
    Convert a folder of `TXT` files into a folder of _bigger_ `TXT` files.

    Parameters
    ----------
    folder_in : pathlib.Path
        Folder containing the source documents
    folder_out : pathlib.Path
        The folder containing all the aggreated documents
    stem : str
        The output file's stem
    max_lines : int
        The number of lines per file
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    folder_out.mkdir(parents = True, exist_ok = True)

    worker = mpb.EPTS(
        extract = u.list_folder_documents, extract_args = (folder_in, u.is_txt_document),
        transform = _process_document,
        save = _save_documents, save_args = (folder_out, stem, max_lines),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

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
    json = { 'id' : document_path.stem, 'lines' : lines }
    return json

@typechecked
def _save_documents(documents: t.Iterator[dict], folder_out: pathlib.Path, stem: str, max_lines: int) -> None:
    """
    Buffers the relevant data for later writing
    """
    file_count = 0
    line_count = 0
    buffer = []
    for document in documents:
        buffer.append(document)
        line_count = line_count + len(document['lines'])
        if line_count >= max_lines:
            _flush_buffer(folder_out, stem, file_count, buffer)
            file_count = file_count + 1
            line_count = 0
            buffer = []
    if len(buffer) > 0:
        _flush_buffer(folder_out, stem, file_count, buffer)

@typechecked
def _flush_buffer(folder_out: pathlib.Path, stem: str, count: int, buffer: t.List[dict]) -> None:
    """
    Writes the buffer to disk
    """
    file_name = _get_name(folder_out, stem, count)
    with open(file_name, 'w', encoding = 'utf-8') as fp:
        for i in range(0, len(buffer)):
            document = buffer[i]
            header = [f"--- { document['id'] } --- \n\n"]
            lines = [f'{line}\n' for line in document['lines']]
            footer = ['\n'] if i < len(buffer)-1 else []
            fp.writelines(header + lines + footer)

@typechecked
def _get_name(folder_out: pathlib.Path, stem: str, count: int) -> pathlib.Path:
    """
    Gets the full path of the file for the buffered documents
    """
    name = f'{stem}.{count:04d}.txt'
    path = folder_out.joinpath(name)
    return path

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--folder-in',
        help = 'Folder containing the source documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--folder-out',
        help = 'The folder containing all the aggreated documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-s', '--stem',
        help = 'The output file''s stem',
        type = str,
        default = 'stacked')
    parser.add_argument(
        '-l', '--max-lines',
        help = 'The number of lines per file',
        type = int,
        default = 100000)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'folder in: {args.folder_in}')
    print(f'folder out: {args.folder_out}')
    print(f'stem: {args.stem}')
    print(f'max lines: {args.max_lines}')
    print(f'sub process count: {args.sub_process_count}')
    convert_txt(args.folder_in, args.folder_out, arg.stem, args.max_lines, args.sub_process_count)
