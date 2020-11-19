import io
import pathlib
import shutil
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
from argparse import ArgumentParser
from nltk.tokenize import word_tokenize, sent_tokenize
from typeguard import typechecked

@typechecked
def flatten_corpus(jsonl_in: pathlib.Path, folder_out: pathlib.Path, fields: str, separator: str, sub_process_count: int) -> None:
    """
    Tokenizes all the articles into the standard form: one sentence per line, paragraphs have a blank line between them.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the articles
    folder_out : pathlib.Path
        The folder containing all the documents after being collated and flattened
    fields : str
        The fields to be collated
    separator : str
        The separator to use then the field is of type `List[str]`
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if folder_out.exists():
        shutil.rmtree(str(folder_out))
    folder_out.mkdir(parents = True)

    worker = mpb.EPTS(
        extract = _collect_documents, extract_args = (jsonl_in),
        transform = _collate_fields, transform_init = _passthrough, transform_init_args = (fields, separator),
        save = _save_documents, save_args = (folder_out, jsonl_in.stem),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

def _collect_documents(jsonl_in: pathlib.Path) -> t.Iterator[dict]:
    with open(jsonl_in, 'r', encoding = 'utf-16') as fp:
        with jl.Reader(fp) as reader:
            for item in reader:
                yield item

def _passthrough(fields: str, separator: str) -> t.List:
    fields = [field.strip() for field in fields.split(',')]
    result = [fields, separator]
    return result

def _collate_fields(state: t.List, document: dict) -> dict:
    fields = state[0]
    separator = state[1]

    tmp1 = [document[field] for field in fields]
    if _are_equal_length(tmp1):
        new_lines = []
        for i in range(len(tmp1[0])):
            curr_lines = []
            for field in fields:
                curr_line = document[field][i]
                if type(curr_line) is not str:
                    curr_line = separator.join(curr_line)
                curr_lines.append(curr_line)
            new_lines.append(curr_lines)
        json = {
            'id' : document['id'],
            'title' : document['title'],
            'lines': new_lines }
    else:
        json = {
            'id' : document['id'],
            'title' : document['title'],
            'lines': None}
    return json

def _are_equal_length(collection: t.List[t.List]) -> bool:
    l0 = len(collection[0])
    for item in collection:
        if l0 != len(item):
            return False
    return True

def _save_documents(documents: t.Iterator[dict], folder_out: pathlib.Path, stem: str) -> None:
    """
    Writes the relevant data to disk
    """
    curr_file_count = 0
    curr_line_count = 0
    mx_line_count = 100000
    errors = []

    fp = open(_get_name(folder_out, stem, curr_file_count), 'w', encoding = 'utf-16')
    for document in documents:
        if document['lines'] == None:
            errors.append(document['id'])
        else:
            x = _save_document(fp, document)
            curr_line_count = curr_line_count + x
            if curr_line_count > mx_line_count:
                fp.close()
                curr_file_count = curr_file_count + 1
                curr_line_count = 0
                fp = open(_get_name(folder_out, stem, curr_file_count), 'w', encoding = 'utf-16')
    fp.close()
    if len(errors) > 0:
        print(f"Found errors in file(s): {', '.join(errors)}")

@typechecked
def _save_document(fp: io.TextIOWrapper, document: dict) -> int:
    fp.writelines([f"--- { document['id'] } --- { document['title'] } ---\n\n"])
    for lines in document['lines']:
        lines = [f'{line}\n' for line in lines]
        lines.append('\n')
        fp.writelines(lines)
    return len(document['lines'])

def _get_name(folder_out: pathlib.Path, stem: str, curr_file_count: int) -> str:
    name = f'{stem}.{curr_file_count:04d}.txt'
    path = folder_out.joinpath(name)
    return path

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--folder-out',
        help = 'The folder containing all the documents after being collated and flattened',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-f', '--fields',
        help = 'The fields to be collated',
        type = str,
        required = True)
    parser.add_argument(
        '-sep', '--separator',
        help = 'The separator to use then the field is of type `List[str]`',
        type = str,
        default = ' ')
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'jsonl in: {args.jsonl_in}')
    print(f'folder out: {args.folder_out}')
    print(f'fields: {args.fields}')
    print(f'separator: {args.separator}')
    print(f'sub process count: {args.sub_process_count}')
    flatten_corpus(args.jsonl_in, args.folder_out, args.fields, args.separator, args.sub_process_count)
