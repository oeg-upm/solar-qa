# Solar-QA-CLI
This repository contains the command-line tool for [solar-qa pipepine](https://github.com/oeg-upm/solar-qa-eval)

## Requirement

### Requirement for Paper Extraction

- gorbid-client-python

### Requirement for Generation

- torch
- accelerate
- tokenizers
- bitsandbytes
- huggingface_hub
- sentence-transformer
- faiss-cpu
- langchain
- langchain_groq
- langchain-community



### Usage

1. Install [GROBID](https://grobid.readthedocs.io/en/latest/) in your computing device
2. Start running GROBID server in your local device by 
```console
./gradlew run
```
3. With the running GROBID server, to run the entire command-line tool by running the `cli.py` in the directory `.../CLI/code/cli.py`. The command line to run the `cli.py` is given below:
```json
"--use_platform": the parameter of whether use online platform or local model for the llm(generation model). option = ["True", "False"]
"--user_key": the user key or token for the online platform, type="str"
"--llm_id": the reference id for the llm(generation model), type="str"
"--hf_key": your huggingface token, this is required to use the similarity model, type="str"
"--llm_platform": indication of which llm online platform you wish to use, option=["grob"]
"--sim_model_id": the reference id for the similarity model, type="str"
"--pdf_file_path": the directory for the pdf fild that you wish to analysis, type="str", file type=.pdf
"--prompt_file_path": the directory for the json file that contains your prompt, file type=.json
"--context_file_path": the directory for where you wish to save the output file, file type=.json
```
*Example not use online platform:*
```console
python cli.py --use_platform False --hf_key YOUR_HF_KEY --llm_id meta-llama/Llama-3.2-3B-Instruct --sim_model_id Salesforce/SFR-Embedding-Mistral --pdf_file_path .../test.pdf --prompt_file .../prompts.json --context_file_path .../context.json
```
*Example use online platform:*
```console
python cli.py --use_platform True --user_key YOUR_USER_KEY --hf_key YOUR_HF_KEY --llm_id llama-3.1-70b-versatile --llm_platform grob --sim_model_id Salesforce/SFR-Embedding-Mistral --pdf_file_path .../test.pdf --prompt_file .../prompts.json --context_file_path .../context.json
```