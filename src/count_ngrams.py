import csv
import pathlib
import shutil
import typing as t
import utils as u
import utils_jsonl as ul
from argparse import ArgumentParser
from sys import maxsize as MAX_SIZE
from typeguard import typechecked
from uuid import uuid4

@typechecked
def count_ngrams(jsonl_in: pathlib.Path, csv_out: pathlib.Path, size: int, top: int, fields: t.List[str], chunk_size: int) -> None:
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
    chunk_size: int
        The amount of n-grams to aggregate before cacheing
    """
    if csv_out.exists():
        csv_out.unlink()
    cache_dir = csv_out.parent.joinpath(f'tmp_{csv_out.name}')
    cache_dir.mkdir(parents = True, exist_ok = True)

    docs = ul.list_documents(jsonl_in)
    docs = u.progress_overlay(docs, 'Reading document')
    ngrams = (_count_ngrams_in_doc(doc, fields, size) for doc in docs)
    chunks = _chunk_ngrams_in_corpus(ngrams, chunk_size)
    caches = (_cache_ngram_chunks(x, cache_dir) for x in chunks)
    caches = list(caches)
    ngrams = _read_ngram_caches(caches)
    ngrams = _aggregate_ngrams_caches(ngrams)
    ngrams = u.progress_overlay(ngrams, 'Reading n-grams')
    ngrams = _keep_top_ngrams(ngrams, top)    
    _save_ngrams(ngrams, csv_out, size)
    shutil.rmtree(cache_dir)

@typechecked
def _count_ngrams_in_doc(document: dict, fields: t.List[str], size: int) -> dict:
    result = {}
    for field in fields:
        if field in document:
            for line in document[field]:
                tokens = line.upper().split(' ')
                for i in range(len(tokens) - size + 1):
                    ngram = ' '.join(tokens[i:(i+size)])
                    if ngram not in result:
                        result[ngram] = 0
                    result[ngram] = result[ngram] + 1
    return result

@typechecked
def _chunk_ngrams_in_corpus(ngram_list: t.Iterator[dict], chunk_size: int) -> t.Iterator[dict]:
    tmp = {}
    for ngrams in ngram_list:
        for ngram, count in ngrams.items():
            if ngram not in tmp:
                tmp[ngram] = 0
            tmp[ngram] = tmp[ngram] + count
        if len(tmp) > chunk_size:
            yield tmp
            tmp = {}
    if len(tmp) > 0:
        yield tmp

@typechecked
def _cache_ngram_chunks(ngrams: dict, cache_dir: pathlib.Path) -> pathlib.Path:
    file_name = cache_dir.joinpath(f'tmp_{uuid4()}.csv')
    with open(file_name, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        for ngram, count in sorted(ngrams.items(), key = lambda a: a[0]):
            writer.writerow([ngram, count])
    return file_name

@typechecked
def _read_ngram_caches(caches: t.List[pathlib.Path]) -> t.Iterator[list]:
    readers = [_read_ngram_cache(cache) for cache in caches]
    current = [next(reader) for reader in readers]
    cnt = len(current)
    while cnt > 0:
        i = _min_index(current)
        yield current[i]
        current[i] = next(readers[i], None)
        if current[i] is None:
            cnt = cnt - 1

@typechecked
def _min_index(ngrams: t.List[t.Union[list, None]]) -> int:
    len_ngs = len(ngrams)
    for i in range(len_ngs):
        if ngrams[i] is not None:
            min_ng = ngrams[i][0]
            min_i = i
            break
    for i in range(min_i + 1, len_ngs):
        curr = ngrams[i]
        if curr is not None and curr[0] < min_ng:
            min_ng = curr[0]
            min_i = i
    return min_i

@typechecked
def _read_ngram_cache(cache: pathlib.Path) -> t.Iterator[list]:
    with open(cache, 'r', encoding = 'utf-8') as fp:
        reader = csv.reader(fp, delimiter = ',', quotechar = '"')
        for item in reader:
            item[1] = int(item[1])
            yield item

@typechecked
def _aggregate_ngrams_caches(ngrams: t.Iterator[list]) -> t.Iterator[list]:
    prev = None
    for ngram in ngrams:
        if prev is None:
            prev = ngram
        elif prev[0] == ngram[0]:
            prev[1] = prev[1] + ngram[1]
        else:
            yield prev
            prev = ngram
    if prev is not None:
        yield prev

@typechecked
def _keep_top_ngrams(ngrams: t.Iterator[list], top: int) -> dict:
    def _add(results, count, ngram):
        if count not in results:
            results[count] = []
        results[count].append(ngram)
    results = {}
    cnt = 0
    mn = MAX_SIZE
    for ngram in ngrams:
        if cnt < top:
            _add(results, ngram[1], ngram[0])
            cnt = cnt + 1
            if ngram[1] < mn:
                mn = ngram[1]
        elif ngram[1] == mn:
            _add(results, ngram[1], ngram[0])
            cnt = cnt + 1
        elif ngram[1] > mn:
            _add(results, ngram[1], ngram[0])
            cnt = cnt + 1
            t1 = len(results[mn])
            if cnt - t1 >= top:
                del results[mn]
                cnt = cnt - t1
                mn = min(results.keys())
    res = {}
    for count, ngrams in results.items():
        for ngram in ngrams:
            res[ngram] = count
    return res

@typechecked
def _save_ngrams(ngrams: dict, csv_out: pathlib.Path, size: int) -> None:
    with open(csv_out, 'w', encoding = 'utf-8', newline = '') as fp:
        writer = csv.writer(fp, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL)
        writer.writerow(['n', 'count', 'ngram'])
        for ngram, count in sorted(ngrams.items(), key = lambda a: a[1], reverse = True):
            writer.writerow([size, count, ngram])

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
    parser.add_argument(
        '-c', '--chunk_size',
        help = 'The amount of n-grams to chunk to disk to prevent OOM',
        type = int,
        default = 10000000)
    args = parser.parse_args()
    print(' --- count_ngrams ---')
    print(f'jsonl in: {args.jsonl_in}')
    print(f'csv out: {args.csv_out}')
    print(f'size: {args.size}')
    print(f'top: {args.top}')
    print(f'fields: {args.fields}')
    print(f'chunk size: {args.chunk_size}')
    print(' ---------')
    count_ngrams(args.jsonl_in, args.csv_out, args.size, args.top, args.fields, args.chunk_size)
