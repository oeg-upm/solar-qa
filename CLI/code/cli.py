# File       : pipeline.py
# Time       ：2024/7/14 14:11
# Author     ：ClarkWang
# Contact    ：wzyyyyyy0519@gmail
# Description：

# !pip install --upgrade langchain langchain_groq
# !pip install --upgrade langchain-community
# !pip install --upgrade langchain-core
# !pip install --upgrade langsmith
# !pip install ctransformers[cuda]
# !pip install huggingface-hub
# !pip install --upgrade sqlalchemy
# !pip install rdflib
# !pip install llama-cpp-python
# !pip install typing-extensions==4.7.1 --upgrade
# !pip install pypdf2
# !pip install sentence-transformers==2.7.0
# !pip install --upgrade transformers
# !pip install faiss-cpu
# !pip install bitsandbytes accelerate

import warnings
warnings.filterwarnings("ignore")

import os
import json
import argparse
import time
import torch
import transformers
from huggingface_hub import login
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from process import process_paper


def get_context(context):
    res = []
    for item in context:
        res.append(item.page_content)
    return res

def clean_gen(gen):
    res = {}
    for line in gen.split("\n"):
        if ":" in line:
            try:
                s, e = line.split(":")
                res[s.strip()] = e
            except:
                pass
    return res

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

class SolarQA:
    def __init__(self, use_platform, user_key, llm_id, hf_key, llm_platform="LOCAL", temperature=0.1, sim_model_id="Salesforce/SFR-Embedding-Mistral", pdf_file_path="", context_file_path=""):
        self.use_platform = use_platform
        self.llm_id = llm_id
        self.user_key = user_key
        self.hf_key = hf_key
        self.llm_platform = llm_platform.lower()
        self.temperature = temperature
        self.sim_model_id = sim_model_id
        self.sys_prompt = """
        You are an assistant for extract information from context and selection the possible answer from the selection provided.
        You are given the extracted parts of a paper about solar chemistry and a question. Provide the extracted information and nothing else.
        """
        self.context_file_path = context_file_path
        self.pdf_file_path = pdf_file_path
        
        self.context_result = {
            "generation_model": self.llm_id,
            "similarity_model": self.sim_model_id,
            "similarity_metric": "Cosine_Similarity",
            "result": []
        }
        login(self.hf_key)
        self.get_text()
        self.get_vector()
        print("¡¡¡Vector Store Database is prepared!!!")
        self.get_llm()

    def get_text(self):
        title_list = ["Abstract", "Experimental", "Results and discussion"]
        # with open(self.json_path, "rb") as f:
        #     data = json.load(f)
        data = process_paper(self.pdf_file_path)
        print("¡¡¡PDF file has been extracted!!!")
        self.context = ""
        for section in data:
            if section["title"] in title_list:
                self.context += section["title"]
                self.context += "\n"
                self.context += section["content"]
                self.context += "\n"

    def get_llm(self):
        if self.use_platform:
            if self.llm_platform == "groq":
                os.environ["GROQ_API_KEY"] = self.user_key
                self.llm = ChatGroq(temperature=self.temperature, model_name=self.llm_id)
            else:
                raise ValueError('Unsupportted Platform')
        else:
                try:
                    bnb_config = transformers.BitsAndBytesConfig(
                        load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch.bfloat16
                    )
                    self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.llm_id)
                    self.llm = transformers.AutoModelForCausalLM.from_pretrained(
                        self.llm_id,
                        torch_dtype=torch.bfloat16,
                        device_map="auto",
                        quantization_config=bnb_config
                    )
                    self.terminators = [
                        self.tokenizer.eos_token_id,
                        self.tokenizer.convert_tokens_to_ids("<|eot_id|>")
                    ]
                except:
                    raise ValueError('Unsupportted Platform')

    def get_vector(self):
        model_kwargs = {"device": "cpu"}
        self.sim_model = HuggingFaceEmbeddings(model_name=self.sim_model_id, model_kwargs=model_kwargs)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=32,
            length_function=len
        )
        chunks = text_splitter.split_text(text=self.context)
        self.vector_store = FAISS.from_texts(chunks, embedding=self.sim_model, normalize_L2=True, distance_strategy="COSINE")

    def search(self, query, k):
        embed_q = self.sim_model.embed_query(query)
        self.context = self.vector_store.similarity_search_with_score_by_vector(embed_q, k)

    def format_prompt(self, query, k):
        self.search(query, k)
        prompt = self.sys_prompt + "\n" + "Question:"
        prompt += query
        prompt += "\n"
        prompt += "Context:"
        for i in range(k):
            prompt += f"{self.context[i]}\n"
        return prompt

    def generation(self, query_data):
        res = ""
        if self.use_platform:
            for key, query in query_data.items():
                new_prompt = self.format_prompt(query, 5)
                messages = [{"role": "system", "content": self.sys_prompt}, {"role": "user", "content": new_prompt}]
                outputs = self.llm.invoke(messages)
                response = outputs.content
                temp_res = {
                    "question_category": key,
                    "query": query,
                    "generation": clean_gen(response),
                    "evidence": []
                }
                for i in range(len(self.context)):
                    context = self.context[i][0].page_content
                    sim_score = float(self.context[i][1])
                    temp_res["evidence"].append({"pdf_reference": context, "similarity_score": sim_score})
                self.context_result["result"].append(temp_res)
                res += response
                res += "\n"
            self.result = clean_gen(res)
        else:
            for key, query in query_data.items():
                new_prompt = self.format_prompt(query, 5)
                messages = [{"role": "system", "content": self.sys_prompt}, {"role": "user", "content": new_prompt}]
                input_ids = self.tokenizer.apply_chat_template(
                    messages,
                    add_generation_prompt=True,
                    return_tensors="pt"
                )
                outputs = self.llm.generate(
                    input_ids,
                    max_new_tokens=1024,
                    eos_token_id=self.terminators,
                    do_sample=True,
                    temperature=self.temperature,
                    top_p=0.9,
                )
                response = self.tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
                temp_res = {
                    "question_category": key,
                    "query": query,
                    "generation": clean_gen(response),
                    "evidence": []
                }
                for i in range(len(self.context)):
                    context = self.context[i][0].page_content
                    sim_score = float(self.context[i][1])
                    temp_res["evidence"].append({"pdf_reference": context, "similarity_score": sim_score})
                self.context_result["result"].append(temp_res)
                res += response
                res += "\n"
            self.result = clean_gen(res)

    def save_context(self):
        # print(self.context_result)
        with open(self.context_file_path, "w") as f:
            json.dump(self.context_result, f)
        print(f"RAG context is saved at: {self.context_file_path}")



