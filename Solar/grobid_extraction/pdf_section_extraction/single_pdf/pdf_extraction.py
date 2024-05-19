from grobid_client.grobid_client import GrobidClient
import json
import xmltodict
import os

# GROBID client configuration
client = GrobidClient(config_path="../settings/config.json")

service_name = "processFulltextDocument"
pdf_file = "../documents/paper_1.pdf"


def process_fulltext_document(service, file):
    rsp = client.process_pdf(service, file,
                             generateIDs=True,
                             consolidate_header=True,
                             consolidate_citations=False,
                             include_raw_citations=False,
                             include_raw_affiliations=False,
                             tei_coordinates=True,
                             segment_sentences=True)

    if rsp[1] == 200:  # Check http status is 200
        xml_content = rsp[2]  # rsp[2] should be the xml string
        return xml_content
    else:
        print("Error:", rsp[1])
        return None


xml_response = process_fulltext_document(service_name, pdf_file)
if xml_response:
    # Convert XML to dictionary
    dict_data = xmltodict.parse(xml_response)

    # Convert dictionary to JSON
    # json_data = json.dumps(dict_data, indent=4)

    # Make the folder if it doesn't exist
    output_folder_xml = "../xml_results"
    if not os.path.exists(output_folder_xml):
        os.makedirs(output_folder_xml)

    # Save XML file
    output_path_xml = os.path.join(output_folder_xml, "paper_1.2.xml")
    with open(output_path_xml, "w") as xml_file:
        xml_file.write(xml_response)
    print(f"XML file saved in {output_path_xml}")

    # Crear la carpeta si no existe
    """ output_folder = "../json_results"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder) """

    # Guardar JSON en un archivo
    """  output_path = os.path.join(output_folder, "paper_11.json")
    with open(output_path, "w") as json_file:
        json_file.write(json_data) """

    # print(f"JSON file saved in {output_path}")
else:
    print("No XML response.")
