import requests
from xml.etree import ElementTree


def fetch_abstracts_europe_pmc(doi):
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
                abstract_text = result.findtext('abstractText') or None
                title = result.findtext('title') or None
                authors = result.findtext('authorString') or None
                affiliation = result.findtext('affiliation') or None
                journal = "TBD: GET JOURNAL ID FROM DOI" # TODO: get from DOI (create a utility for this)
                citation_count = result.findtext('citedByCount') or None
                publication_date = result.findtext('firstPublicationDate') or None

                print(f"Abstract found for DOI: {doi}")
                abstract_dict = {
                      'doi': doi,
                      'title': title,
                      'author': authors,
                      'abstract': abstract_text,
                      'affiliation': affiliation,
                      'journal': journal,
                      'citation_count': citation_count,
                      'publication_date': publication_date,
                }
                
        else:  
            print(f"No data found for DOI: {doi}")
            return None
        
    except Exception as e:
        print(f"Error processing DOI {doi}: {str(e)}")
        return None
   
    return abstract_dict


def fetch_references_crossref(doi):
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
                ref_doi = ref.get('DOI', 'Not available')       
                references.append(ref_doi)
            print(f"References found for DOI: {doi}")
        else:
            print(f"No references found for DOI: {doi}")

    except requests.exceptions.RequestException as e:
        print(f"Error processing DOI {doi}: {str(e)}")

    print(f"Processed {len(references)} references")
    return references

