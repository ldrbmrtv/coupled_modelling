import os
import requests
import json


def main():
    # Define the paths for ontology and JSON folders
    owl_folder = '04_04_2023\ontology'
    json_folder = '04_04_2023\json'
    if not os.path.exists(json_folder):
        os.mkdir(json_folder)

    # Extract labels from OWL files
    labels = scan_folder(owl_folder)

    if labels:
        # Process each label using the util_falcon() function
        answers = {}
        for label in labels:
            answer = util_falcon(label)
            answers[label] = answer

        # Write the results to a JSON file
        json_file_path = os.path.join(json_folder, "falcon_mapping.json")
        with open(json_file_path, "w", encoding="utf8") as f:
            json.dump(answers, f, ensure_ascii=False, indent=4)

    print("Processing completed. Results saved to:", json_file_path)


def util_falcon(text):
    """
    Calls the Falcon API to extract entities and relations related to the given text.

    Args:
        text (str): The input text to process.

    Returns:
        dict: A dictionary containing the extracted entities and relations.
    """
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "text": text
    }

    response = requests.post("https://labs.tib.eu/falcon/falcon2/api?mode=long&db=1",
                             headers=headers, data=json.dumps(data))

    # Convert the response content from bytes to string
    data_str = response.content.decode('utf-8')

    # Parse the response JSON
    print(data_str)
    parsed_data = json.loads(data_str)

    # Extract entities and relations from the parsed data
    entities_wiki = parsed_data.get('entities_wikidata', [])
    relations_wiki = parsed_data.get('relations_wikidata', [])
    entities_db = parsed_data.get('entities_dbpedia', [])
    relations_dbpedia = parsed_data.get('relations_dbpedia', [])

    # Construct the answer dictionary
    answer = {}
    if entities_wiki:
        answer["entities_wiki"] = [entry["URI"]
                                   for entry in entities_wiki]
    if relations_wiki:
        answer["relations_wikidata"] = [entry["URI"]
                                        for entry in relations_wiki]
    if entities_db:
        answer["entities_db"] = [entry["URI"]
                                 for entry in entities_db]
    if relations_dbpedia:
        answer["relations_dbpedia"] = [entry["URI"]
                                       for entry in relations_dbpedia]

    return answer


def scan_folder(path):
    """
    Scans the specified folder for OWL files and extracts labels from them.

    Args:
        path (str): The path to the folder to scan.

    Returns:
        set: A set of unique labels extracted from the OWL files.
    """
    labels = set()
    for file_name in os.listdir(path):
        if file_name.endswith('.owl'):
            file_path = os.path.join(path, file_name)
            labels.update(extract_labels_from_owl(file_path))
    return labels


def extract_labels_from_owl(file_path):
    """
    Extracts labels from the specified OWL file.

    Args:
        file_path (str): The path to the OWL file.

    Returns:
        set: A set of unique labels extracted from the OWL file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
        labels = set()
        for line in lines:
            if not line.startswith('  <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">'):
                continue
            line = line.replace(
                '  <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">', "")
            line = line.replace('</rdfs:label>\n', "")
            labels.add(line)
        return labels


if __name__ == "__main__":
    main()
