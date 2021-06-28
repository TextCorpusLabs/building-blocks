import csv
import pathlib
import progressbar as pb
import typing as t
import utils as u
import utils_jsonl as ul
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def count_ngrams(jsonl_in: pathlib.Path, csv_out: pathlib.Path, size: int, top: int, fields: t.List[str]) -> None:
    """
    Calculate the n-grams for a `JSONL` file.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        JSONL file containing the aggregated corpus
    csv_out : pathlib.Path
        The csv file containing the n-grams
    size :  int
        The size of the n-grams
    top : int
        The amount of top n-grams for saving
    fields : List[str]
        The field(s) used to extract n-grams
    """
    if csv_out.exists():
        csv_out.unlink()
    counts = _count_ngram(jsonl_in, size, fields)
    min = _min_count(counts, top)
    _save_counts(counts, csv_out, min)

@typechecked
def _count_ngram(jsonl_in: pathlib.Path, size: int, fields: t.List[str]) -> dict:
    counts = {}
    bar_i = 0
    widgets = [ 'Counting Documents # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for document in ul.list_documents(jsonl_in):
            _update_ngram_counts(document, fields, size, counts)
            bar_i = bar_i + 1
            bar.update(bar_i)
    return counts

@typechecked
def _update_ngram_counts(document: dict, fields: t.List[str], size: int, counts: dict) -> None:
    for field in fields:
        if field in document:
            for line in document[field]:
                tokens = line.split(' ')
                for i in range(len(tokens) - size + 1):
                    token = ' '.join(tokens[i:(i+size)])
                    token = token.upper()
                    if token not in counts:
                        counts[token] = 0
                    counts[token] = counts[token] + 1
@typechecked
def _min_count(counts: dict, top: int) -> int:
    min = 0
    i = 0
    for v in sorted(counts.values(), reverse = True):
        min = v
        i = i + 1
        if i > top:
            break
    return min

@typechecked
def _save_counts(counts: dict, csv_out: pathlib.Path, min: int) -> None:
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
    bar_i = 0
    widgets = [ 'Saving n-grams # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        with open(csv_out, 'w', encoding = 'utf-8', newline = '') as fp:
            writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)    
            writer.writerow(['count', 'ngram'])
            for key, value in counts.items():
                if value >= min:
                    writer.writerow([value, key])
                    bar_i = bar_i + 1
                    bar.update(bar_i)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL file containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--csv-out',
        help = 'The csv file containing all the n-grams',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-n', '--size',
        help = 'The size of the n-grams',
        type = int,
        required = True)
    parser.add_argument(
        '-t', '--top',
        help = 'The amount of top n-grams for saving',
        type = int,
        required = True)
    parser.add_argument(
        '-f', '--fields',
        help = 'The field(s) used to extract n-grams',
        type = u.csv_list,
        default = 'text')
    args = parser.parse_args()
    print(' --- count_ngrams ---')
    print(f'jsonl in: {args.jsonl_in}')
    print(f'csv out: {args.csv_out}')
    print(f'size: {args.size}')
    print(f'top: {args.top}')
    print(f'fields: {args.fields}')
    print(' ---------')
    count_ngrams(args.jsonl_in, args.csv_out, args.size, args.top, args.fields)
