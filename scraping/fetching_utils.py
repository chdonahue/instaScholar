import requests
from xml.etree import ElementTree
import logging
from utils.path import resolve_data_path
from time import sleep


def fetch_abstracts_europe_pmc(doi, logger):
    """ 
    This function fetches abstracts from Europe PMC for a list of DOIs.

    Args:
        doi (str): The DOI of the paper to fetch.

    Returns:
        abstract_dict (dict): A dictionary with the following keys:
            - 'doi' (str): The DOI of the paper.
            - 'title' (str): The title of the paper.
            - 'author' (str): The authors of the paper.
            - 'abstract' (str): The abstract of the paper.
            - 'affiliation' (str): The affiliation of the authors.
            - 'journal' (str): The journal of the paper.
            - 'citation_count' (str): The number of citations to the paper.
            - 'publication_date' (str): The publication date of the paper, formatted as YYYY-MM-DD
    """
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    abstract_dict = {}
    try:
        params = {
            'query': f'DOI:"{doi}"',
            'resultType': 'core',
            'format': 'xml'
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        root = ElementTree.fromstring(response.content)
        result = root.find('.//result')
        
        if result is not None:
            issn, journal_name = get_journal_info_from_doi(doi, logger)
            abstract_text = result.findtext('abstractText') or None
            title = result.findtext('title') or None
            authors = result.findtext('authorString') or None
            affiliation = result.findtext('affiliation') or None
            citation_count = result.findtext('citedByCount') or None # THIS IS VERY OUTDATED
            publication_date = result.findtext('firstPublicationDate') or None
            references = fetch_references_crossref(doi, logger)

            logger.info(f"Abstract found for DOI: {doi}")
            abstract_dict = {
                    'doi': doi,
                    'title': title,
                    'author': authors,
                    'abstract': abstract_text,
                    'affiliation': affiliation,
                    'journal': journal_name,
                    'issn': issn,
                    'citation_count': citation_count,
                    'publication_date': publication_date,
                    'references': references,
            }
                
        else:  
            logger.info(f"No data found for DOI: {doi}")
            return None
        
    except Exception as e:
        logger.info(f"Error processing DOI {doi}: {str(e)}")
        return None
   
    return abstract_dict


def fetch_references_crossref(doi, logger):
    """ 
    This function fetches references from Crossref for a given DOI. Crossref is better for references.

    Args:
        doi (str): The DOI of the paper to fetch references for.

    Returns:
        references (list): A list of DOIs
    """
    base_url = "https://api.crossref.org/works/"
    references = []
    try:
        url = base_url + doi
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'reference' in data['message']:
            for ref in data['message']['reference']:
                ref_doi = ref.get('DOI', None)  
                if ref_doi is not None:     
                    references.append(ref_doi)
            logger.info(f"References found for DOI: {doi}")
        else:
            logger.info(f"No references found for DOI: {doi}")

    except requests.exceptions.RequestException as e:
        logger.info(f"Error processing DOI {doi}: {str(e)}")

    logger.info(f"Processed {len(references)} references")
    return references



def fetch_dois_from_issn(issn, start_date, end_date, logger):
    """
    Given an issn and start/end dates ('YYYY-MM-DD'), returns a list of dois.
    Uses the Crossref API
    Args:
        issn (str): unique journal identifier
        start_date (str): YYYY-MM-DD
        end_date (str): YYYY-MM-DD
    Returns:
        doi_dict (dict): ISSN (key)->list of DOI article identifiers for the specified date range
    """
    base_url = "https://api.crossref.org/works"
    
    params = {
        "filter": f"issn:{issn},from-pub-date:{start_date},until-pub-date:{end_date}",
        "rows": 100,
        "cursor": "*"
    }
    
    headers = {
        "User-Agent": "MyApp/1.0 (mailto:your-email@example.com)"
    }
    
    all_dois = []
    doi_dict = {}
    
    while True:
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            items = data['message']['items']
            dois = [item['DOI'] for item in items if 'DOI' in item]
            if not dois:  # If no new DOIs are found, break the loop
                break
            all_dois.extend(dois)
            
            logger.info(f"Fetched {len(dois)} DOIs. Total: {len(all_dois)}")
            
            next_cursor = data['message'].get('next-cursor')
            if not next_cursor:
                break
            
            params['cursor'] = next_cursor
            sleep(1)  # Be nice to the API
            
        except requests.exceptions.RequestException as e:
            logger.info(f"An error occurred: {e}")
            break
        doi_dict[issn] = all_dois
    return doi_dict

def get_journal_info_from_doi(doi, logger):
    """
    Grabs journal name and ISSN from a DOI
    """

    base_url = "https://api.crossref.org/works/"
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.get(base_url + doi, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        message = data['message']
        
        # Get ISSN (prefer print ISSN if available)
        issn_list = message.get('ISSN', [])
        issn_types = message.get('issn-type', [])
        print_issn = next((item['value'] for item in issn_types if item['type'] == 'print'), None)
        issn = print_issn or (issn_list[0] if issn_list else None)
        
        # Get journal name
        journal_name = message.get('container-title', [None])[0]
        
        return issn, journal_name
    
    except (requests.exceptions.RequestException,
            KeyError, IndexError, ValueError,
            Exception) as e:
        logger.error(f"Error processing DOI {doi}: {str(e)}")
        return None
