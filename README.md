# solar-qa
A pipeline to annotate solar chemistry experiments according to solarchem model


## Paper Extraction: Grobid

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

## Generation

With the tasks to extract experiment-related information from the academic papers, we have adapted Large Language Models (LLMs) to understand the experiment and then provide the related information. To provided the related information from the experiment, we have implemented [RAG](https://arxiv.org/abs/2005.11401) technique in the generation pipeline.

### Generation Models:
- LLama3-8B: [Model ID](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
- LLama3-70B: [Model ID](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct)

### Generation Pipeline:

1. With the extraction from Gorbid, sections that are related to the experiment are extracted from the paper as the context. `Abstract`, `Experimental` and `Result`
2. Divided three sections into chunks and apply [Embedding Model](https://huggingface.co/Salesforce/SFR-Embedding-Mistral) as well as the query to select the most similar chunks.
3. Decode the most similar chunks into textual information and feed the textual information to the model to provide the context.
4. Apply the model to generate result follows the format: `Item: XXX`

### Generation Method

> Indicating the correlation and restrictions in the prompt

**Example**:
> "items": ["Light_source", "Lamp"]
> 
> "restriction": "If Light_source is Solar or Solar Simulator, Lamp is always Solar Simulator"

**Prompt Template**:

    Please find the category of Light_source and Lamp from the provided context which describe an solar chemical experiment.

    The generation condition of the extraction is given: If Light_source is Solar or Solar Simulator, Lamp is always Solar Simulator.

    Please only select the generation from the provided possible choices.

    Possible Choices:

    Light_source: ["UV", "Solar", "UV-Vis", "Monochromatic", "Solar Simulator"]

    Lamp: ["Fluorescent", "Mercury" ,"Halogen" ,"Mercury-Xenon", "LED", "Tungsten", "Xenon","Tungsten-Halide", "Solar Simulator"]

    Please generating restrictively follow the format, and must start the generation as the format. Do not generate anything else.

    Light_source: XXX

    Lamp: XXX

### Run Generation

`Groq.ipynb` contains all the libraries needed as well as the code to run the experiment. The needed data files for run the model and evaluate the model contains in the folder `Solar/ground_truth_data/`.

## Evaluation

### Basic Evaluation Process
- We adopt the model from [Massive Text Embedding Benchmark](https://huggingface.co/blog/mteb) based on the STS Task to calculate the similarity between each generate term and corresponding term in the ground truth. [Model ID](https://huggingface.co/Salesforce/SFR-Embedding-Mistral)
- We apply the similarity to each term pair (ground_truth_term, generation_term)
- In case of the number of generated terms and ground truth mismatched, we take the minimal number of generation and ground truth as the number of term we evaluate.
- We set the threshold as 0.85 for correct generation, which 1 indicate correct generation and 0 indicate miss generation
- Then calculate the overall accuracy for each item.

### Rule-based Evaluation Process

- If the ground_truth is in the generation, we consider it is accurate
- If generated reactor type is `Optical Fiber` or `Packed-bed` or `Membrane` and the ground truth is `Fixed-bed`, we consider it is accurate
- Then apply the same evaluation process as `Basic Evaluation Process`



### Evaluation Leadboard

| Rank |   Model  | Catalyst | Co-Catalyst | Light Source | Lamp   | Reactor Type | Reaction Medium | Operation Mode |  Overall Average |
|------|------------|----------|-------------|--------------|--------|--------------|-----------------|----------------|----------------|
|1|Claude_3_opus|0.9655|0.6552|0.7241|0.7586|0.5517|0.6897|0.8966|0.7488|
|2|LLama_3_70B|0.8276|0.6207|0.8276|0.6207|0.3103|0.6207|0.8276|0.665|
|3|GLM4|0.931|0.4828|0.5517|0.4828|0.5517|0.6897|0.8966|0.6552|
|4|GPT4|0.8621|0.4828|0.6552|0.6552|0.4483|0.6207|0.8621|0.6552|
|5|LLama_3_8B|0.7931|0.4828|0.5172|0.5172|0.3103|0.6552|0.7241|0.5714|
|6|GPT3.5|0.6552|0.4138|0.7241|0.3448|0.3448|0.5172|0.8966|0.5567|




