import pathlib
import json
import progressbar as pb
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def extract_json_from_jsonl(jsonl_in: pathlib.Path, folder_out: pathlib.Path, id_element: str) -> None:
    """
    Extracts a folder of `JSON` files from a a `JSONL` file.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    folder_out : pathlib.Path
        The folder containing all the documents after being extracted
    id_element : str
        The name of the element to use as a file name
    """

    folder_out.mkdir(parents = True, exist_ok = True)
    
    bar_i = 0
    widgets = [ 'Saving JSONL # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        documents = u.list_jsonl_documents(jsonl_in)
        for document in documents:
            if id_element in document:
                file_name = folder_out.joinpath(f'./{document[id_element]}.json')
                with open(file_name, 'w', encoding = 'utf-8') as fp:
                    json.dump(document, fp, sort_keys = True, indent = None)
                bar_i = bar_i + 1
                bar.update(bar_i)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the documents',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--folder-out',
        help = 'The folder containing all the documents after being extracted',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-id', '--id-element',
        help = 'The name of the element to use as a file name',
        type = str,
        default = 'id')
    args = parser.parse_args()
    print(' --- extract_json_from_jsonl ---')
    print(f'jsonl in: {args.jsonl_in}')
    print(f'folder out: {args.folder_out}')
    print(f'id element: {args.id_element}')
    print(' ---------')
    extract_json_from_jsonl(args.jsonl_in, args.folder_out, args.id_element)
