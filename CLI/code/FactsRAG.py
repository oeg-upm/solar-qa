from dotenv import load_dotenv
from cdlib import algorithms
import networkx as nx
import os
import json
import argparse
from collections import OrderedDict
from process import *


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.docstore.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from sentence_transformers import util


def get_text(data):
    title_list = ["Article_Title", "Abstract", "Experimental", "Results and discussion"]
    context = ""
    context_list = []
    for section in data:
        if section["title"] in title_list:
            # self.context_list.append(f"{section["title"]}: {section["content"]}")
            context += section["title"]
            context += "\n"
            context += section["content"]
            context += "\n"
    return context


def get_title(data):
    for section in data:
        if section["title"] == "Article_Title":
            return section["content"]
        else:
            pass
    return "None Given"


def get_doi(data):
    for section in data:
        if section["title"] == "Doi":
            return section["content"]
        else:
            pass
    return "None Given"


def clean_response(gen, category):
    print(gen)
    res = {}
    s, e = gen.split(":")
    res[category] = e
    print(res)
    return res


class SolarFact:
    def __init__(self, llm_id, embedding_id, input_file_path=str(), context_file_path=str()):
        self.llm_id = llm_id
        self.embedding_id = embedding_id
        self.input_file_path = input_file_path
        self.context_file_path = context_file_path
        self._get_llm()
        self._get_documents()
        self.context_result = {
            "paper_title": self.paper_title,
            "DOI": self.doi,
            "generation_model": self.llm_id,
            "similarity_model": self.embedding_id,
            "similarity_metric": "Cosine_Similarity",
            "result": []
        }
        self.chunks, self.entities, self.relations, self.facts = self._prepare_pipeline()
    
    def _get_llm(self):
        self.llm = ChatOllama(model=self.llm_id, temperature=0)
        self.embeddings = OllamaEmbeddings(model=self.embedding_id)
    
    def _get_documents(self):
        if self.input_file_path[-3:] == "pdf":
            # print(1)
            data = process_paper(self.input_file_path)
        else:
            with open(self.input_file_path, "rb") as f:
                data = json.load(f)
        self.paper_title = get_title(data)
        self.doi = get_doi(data)
        self.documents = get_text(data)
    
    def _split_documents_into_chunks(self, chunk_size=600, overlap_size=100):
        documents = [Document(page_content=self.documents)]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap_size)
        chunks = text_splitter.split_documents(documents)
        return chunks
    
    def _extract_entities_from_chunks(self, chunks):
        entities = {}
        title_list = ['Article Title', "Abstract", "Experimental", "Results and discussion"]
        print(f"------Start extracting entities from chunks------")
        print(f"------Total chunk count: {len(chunks)}------")
        for index, chunk in enumerate(chunks):
            if chunk in title_list:
                pass
            else:
                response = self.llm.invoke(
                    [
                        {"role": "system", "content": "Extract all the entities from the following text."},
                        {"role": "user", "content": chunk.page_content}
                    ]
                )
            entities_for_chunks = response.content
            entities[index] = entities_for_chunks
        print(f"------Entities extraction is done------")
        return entities
    
    def _extract_relationships_from_chunks_and_entities(self, chunks, entities):
        relations = {}
        title_list = ['Article Title', "Abstract", "Experimental", "Results and discussion"]
        print(f"------Start extracting entities from chunks------")
        print(f"------Total chunk count: {len(chunks)}------")
        for index, chunk in enumerate(chunks):
            if chunk in title_list:
                pass
            else:
                response = self.llm.invoke(
                    [
                        {"role": "system", "content": "Extract all the relationship from the following context and provided entities in the format of triples, (subject, predicate, object)"},
                        {"role": "user", "content": f"Context: {chunk.page_content}, Entities: {entities[index]}"}
                    ]
                )
            relation = response.content
            relations[index] = relation
        print(f"------Relationships extraction is done------")
        return relations
    
    def _generate_facts_from_relations(self, chunks, relations):
        facts = {}
        print(f"------Start generating factual sentences------")
        for index, chunk in enumerate(chunks):
            response = self.llm.invoke(
                [
                    {"role": "system", "content": "Construct simple fact sentences by combining the following relationships after the \"Facts:\" word."},
                    {"role": "user", "content": f" Relations: {relations[index]}"}
                ]
            )
            fact = response.content
            facts[index] = fact
        print(f"------Facts generation is done------")
        return facts
    
    def _cal_fact_cosine_similairty(self, facts, prompt, category):
        if isinstance(facts, list):
            facts = {index: value for index, value in enumerate(facts)}
        sim_dict = {}
        for key, fact in facts.items():
            fact_embed = self.embeddings.embed_query(fact)
            query_embed = self.embeddings.embed_query(prompt)
            cosine_similarity = util.cos_sim(fact_embed, query_embed)
            sim_dict[key] = cosine_similarity[0].detach().item()
        sorted_sim_dict = dict(sorted(sim_dict.items(), key=lambda item: item[1], reverse=True))
        return sorted_sim_dict
            
    def _generate_final_answer(self, sort_sim_dict, k, text, prompt, category, selection=None):
        indexes = list(sort_sim_dict.keys())[:k]
        context = ""
        for ind in indexes:
            context += text[ind] 
        if selection is None:
            final_response = self.llm.invoke(
                    [
                    {"role": "system", "content": f"Answer the following query based on the provided summary of facts. Please indicate the answer following the structure of \"###{category}:\" YOUR ANSWER"},
                    {"role": "user", "content": f"Facts: {context} Query : {prompt}"}
                    ]
                )
            
        else:
            final_response = self.llm.invoke(
                    [
                    {"role": "system", "content": f"Answer the following query by selecting only one of the choices based on the provided summary of facts. Please indicate the answer following the structure of \"###{category}:\" YOUR ANSWER"},
                    {"role": "user", "content": f"Query: {prompt} Choices: {selection} Facts: {context}"}
                    ]
                )
        return indexes, final_response.content
    
    def _prepare_pipeline(self):
        chunks = self._split_documents_into_chunks()
        
        entities = self._extract_entities_from_chunks(chunks)
        
        relations = self._extract_relationships_from_chunks_and_entities(chunks, entities)
        
        facts = self._generate_facts_from_relations(chunks, relations)
        
        return chunks, entities, relations, facts
        
    
    def graphrag_pipeline(self, k, prompt, category):
        print("---------------------running factrag pipeline---------------------")
        ## Prepare data
        #self.chunks, self.entities, self.relations, self.facts
        
        ## Get choices
        if category in ["catalyst", "co_catalyst"]:
            selection = None
        elif category == "Light_source":
            selection = "'UV', 'Solar', 'UV-Vis', 'Monochromatic', 'Solar Simulator', 'Do not Know'"
        elif category == "Lamp":
            selection = "'Fluorescent', 'Mercury', 'Halogen', 'Mercury-Xenon', 'LED', 'Tungsten', 'Xenon', 'Tungsten-Halide', 'Solar Simulator', 'Do not Know'"
        elif category == "Reaction_medium":
            selection = "'Liquid', 'Gas', 'Do not Know'"
        elif category == "Reactor_type":
            selection = "'Slurry', 'Fixed-bed', 'Optical Fiber', 'Monolithic', 'Membrane', 'Fluidised-bed', 'Do not Know'"
        elif category == 'Operation_mode':
            selection = "'Batch', 'Continuous', 'Batch/Continuous', 'Do not Know'"
            
        ## Run Pipeline
        sim_dict = self._cal_fact_cosine_similairty(self.facts, prompt, category)
        
        indexes, final_response = self._generate_final_answer(sim_dict, k, self.facts, prompt, category, selection)
        
        evidences = []
        
        for index in indexes:
            evidence = {
                "similairty_score": sim_dict[index],
                "pdf_reference": self.chunks[index].page_content,
                "generated_facts": self.facts[index]
            }
            evidences.append(evidence)
        temp = {
                "question_category": category,
                "query": prompt,
                "generation": final_response,
                "RAG_source": "generated_facts",
                "selected_answer": clean_response(final_response, category),
                "evidences": evidences
            }
        return temp
        

