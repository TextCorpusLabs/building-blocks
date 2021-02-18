import pathlib
import json
import mp_boilerplate as mpb
import typing as t
import utils as u
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def jsonl_to_itxt(jsonl_in: pathlib.Path, folder_out: pathlib.Path, id_element: str, extract: t.List[str], sub_process_count: int) -> None:
    """
    Converts a `JSONL` file into a folder of _interleaved_ `TXT` files.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the documents
    folder_out : pathlib.Path
        The folder containing all the documents after being extracted
    id_element : str
        The name of the element to use as a file name
    extract : List[str]
        The name(s) of the elements to extract
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    folder_out.mkdir(parents = True, exist_ok = True)

    worker = mpb.EPTS(
        extract = u._list_jsonl_documents, extract_args = (jsonl_in),
        transform = _save_txt_document, transform_init = _passthrough, transform_init_args = (str(folder_out), id_element, extract),
        save = _log_errors, save_args = (folder_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

@typechecked
def _save_txt_document(state:t.Tuple[str, str, t.List[str]], document: dict) -> t.Tuple[int, str]:
    """
    Saves the `TXT` document

    Parameters
    ----------
    state : tuple
        [0] The output folder
        [1] The element to use as a file name
        [2] The elements to extract
    document : dict
        The document to be saved
    """
    if state[1] in document:
        if _all_elements_present_as_list(document, state[2]):
            values = _extract_flattened_lists(document, state[2])
            if _all_lists_equal_lenght(values):
                file_name = pathlib.Path(state[0]).joinpath(f'./{document[state[1]]}.txt')
                with open(file_name, 'w', encoding = 'utf-8') as fp:
                    for i in range(0, len(values[0])):
                        tmp = [f'{vn[i]}\n' for vn in values]
                        fp.writelines(tmp + ['\n'])
                return (0, '')
            else:
                return (1, f'`List` elements different lengths in document : {document[state[1]]}')
        else:
            return (1, f'missing `List` elements in document : {document[state[1]]}')
    else:
        return (1, f'missing id: {state[1]}')

@typechecked
def _all_elements_present_as_list(document: dict, elements: t.List[str]) -> bool:
    """
    Checks to see if all the elements are in the document
    """
    for elm in elements:
        if elm in document:
            if type(document[elm]) != list:
                return False
        else:
            return False
    return True

@typechecked
def _extract_flattened_lists(document: dict, elements: t.List[str]) -> t.List[t.List[str]]:
    """
    Extracts known elements as flattened lists.
    I.E. list -> list, list[list] -> list
    """
    result = [None] * len(elements)
    for i in range(0, len(elements)):
        value = document[elements[i]]
        if type(value[0]) == list:
            result[i] = [' '.join(vn) for vn in value]
        else:
            result[i] = value
    return result

@typechecked
def _all_lists_equal_lenght(values: t.List[t.List[str]]) -> bool:
    """
    Tests to see if all the lengths of all the elements are the same
    """
    for vn in values:
        if len(values[0]) != len(vn):
            return False
    return True        

@typechecked
def _value_to_lines(value: t.Any) -> t.List[str]:
    """
    Converts a value of unknow type into lines for the `TXT` file
    """
    if value == None:
        value = ''
    if type(value) == list:
        if len(value) == 0:
            value = ['']
        v1 = value[0]
        if type(v1) == list:
            value = [' '.join(vn) for vn in value]
        return [f'{vn}\n' for vn in value]
    else:
        return [f'{value}\n']

@typechecked
def _passthrough(folder_out: str, id_element: str, extract: t.List[str]) -> t.Tuple[str, str, t.List[str]]:
    """
    Pass the state from the main thread to the single document processing function
    """
    result = (folder_out, id_element, extract)
    return result

@typechecked
def _log_errors(results: t.Iterator[t.Tuple[int, str]], folder_out: pathlib.Path) -> None:
    """
    Logs the errors in the interleaving process

    Parameters
    ----------
    results : iterator
        The results of the transformation process
    folder_out : pathlib.Path
        The folder containing the results
    """
    file_name = folder_out.parent.joinpath(f'{folder_out.stem}.error.log')
    with open(file_name, 'w', encoding = 'utf-8') as fp:
        for result in results:
            if result[0] != 0:
                fp.write(f'{result[0]}: {result[1]}\n')

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
    parser.add_argument(
        '-e', '--extract',
        help = 'The name(s) of the elements to extract',
        type = u.csv_list,
        required = True)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()    
    print(f'jsonl in: {args.jsonl_in}')
    print(f'folder out: {args.folder_out}')
    print(f'id element: {args.id_element}')
    print(f'extract: {args.extract}')
    print(f'sub process count: {args.sub_process_count}')
    jsonl_to_itxt(args.jsonl_in, args.folder_out, args.id_element, args.extract, args.sub_process_count)
