import xml.etree.ElementTree as ET
import json
import pandas as pd
import glob
import re
import unicodedata
import os
import logging

# Configure logging
log_file_path = 'process_errors.log'
logging.basicConfig(filename=log_file_path, level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

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

    sections = [
        {"title": "Abstract", "content": abstract_content},
        {"title": "Experimental", "content": experimental_content},
        {"title": "Results and discussion", "content": results_discussion_content},
        {"title": "Conclusions", "content": conclusions_content},
    ]

    if supporting_information_content:
        sections.append({"title": "Supporting Information",
                        "content": supporting_information_content})

    return sections, title

def process_files_in_folder(xml_folder_path, complete_output_folder, incomplete_output_folder, csv_path):
    # Read the CSV file to get the mapping of titles to IDs
    df = pd.read_csv(csv_path)

    # Add .xml extension to filenames in the DataFrame
    df['filename'] = df['filename'].str.strip() + '.xml'

    # Ensure the output folders exist
    if not os.path.exists(complete_output_folder):
        os.makedirs(complete_output_folder)
    if not os.path.exists(incomplete_output_folder):
        os.makedirs(incomplete_output_folder)

    # Get all XML files in the folder
    xml_files = glob.glob(os.path.join(xml_folder_path, '*.xml'))

    for xml_file_path in xml_files:
        try:
            # Extract sections and title
            sections, title = extract_sections_from_xml(xml_file_path)

            # Get the filename from the xml_file_path
            filename = os.path.basename(xml_file_path)

            # Find the matching row in the CSV file by filename
            matching_row = df[df['filename'] == filename]

            if not matching_row.empty:
                paper_id = matching_row['No_de_Ref'].values[0]
                json_file_name = f'paper_{paper_id}.json'

                # Check if all sections have content
                all_sections_have_content = all(section['content'] for section in sections)

                if all_sections_have_content:
                    output_json_path = os.path.join(complete_output_folder, json_file_name)
                else:
                    output_json_path = os.path.join(incomplete_output_folder, json_file_name)

                # Write the extracted sections to JSON
                json_data = json.dumps(sections, indent=2)
                with open(output_json_path, 'w') as json_file:
                    json_file.write(json_data)

                print(f"JSON saved successfully in {output_json_path}")
            else:
                error_message = f"No match found for file: {filename}"
                print(error_message)
                logging.error(error_message)
        except Exception as e:
            error_message = f"Error processing file {xml_file_path}, Title: {title}, Error: {str(e)}"
            print(error_message)
            logging.error(error_message)

# Example usage
xml_folder_path = '../xml_results/'
complete_output_folder = '../json_results/complete/'
incomplete_output_folder = '../json_results/incomplete/'
csv_path = '../paper_references.csv'
process_files_in_folder(xml_folder_path, complete_output_folder, incomplete_output_folder, csv_path)

# Check if log file exists
if os.path.exists(log_file_path):
    print(f"Log file created successfully: {log_file_path}")
else:
    print("Log file not created.")