def get_parser():
    parser = argparse.ArgumentParser(description="Demo of LLM Pipeline")
    parser.add_argument('--llm_id', type=str, default=True, help="the parameter of which LLM model from ollama to use")
    parser.add_argument('--embedding_id', type=str, default=True, help="the parameter of which embedding model from ollama to use")
    parser.add_argument('--input_file_path', type=str, default=True, help="path for input data, pdf file or extracted json file")
    parser.add_argument('--prompt_file', help='queries', type=str)
    parser.add_argument('--context_file_path', type=str, default=True, help="save context file")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    args_dict = vars(args)
    prompt_file = args_dict["prompt_file"]
    del args_dict["prompt_file"]
    factrag = SolarFact(**args_dict)
    context_result = {
            "paper_title": factrag.paper_title,
            "DOI": factrag.doi,
            "generation_model": factrag.llm_id,
            "similarity_model": factrag.embedding_id,
            "similarity_metric": "Cosine_Similarity",
            "result": []
    }
    with open(prompt_file, "rb") as f:
        query_data = json.load(f)
    for key, value in query_data.items():
        temp = factrag.graphrag_pipeline(5, value, key)
        context_result["result"].append(temp)
    # print(context_result)
    with open(factrag.context_file_path, "w") as f:
        json.dump(context_result, f)


main()