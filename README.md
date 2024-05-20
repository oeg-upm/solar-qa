# solar-tagger
A pipeline to annotate solar chemistry experiments according to solarchem model


## Grobid

GROBID is a machine learning library for extracting, parsing, and restructuring raw documents, such as PDFs, into structured XML/TEI encoded documents, with a particular focus on technical and scientific publications.

### Implementation

First, you need to install GROBID following the documentation available at the following link: [GROBID Installation](https://grobid.readthedocs.io/en/latest/Install-Grobid/). Once installed, you should run the command `./gradlew run`, which will start the server on the default port 8070 (http://localhost:8070), configured in the `config.json` file within the `settings` folder.

We have two folders where the python files to run are located:

- **single_pdf**: This folder contains two files:
  1. `pdf_extraction.py`: Extracts all sections of a PDF into an XML file within the `xml_results` folder.
     - Command to run this file: `python pdf_extraction.py`
  2. `extract_section.py`: Extracts specific sections into a JSON file within the `json_results` folder.
     - Command to run this file: `python extract_section.py`

- **multiple_pdfs**: Contains a file `multiple_pdfs_extraction.py` that extracts all sections of multiple PDFs into several XML files within the `xml_results` folder.
  - Command to run this file: `python multiple_pdfs_extraction.py`

The PDFs to be processed are located in the `documents` folder.

## Evaluation

### Evaluation Process
- We adopt the model from Massive Text Embedding Benchmark based on the STS Task to calculate the similarity between each generate term and corresponding term in the ground truth.
- We apply the similarity to each term pair (ground_truth_term, generation_term)
- In case of the number of generated terms and ground truth mismatched, we take the minimal number of generation and ground truth as the number of term we evaluate.
- We set the threshold as 0.85 for correct generation, which 1 indicate correct generation and 0 indicate miss generation
- Then calculate the overall accuracy for each item.


| Rank | Model      | Catalyst | Co-Catalyst | Light Source | Lamp   | Reactor Type | Reaction Medium | Operation Mode |
|------|------------|----------|-------------|--------------|--------|--------------|-----------------|----------------|
| 1    | Llama_3_8B | 0.7576   | 0.5758      | 0.6364       | 0.6364 | 0.5455       | 0.4242          | 0.7273         |



