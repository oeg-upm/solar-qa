from grobid_client.grobid_client import GrobidClient
import xml.etree.ElementTree as ET
import json
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import glob
import os
import re
import unicodedata
import logging
import fitz  # PyMuPDF
import camelot
import pdfplumber
from tabula import read_pdf

from os import path, makedirs, listdir

# Configure logging
log_file_path = 'process_errors.log'
logging.basicConfig(filename=log_file_path, level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# GROBID client configuration
client = GrobidClient(config_path="../settings/config.json")
service_name = "processFulltextDocument"
pdf_folder = "../documents/"
output_base_folder = '../json_results/'
complete_output_folder = '../json_results/complete/'
incomplete_output_folder = '../json_results/incomplete/'
csv_path = '../paper_references.csv'

# Create output folders
for folder in [complete_output_folder, incomplete_output_folder]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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
    # Unicode normalization to remove special characters
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    # Remove non-printable characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove all non-ASCII characters
    
    # Remove unwanted characters using regular expressions
    text = re.sub(r'[\u00b0\n\t\r]', ' ', text)  # Remove specific characters
    text = re.sub(r'[^A-Za-z0-9\s,.?!;:()\-\'\"/]', '', text)  # Keep only alphanumeric characters and basic punctuation, including "/"
    
    # Replace multiple spaces with a single one
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_sections_from_xml(file_path):
    # Load XML from a file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace, if the XML uses namespaces
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Extract title
    title = ''
    title_element = root.find(".//tei:title", ns)
    if title_element is not None:
        title = ''.join(title_element.itertext()).strip()

    # Function for extracting content under a specific tag, handles namespaces
    def extract_content_by_tag(tag_name):
        content = []
        # Adjust the label name for the namespace if necessary.
        path = f".//{{{ns['tei']}}}{tag_name}" if ns else f".//{tag_name}"
        for elem in root.findall(path):
            text = ''.join(elem.itertext())
            if text:
                content.append(clean_text(text.strip()))
        return " ".join(content)

    # Function to extract content according to keywords
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

    # Function to extract image descriptions
    def extract_image_descriptions():
        descriptions = []
        for figure in root.findall(".//tei:figure", ns):
            figure_label = figure.find(".//tei:figDesc", ns)
            if figure_label is not None:
                descriptions.append(''.join(figure_label.itertext()).strip())
        return descriptions

    # Extraction of sections
    abstract_content = extract_content_by_tag("abstract")
    experimental_content = extract_content_by_keywords(
        ["Experimental", "Experimental studies", "Experiments", "Experimental methods", "Methods"], "Results and discussion")
    results_discussion_content = extract_content_by_keywords(
        ["Results and discussion", "Result and discussion", "Results"], "Conclusion")
    supporting_information_content = extract_content_by_keywords(
        ["Supporting Information", "Supporting"], "Conclusion")
    conclusions_content = extract_content_by_keywords(
        ["Conclusion", "Conclusions"], "Conclusion")
    image_descriptions = extract_image_descriptions()

    sections = [
        {"title": "Abstract", "content": abstract_content},
        {"title": "Experimental", "content": experimental_content},
        {"title": "Results and discussion", "content": results_discussion_content},
        {"title": "Conclusions", "content": conclusions_content},
    ]

    if supporting_information_content:
        sections.append({"title": "Supporting Information",
                        "content": supporting_information_content})

    return sections, title, image_descriptions

def extract_images_from_pdf(pdf_path, images_folder, image_descriptions):
    doc = fitz.open(pdf_path)
    image_descriptions_dict = {}
    image_counter = 1

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width, height = base_image["width"], base_image["height"]

            # Filter out small images (possible logos)
            if width < 300 or height < 300:
                continue

            image_name = f"image_{image_counter}.{image_ext}"
            image_path = os.path.join(images_folder, image_name)

            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            # Add description if available
            if image_counter <= len(image_descriptions):
                image_descriptions_dict[image_name] = clean_text(image_descriptions[image_counter - 1])

            image_counter += 1

    return image_descriptions_dict

def extract_tables_from_pdf(pdf_path, tables_folder, paper_id):
    try:
        # Extract tables from the PDF
        tables = read_pdf(pdf_path, pages='all', multiple_tables=True)

        # Check if tables were found
        if not tables:
            error_message = f"No tables found in the file: {pdf_path}"
            print(error_message)
            logging.error(error_message)
            return

        # Save each table as a CSV file
        for i, table in enumerate(tables):
            table_file_path = os.path.join(tables_folder, f"table_{paper_id}_{i + 1}.csv")
            table.to_csv(table_file_path, index=False)

        print(f"Tables extracted and saved for paper {paper_id}.")
    except Exception as e:
        error_message = f"Error extracting tables from file {pdf_path}: {str(e)}"
        print(error_message)
        logging.error(error_message)

def process_paper(pdf_file_path, xml_file_path, output_base_folder, complete_output_folder, incomplete_output_folder, paper_id):
    try:
        # Extract sections using Grobid
        sections, title, image_descriptions = extract_sections_from_xml(xml_file_path)

        # Check if all sections have content
        complete = all(section["content"] for section in sections)

        # Set the base paper folder based on completion status
        if complete:
            paper_folder = os.path.join(complete_output_folder, f"paper_{paper_id}")
        else:
            paper_folder = os.path.join(incomplete_output_folder, f"paper_{paper_id}")

        # Create folders for the paper
        images_folder = os.path.join(paper_folder, "images")
        tables_folder = os.path.join(paper_folder, "tables")
        os.makedirs(images_folder, exist_ok=True)
        os.makedirs(tables_folder, exist_ok=True)

        # Save sections to JSON in the paper folder
        output_json_path = os.path.join(paper_folder, f"paper_{paper_id}.json")
        with open(output_json_path, 'w') as json_file:
            json.dump(sections, json_file, indent=2)

        # Extract images
        image_descriptions_dict = extract_images_from_pdf(pdf_file_path, images_folder, image_descriptions)

        # Save image descriptions to JSON
        image_descriptions_path = os.path.join(images_folder, "image_descriptions.json")
        with open(image_descriptions_path, 'w') as json_file:
            json.dump(image_descriptions_dict, json_file, indent=2)

        # Extract tables
        extract_tables_from_pdf(pdf_file_path, tables_folder, paper_id)

        print(f"Processed paper {paper_id} successfully.")
    except Exception as e:
        print(f"Error processing paper {paper_id}: {e}")
        logging.error(f"Error processing paper {paper_id}: {e}")

        
def process_files_in_folder(pdf_folder_path, output_base_folder, complete_output_folder, incomplete_output_folder, csv_path):
    # Read the CSV file to get the mapping of titles to IDs
    df = pd.read_csv(csv_path)

    # Add .pdf extension to filenames in the DataFrame
    df['filename'] = df['filename'].str.strip() + '.pdf'

    # Ensure the output folder exists
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)

    # Get all PDF files in the folder
    pdf_files = glob.glob(os.path.join(pdf_folder_path, '*.pdf'))

    for pdf_file_path in pdf_files:
        try:
            # Get the filename from the pdf_file_path
            filename = os.path.basename(pdf_file_path)

            # Find the matching row in the CSV file by filename
            matching_row = df[df['filename'] == filename]

            if not matching_row.empty:
                paper_id = matching_row['No_de_Ref'].values[0]

                # Process the PDF with Grobid to get the XML
                xml_response = process_fulltext_document(service_name, pdf_file_path)

                if xml_response:
                    xml_output_folder = "../xml_results2/"
                    if not path.exists(xml_output_folder):
                        makedirs(xml_output_folder)

                    base_filename = path.splitext(filename)[0]
                    xml_file_path = path.join(
                        xml_output_folder, f"{base_filename}.xml")

                    with open(xml_file_path, "w") as xml_file:
                        xml_file.write(xml_response)

                    # Process the paper

                    process_paper(pdf_file_path, xml_file_path, output_base_folder, complete_output_folder, incomplete_output_folder, paper_id)
                else:
                    error_message = f"No se pudo procesar el XML para el archivo: {filename}"
                    print(error_message)
                    logging.error(error_message)
            else:
                error_message = f"No se encontró una coincidencia para el archivo: {filename}"
                print(error_message)
                logging.error(error_message)
        except Exception as e:
            error_message = f"Error procesando el archivo {pdf_file_path}: {str(e)}"
            print(error_message)
            logging.error(error_message)


# Example usage
#xml_folder_path = '../xml_results/'
output_folder_path = '../json_results/'
csv_path = '../paper_references.csv'
process_files_in_folder(pdf_folder, output_base_folder, complete_output_folder, incomplete_output_folder, csv_path)

# Check if the log file exists
if os.path.exists(log_file_path):
    print(f"El archivo de log se ha creado correctamente: {log_file_path}")
else:
    print("No se ha creado el archivo de log.")
