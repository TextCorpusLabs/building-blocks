import pathlib
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from nltk.tokenize import word_tokenize, sent_tokenize
from typeguard import typechecked

@typechecked
def tokenize_jsonl(jsonl_in: pathlib.Path, jsonl_out: pathlib.Path, id_element: str, tokens: t.List[t.Tuple[str,str]], sub_process_count: int) -> None:
    """
    Tokenizes all the files into the standard form: one sentence per line, paragraphs have a blank line between them.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the files
    jsonl_out : pathlib.Path
        The JSONL containing all the files after tokenization
    id_element : str
        The name of the element used for correlation between processed files
    tokens : List[(str,str)]
        Run the algorithm over these elements
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = _collect_documents, extract_args = (jsonl_in),
        transform = _tokenize_document, transform_init = _passthrough, transform_init_args = (id_element, tokens),
        save = _save_documents_to_jsonl, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _collect_documents(jsonl_in: pathlib.Path) -> t.Iterator[dict]:
    with open(jsonl_in, 'r', encoding = 'utf-8') as fp:
        with jl.Reader(fp) as reader:
            for item in reader:
                yield item

@typechecked
def _passthrough(id_element: str, tokens: t.List[t.Tuple[str,str]]) -> t.Tuple[str, t.List[t.Tuple[str,str]]]:
    """
    Parameters
    ----------
    id_element : str
        The name of the element used for correlation between processed files
    tokens : List[(str,str)]
        Passthrough
    """
    return (id_element, tokens)

@typechecked
def _tokenize_document(state: t.Tuple[str, t.List[t.Tuple[str,str]]], document: dict) -> dict:
    """
        Parameters
    ----------
    state : tuple
        [0] The PK
        [1] The elements to tokenize
    document : dict
        The document in question
    """

    pk = state[0]
    tokens = state[1]

    json = {}
    json[pk] = document[pk]

    for token in tokens:
        lines = [line for line in _tokenize_lines(document[token[0]])]
        json[token[1]] = lines
    return json

@typechecked
def _tokenize_lines(lines: t.List[str]) -> t.Iterator[str]:
    """
    Tokenizes all the lines into paragraphs/words using standard Punkt + Penn Treebank tokenizers
    """

    for line in lines:
        line = line.strip()
        if line == '':
            yield ''
        else:
            sentences = sent_tokenize(line)
            for sentence in sentences:
                words = word_tokenize(sentence)
                yield ' '.join(words)

@typechecked
def _save_documents_to_jsonl(results: t.Iterator[dict], jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant data to disk
    """
    with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for item in results:
                writer.write(item)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'The JSONL containing all the documents after tokenization',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-id', '--id-element',
        help = 'The name of the element used for correlation between processed files',
        type = str,
        default = 'id')
    parser.add_argument(
        '-t', '--tokens',
        help = 'The target input element',
        type = u.csv_tuple,
        default = 'text:tokenized')
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'jsonl in: {args.jsonl_in}')
    print(f'jsonl out: {args.jsonl_out}')
    print(f'id element: {args.id_element}')
    print(f'tokens: {args.tokens}')
    print(f'sub process count: {args.sub_process_count}')
    tokenize_jsonl(args.jsonl_in, args.jsonl_out, args.id_element, args.tokens, args.sub_process_count)
