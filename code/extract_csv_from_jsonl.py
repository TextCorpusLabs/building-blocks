import csv
import pathlib
import json
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def extract_csv_from_jsonl(jsonl_in: pathlib.Path, csv_out: pathlib.Path, extract: t.List[str], sub_process_count: int) -> None:
    """
    Extracts a `CSV` file from a `JSONL` file. 

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    csv_out : pathlib.Path
        The CSV file containing all the documents
    extract : List[str]
        The name(s) of the elements to extract
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if csv_out.exists():
        csv_out.unlink()

    worker = mpb.EPTS(
        extract = u.list_jsonl_documents, extract_args = (jsonl_in),
        transform = _extract_document, transform_init = _passthrough, transform_init_args = (extract),
        save = _save_documents, save_args = (csv_out, extract),
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
            value = document[elm]
            if type(value) == list:
                if len(value) == 0:
                    value = ''
                else:
                    v1 = value[0]
                    if type(v1) == list:
                        value = ' '.join([' '.join(vn) for vn in value])
                    else:
                        value = ' '.join(value)
            result[elm] = value
    return result

@typechecked
def _passthrough(extract: t.List[str]) -> t.List[str]:
    """
    Pass the state from the main thread to the single document processing function
    """
    return extract

@typechecked
def _save_documents(documents: t.Iterator[dict], csv_out: pathlib.Path, extract: t.List[str]) -> None:
    """
    Saves the documents to CSV
    
    Parameters
    ----------
    documents : Iterator[dict]
        The `dict`s to save
    csv_out : pathlib.Path
        The CSV file containing all the documents
    extract : List[str]
        The name(s) of the elements to extract
    """
    with open(csv_out, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)    
        writer.writerow(extract)
        for document in documents:
            row = [None] * len(extract)
            for i in range(0, len(extract)):
                if extract[i] in document:
                    row[i] = document[extract[i]]
            writer.writerow(row)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--csv-out',
        help = 'The CSV file containing all the documents',
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
    print(f'csv out: {args.csv_out}')
    print(f'extract: {args.extract}')
    print(f'sub process count: {args.sub_process_count}')
    extract_csv_from_jsonl(args.jsonl_in, args.csv_out, args.extract, args.sub_process_count)
