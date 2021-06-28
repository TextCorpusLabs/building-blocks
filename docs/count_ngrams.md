# Count NGrams

Count the n-grams for a `JSONL` file.

# Steps

Below are the steps needed to run the _calculation_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/src` directory.
3. [Count](../src/count_ngrams.py) the n-grams for a `JSONL` file.
   * The `-in`/`-out` parameters control the source and destination files.
     **WARNING**: If the output file exists, it is deleted.
   * The `-n` parameter controls the n-gram length.
   * The `-t` parameter controls how many n-grams are saved.
   * The optional `-f` parameter allows the input element's name to be changed or provide a list of such elements in csv form.
     It defaults to 'text'.
   ```{ps1}
   python count_ngrams.py -in d:/corpus_in.jsonl -out d:/corpus_out.csv -n 1 -t 10000
   ```