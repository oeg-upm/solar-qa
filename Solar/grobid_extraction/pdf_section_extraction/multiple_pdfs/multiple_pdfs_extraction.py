from grobid_client.grobid_client import GrobidClient
import json
import xmltodict
from os import path, makedirs, listdir

# GROBID client configuration
client = GrobidClient(config_path="../settings/config.json")

service_name = "processFulltextDocument"
pdf_folder = "../documents"


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


def process_all_pdfs(pdf_folder):
    for filename in listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_file = path.join(pdf_folder, filename)
            print(f"Processing: {pdf_file}")
            xml_response = process_fulltext_document(service_name, pdf_file)

            if xml_response:
                dict_data = xmltodict.parse(xml_response)
                json_data = json.dumps(dict_data, indent=4)

                # Output folders for XML and JSON
                xml_output_folder = "../xml_results"
                # json_output_folder = "../json_results"

                if not path.exists(xml_output_folder):
                    makedirs(xml_output_folder)
                """ if not path.exists(json_output_folder):
                    makedirs(json_output_folder) """

                base_filename = path.splitext(filename)[0]
                xml_file_path = path.join(
                    xml_output_folder, f"{base_filename}.xml")
                # json_file_path = path.join(json_output_folder, f"{base_filename}.json")

                with open(xml_file_path, "w") as xml_file:
                    xml_file.write(xml_response)
                """ with open(json_file_path, "w") as json_file:
                    json_file.write(json_data) """

                print(f"XML and JSON files saved for {filename}")


process_all_pdfs(pdf_folder)
