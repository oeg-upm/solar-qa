# File       : play.py
# Time       ：2024/4/22 11:15
# Author     ：ClarkWang
# Contact    ：wzyyyyyy0519@gmail
# Description：
from PyPDF2 import PdfReader
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

def chunk_processing(pdf):
    """
    Process a PDF file, extracting text and splitting it into chunks.
    """
    pdf_reader = PdfReader(pdf)

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text=text)
    return chunks

def embeddings(chunks):
    """
    Create embeddings for text chunks using OpenAI.
    """
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_KEY)
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    return vector_store


def generation(VectorStore):
    """
    Generate responses based on prompts and embeddings.
    """
    retriever = VectorStore.as_retriever()

    template = """Respond to the prompt based on the following context: {context}
    Questions: {questions}
    """
    prompt = ChatPromptTemplate.from_template(template)

    model = ChatOpenAI(openai_api_key=OPENAI_KEY)

    chain = (
            {"context": retriever, "questions": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
    )

    query = "Please Generate the Catalyst and co-catalyst from the paper, as well as generate the following information from the selection: Catalyst_set_up:['Powder(Suspended)', 'Film', 'Powder(Supported)', 'Powder', 'Other', 'Optical Fiber', 'SiO2 sublayer', 'Nanorribbons', 'Homogeneous', nan, 'Mesh', 'Monolith', 'Powder of nanocrystals', 'nanosheets', 'Nanofibers', 'ZnO nanorod array@carbon\nfiber (ZnO NA@CF) heterostructures', 'single-crystalline nanosheets', 'powder', 'Flaky g-C3N4 and uniformly loaded CdS nanospheres.', 'Nanocomposites.', 'powders', 'TiO2 nanosheets', 'Ultrathin SnNb2O6 2D nanosheets', 'nanotubes', 'tubes', 'nanorods', 'crystals', 'typical rod-like and belt-like structure', 'microrods', 'Hexagonal Platelets', 'Nickel on silica-alumina support', ' non-uniform grains', 'nanopowder', 'Single Crystal', 'Pellets', 'Powder(Sudpended)'], Reaction_medium:['Liquid', 'Gas'], Reactor_type: ['Slurry', 'Fixed-bed', 'OpticalFiber', 'Monolithic', 'Membrane', 'Fluidised-bed', nan], Operation_mode:['Batch', 'Continuous'], Lamp:['Mercury', 'Fluorescent', 'Xenon', 'SolarSimulator', 'Halogen', nan, 'Tungsten-Halide', 'Mercury-Xenon', 'Other', 'LED', 'Tungsten']. Each information please only generate one selection."

    output = chain.invoke(query)
    return output


paper_dir = "D:\\Projects\\Solar\\paper\\paper_3.pdf"

OPENAI_KEY = "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"

res = {}

for i in range(10):
    idx = i+1
    paper_dirx = "D:\\Projects\\Solar\\paper\\paper_" + str(idx) + ".pdf"
    pdf = open(paper_dirx, 'rb')
    processed_chunks = chunk_processing(pdf)

    embedded_chunks = embeddings(processed_chunks)

    generated_response = generation(embedded_chunks)

    temp = generated_response.splitlines()

    temp_res = {}
    for line in temp:
        if ":" in line:
            s, e = line.split(": ")
            temp_res[s] = e

    res[idx] = temp_res

print(res)
with open("One2Ten.json", "w") as f:
    json.dump(res, f)