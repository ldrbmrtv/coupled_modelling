import requests
import json


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
