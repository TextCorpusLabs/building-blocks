import csv
import pathlib
import typing as t
from . import common_types as ct
from . import utils as u

def extract_csv_from_jsonl(source: pathlib.Path, dest: pathlib.Path, fields: t.List[str]) -> None:
    """
    Extracts a `CSV` file from a `JSONL` file. 

    Parameters
    ----------
    source : pathlib.Path
        The JSONL containing all the documents
    dest : pathlib.Path
        The CSV file containing all the documents
    fields : List[str]
        The name(s) of the fields to extract
    """

    if dest.exists():
        dest.unlink()

    if source.is_file():
        source_files = [source]
    else:
        source_files = (pathlib.Path(path) for path in u.list_folder_documents(source, u.is_jsonl_document))
        
    doc_collections = (u.list_jsonl_documents(file) for file in source_files)
    docs = (x for y in doc_collections for x in y)
    docs = (_extract_document(doc, fields) for doc in docs)
    docs = _save_documents(dest, fields, docs)
    docs = u.progress_overlay(docs, 'Processing Document #')
    for _ in docs: pass

def _extract_document(document: ct.Document, fields: t.List[str]) -> ct.Document:
    """
    Extracts parts of the document 

    Parameters
    ----------
    document : dict
        The document to be saved
    fields : List[str]
        The name(s) of the fields to extract
    """
    result: ct.Document = {}
    for elm in fields:
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

def _save_documents(dest: pathlib.Path, fields: t.List[str], documents: t.Iterator[ct.Document]) -> t.Iterator[ct.Document]:
    """
    Saves the documents to CSV
    
    Parameters
    ----------
    dest : pathlib.Path
        The CSV file containing all the documents
    fields : List[str]
        The name(s) of the elements to fields
    documents : Iterator[dict]
        The `dict`s to save
    """
    with open(dest, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)    
        writer.writerow(fields)
        for document in documents:
            row = [None] * len(fields)
            for i in range(0, len(fields)):
                if fields[i] in document:
                    row[i] = document[fields[i]]
            writer.writerow(row)
            yield document
