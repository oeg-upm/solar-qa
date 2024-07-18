import xml.etree.ElementTree as ET
import json


def extract_sections_from_xml(file_path, output_json_path):
    # Load XML from a file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Namespace, if the XML uses namespaces
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Function for extracting content under a specific tag, handles namespaces
    def extract_content_by_tag(tag_name):
        content = []
        # Adjust the label name for the namespace if necessary.
        path = f".//{{{ns['tei']}}}{tag_name}" if ns else f".//{tag_name}"
        for elem in root.findall(path):
            text = ''.join(elem.itertext())
            if text:
                content.append(text.strip())
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
                text = ''.join(elem.itertext())
                if text:
                    content.append(text.strip())
        return " ".join(content)

    # Function to extract content by specific ID
    def extract_by_xml_id(xml_id):
        for elem in root.findall(".//*[@xml:id='" + xml_id + "']"):
            return " ".join(elem.itertext())

    # Extraction of sections
    """ abstract_content = extract_content_by_keywords(
        ["Introduction"], "Experimental") """
    abstract_content = extract_content_by_tag("abstract")
    experimental_content = extract_content_by_keywords(
        ["Experimental", "Experimental studies", "Experiments", "Methods"], "Results and discussion")
    results_discussion_content = extract_content_by_keywords(
        ["Results and discussion", "Result and discussion", "Results"], "Conclusion")
    supporting_information_content = extract_content_by_keywords(
        ["Supporting Information", "Supporting"], "Conclusion")
    conclusions_content = extract_content_by_keywords(
        ["Conclusion", "Conclusions"], "Conclusion")
    # specific_id_content = extract_by_xml_id("_ZT2rFX7")

    sections = [
        {"title": "Abstract", "content": abstract_content},
        {"title": "Experimental", "content": experimental_content},
        {"title": "Results and discussion", "content": results_discussion_content},
        {"title": "Conclusions", "content": conclusions_content},
    ]

    if supporting_information_content:
        sections.append({"title": "Supporting Information",
                        "content": supporting_information_content})

    json_data = json.dumps(sections, indent=2)

    with open(output_json_path, 'w') as json_file:
        json_file.write(json_data)

    return f"JSON guardado correctamente en {output_json_path}"


# Example usage
xml_file_path = '../xml_results/papers1/paper_16238777645e67b6116072c5.89519248.xml'
output_json_path = '../json_results/papers1/paper_.json'
resultado = extract_sections_from_xml(xml_file_path, output_json_path)
print(resultado)
