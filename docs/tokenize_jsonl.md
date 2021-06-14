# Tokenize JSONL

Tokenize a `JSONL` file by applying the NLTK defaults (Punkt + Penn Treebank) to a text field.

# Steps

Below are the steps needed to run the _tokenization_ process.
The pathing can be changed by updating the parameters.

1. Clone this repository.
2. Open a PowerShell window to the `~/code` directory.
3. [Tokenize](../code/tokenise_jsonl.py) a `JSONL` file by applying the NLTK defaults (Punkt + Penn Treebank) to a text field.
   * The `-in`/`-out` parameters control the source and destination file.
     If the output folder does not exist it is created.
   * The optional `-id` parameter controls which element will be used to correlate related files pre/post tokenization.
     It defaults to 'id'.
   * The optional `-t` parameter allows the input/output element's name to be changed or provide a list of such elements in csv form.
     It defaults to 'text:tokenized'.
   * The optional `-spc` parameter allows for tuning on multi core machines.
     It defaults to 1.
   ```{ps1}
   python tokenize_jsonl.py -in d:/corpus_in.jsonl -out d:/corpus_out.jsonl
   ```

# Academic boilerplate

Below is the suggested text to add to the "Methods and Materials" section of your paper when using this _process_.
The references can be found [here](./references.bib)

> After the corpus was collected and converted to plain text, it was tokenized using the NLTK's ^[http://www.nltk.org] implementation of the Punkt sentence tokenizer [@kiss2006unsupervised] followed by the Penn Treebank word tokenizer [@marcus1993building].
> Punkt was chosen as it has proven viable in several other works [@hiippala2016semi;@avramidis2011evaluate;@yao2014information;@nothman2013learning].
> Laboreiro et al. notes that while the Penn Treebank may have some issues, it is still the de-facto standard [@laboreiro2010tokenizing].