def get_parser():
    parser = argparse.ArgumentParser(description="Demo of LLM Pipeline")
    parser.add_argument('--use_platform', type=lambda x:str2bool(x), default=True, help="the parameter of whether use online llm platform or use local model")
    parser.add_argument('--user_key', default="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", help="if use platform, enter your key for platform", type=str)
    parser.add_argument('--llm_id', default="llama-3.1-70b-versatile", help="the reference for the selected model, support grog model, huggingface llm or local model path ", type=str)
    parser.add_argument('--hf_key', default="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", help="your huggingface token", type=str)
    parser.add_argument('--llm_platform', default="groq", help='your platform choice', choices=["groq"], type=str)
    parser.add_argument('--sim_model_id', default='Salesforce/SFR-Embedding-Mistral', help="encoder model for RAG", type=str)
    parser.add_argument('--pdf_file_path', help='input data, extracted context from pdf', type=str)
    parser.add_argument('--prompt_file_pdf', help='queries', type=str)
    parser.add_argument('--context_file_path', help='save context file', type=str)
    return parser

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    args_dict = vars(args)

    prompt_file_pdf = args_dict["prompt_file_pdf"]

    del args_dict["prompt_file_pdf"]
    start_time = time.time()
    solar = SolarQA(**args_dict)
    print("--- %s Data Preparation and Model Loading time consumption: seconds ---" % (time.time() - start_time))
    temp_time = time.time()
    with open(prompt_file_pdf, "rb") as f:
        query_data = json.load(f)
    solar.generation(query_data=query_data)
    print(solar.result)
    print("--- %s Model generation time consumption: seconds ---" % (time.time() - temp_time))
    solar.save_context()