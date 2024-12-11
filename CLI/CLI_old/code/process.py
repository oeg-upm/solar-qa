from grobid_client.grobid_client import GrobidClient
import subprocess
from multiprocessing import Pool
import xml.etree.ElementTree as ET
import json
import pandas as pd
import re
import unicodedata
import logging
import threading
# from cli import *
# from cli import *

# Configurar el registro (logging)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

# GROBID client configuration
client = GrobidClient(config_path="./setting/config.json")
service_name = "processFulltextDocument"

def process_fulltext_document(service, file):
    try:
        rsp = client.process_pdf(service, file,
                                 generateIDs=True,
                                 consolidate_header=True,
                                 consolidate_citations=False,
                                 include_raw_citations=False,
                                 include_raw_affiliations=False,
                                 tei_coordinates=True,
                                 segment_sentences=True)
        if rsp[1] == 200:  # HTTP status check
            return rsp[2]  # rsp[2] is the XML string
        else:
            print(f"Error: {rsp[1]}")
    except Exception as e:
        print(f"Exception during PDF processing: {e}")
    return None

def clean_text(text):
    """ Limpia y normaliza el texto para eliminar caracteres no deseados. """
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')  # Normalización Unicode
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Eliminar todos los caracteres no ASCII
    text = re.sub(r'[\u00b0\n\t\r]', ' ', text)  # Eliminar caracteres específicos
    text = re.sub(r'[^A-Za-z0-9\s,.?!;:()\-\'\"/]', '', text)  # Mantener solo caracteres alfanuméricos y puntuación básica
    text = re.sub(r'\s+', ' ', text).strip()  # Reemplazar múltiples espacios por uno solo
    return text

def extract_sections_from_xml(xml_content):
    """ Extrae secciones relevantes del contenido XML devuelto por Grobid. """
    root = ET.fromstring(xml_content)
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Extraer título
    title = ''
    title_element = root.find(".//tei:title", ns)
    if title_element is not None:
        title = ''.join(title_element.itertext()).strip()

    # Función para extraer contenido bajo una etiqueta específica
    def extract_content_by_tag(tag_name):
        content = []
        path = f".//{{{ns['tei']}}}{tag_name}"
        for elem in root.findall(path):
            text = ''.join(elem.itertext())
            if text:
                content.append(clean_text(text.strip()))
        return " ".join(content)

    # Función para extraer contenido según palabras clave
    def extract_content_by_keywords(start_keywords, end_section):
        content = []
        capture = False
        for elem in root.iter():
            if elem.tag.endswith("head"):
                if elem.text and any(keyword.lower() in elem.text.lower() for keyword in start_keywords):
                    capture = True
                elif elem.text and end_section.lower() in elem.text.lower():
                    break
            if capture and elem.tag.endswith("p"):
                text = ''.join(elem.itertext()).strip()
                if text:
                    content.append(clean_text(text))
        return " ".join(content)

    # Extracción de secciones
    sections = [
        {"title": "Abstract", "content": extract_content_by_tag("abstract")},
        {"title": "Experimental", "content": extract_content_by_keywords(
            ["Experimental", "Experimental studies", "Experiments", "Experimental methods", "Methods"], "Results and discussion")},
        {"title": "Results and discussion", "content": extract_content_by_keywords(
            ["Results and discussion", "Result and discussion", "Results"], "Conclusion")},
        {"title": "Conclusions", "content": extract_content_by_keywords(
            ["Conclusion", "Conclusions"], "Conclusion")},
    ]

    # Sección opcional "Supporting Information"
    supporting_content = extract_content_by_keywords(
        ["Supporting Information", "Supporting"], "Conclusion")
    if supporting_content:
        sections.append({"title": "Supporting Information", "content": supporting_content})

    return sections

def run_process(cmd):
    subprocess.run(command, capture_output=True, shell=True)

def process_paper(pdf_file_path):
    """ Procesa un archivo PDF y devuelve una lista con objetos JSON por cada sección. """
    try:
        # Procesar el PDF con Grobid para obtener el XML
        xml_response = process_fulltext_document(service_name, pdf_file_path)

        if xml_response:
            # Extraer secciones relevantes del XML y devolverlas como lista de objetos
            sections = extract_sections_from_xml(xml_response)
            return sections  # Devolver el resultado como una lista de objetos JSON
        else:
            return [{"error": "Error processing the PDF."}]
    except Exception as e:
        logging.error(f"Error processing paper: {e}")
        return [{"error": str(e)}]

    
# def get_parser():
#     parser = argparse.ArgumentParser(description="Demo of LLM Pipeline")
#     parser.add_argument('--use_platform', type=lambda x:str2bool(x), default=True, help="the parameter of whether use online llm platform or use local model")
#     parser.add_argument('--user_key', default="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", help="if use platform, enter your key for platform", type=str)
#     parser.add_argument('--llm_id', default="llama-3.1-70b-versatile", help="the reference for the selected model, support grog model, huggingface llm or local model path ", type=str)
#     parser.add_argument('--hf_key', default="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", help="your huggingface token", type=str)
#     parser.add_argument('--llm_platform', default="groq", help='your platform choice', choices=["groq"], type=str)
#     parser.add_argument('--sim_model_id', default='Salesforce/SFR-Embedding-Mistral', help="encoder model for RAG", type=str)
#     parser.add_argument('--pdf_file_path', help='input data, extracted context from pdf', type=str)
#     parser.add_argument('--prompt_file_pdf', help='queries', type=str)
#     parser.add_argument('--context_file_path', help='save context file', type=str)
#     parser.add_argument('--grobid_path', help='the directoray of your grobid location', type=str)
#     return parser

    
# def main():
#     parser = get_parser()
#     args = parser.parse_args()
#     args_dict = vars(args)
#     print(args_dict)
#     prompt_file_pdf = args_dict["prompt_file_pdf"]
#     grobid_path = args_dict["grobid_path"]
#     global command
#     command = f"cd ~; cd {grobid_path}; ./gradlew run"
#     # DETACHED_PROCESS = 0x00000008
#     # subprocess.Popen(["bash", "run_grobid.sh"], creationflags=DETACHED_PROCESS)
#     # subprocess.Popen(["bash", "run_grobid.sh"], close_fds=True)
#     # subprocess.Popen(["bash", "run_grobid.sh"])
#     print("Grobid is running")
#     global client
#     client = GrobidClient(config_path="./setting/config.json")
#     global service_name
#     service_name = "processFulltextDocument"
#     del args_dict["prompt_file_pdf"]
#     del args_dict["grobid_path"]
#     start_time = time.time()
#     solar = SolarQA(**args_dict)
#     print("--- %s Data Preparation and Model Loading time consumption: seconds ---" % (time.time() - start_time))
#     temp_time = time.time()
#     with open(prompt_file_pdf, "rb") as f:
#         query_data = json.load(f)
#     solar.generation(query_data=query_data)
#     print(solar.result)
#     print("--- %s Model generation time consumption: seconds ---" % (time.time() - temp_time))
#     solar.save_context()

# pool = Pool(2)    
# pool.apply_async(subprocess.Popen(["bash", "run_grobid.sh"]), (0,))
# pool.apply_async(main(), (0,))
# # main()
    
# # Configurar el registro (logging)
# logging.basicConfig(level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

# # GROBID client configuration
# client = GrobidClient(config_path="./setting/config.json")
# service_name = "processFulltextDocument"
    


# print(type(process_paper("/home/jovyan/grob/test.pdf")))