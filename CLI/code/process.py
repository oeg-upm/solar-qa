from grobid_client.grobid_client import GrobidClient
import xml.etree.ElementTree as ET
import json
import pandas as pd
import re
import unicodedata
import logging

# Configurar el registro (logging)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

# GROBID client configuration
client = GrobidClient(config_path="./settings/config.json")
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

    # Nueva función para extraer el DOI
    def extract_doi():
        """Extrae el DOI del documento usando su etiqueta específica."""
        doi_element = root.find(".//tei:idno[@type='DOI']", ns)
        if doi_element is not None:
            return clean_text(doi_element.text.strip())
        return None

    # Extraer el DOI
    doi = extract_doi()

    # Construcción de las secciones
    sections = [
        {"title": "Doi", "content": doi if doi else "Doi not found"},  # Incluir el DOI como primera sección
        {"title": "Article_Title", "content": title},  # Agregar el título como primera sección
        {"title": "Abstract", "content": extract_content_by_tag("abstract")},
        {"title": "Experimental", "content": extract_content_by_keywords(
            ["Experimental", "Experimental studies", "Experiments", "Experimental methods", "Methods"], "Results and discussion")},
        {"title": "Results_and_discussion", "content": extract_content_by_keywords(
            ["Results and discussion", "Result and discussion", "Results"], "Conclusion")},
        {"title": "Conclusions", "content": extract_content_by_keywords(
            ["Conclusion", "Conclusions"], "Conclusion")},
    ]

    # Sección opcional "Supporting Information"
    supporting_content = extract_content_by_keywords(
        ["Supporting Information", "Supporting"], "Conclusion")
    if supporting_content:
        sections.append({"title": "Supporting_Information", "content": supporting_content})

    return sections


def process_paper(pdf_file_path):
    
    try:
        # Procesar el PDF con Grobid para obtener el XML
        xml_response = process_fulltext_document(service_name, pdf_file_path)

        if xml_response:
            # Extraer secciones relevantes del XML
            sections = extract_sections_from_xml(xml_response)
            return sections  # Devolver el resultado como una lista de objetos JSON
        else:
            return [{"error": "Error processing the PDF."}]
    except Exception as e:
        logging.error(f"Error processing paper: {e}")
        return [{"error": str(e)}]
    



