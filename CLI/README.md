# SolarRAG CLI

> **_Solar CLI:_**  This CLI contains SolarFactRAG and SolarNaiveRAG pipeline for [solar-qa pipeline](https://github.com/oeg-upm/solar-qa-eval)

## Install

#### 1. install all python packages

```console
pip install ollama networkx leidenalg cdlib python-igraph python-dotenv langchain huggingface_hub langchain-ollama==0.1.0 langchain-community==0.2.19 sentence-transformers==2.7.0 grobid-client-python==0.0.3
```

#### 2. install ollama

more details about ollama please visit the [offical ollama website](https://ollama.com/)

```console
curl -fsSL https://ollama.com/install.sh | sh
```

#### 3. install grobid client

please reference this part to the [offical grobid github page](https://grobid.readthedocs.io/en/latest/Install-Grobid/)

## Run Solar CLI

After installed all prerequisite libraries and software, you can simply run the cli by:

```console
python SolarRAG.py --llm_id llama3.2:3b --embedding_id nomic-embed-text --input_file_path XXX/paper_2.pdf --prompt_file XXX/prompt.json --context_file_path XXX/test.json --rag_type fact
```

Here is a table that describe the parameters to run the FactRAG cli

| Parameter | Definition | DataType | Example |
| -------- | ------- | ------- | ------- |
| llm_id  | the parameter of which LLM model from ollama to use | String | [llama3.2:3b](https://ollama.com/library/llama3.2) |
| embedding_id | the parameter of which embedding model from ollama to use | String | [nomic-embed-text](https://ollama.com/library/nomic-embed-text) |
| input_file_path | path for input data, pdf file or extracted json file | String | ../paper_1.pdf |
| prompt_file | path for the prompt json file | String | ../code/prompt.json |
| context_file_path | path for save the output json file | String | ../FactRAG/context.json |
| rag_type | the type of rag pipeline, range=['fact', 'naive'] | String | fact |