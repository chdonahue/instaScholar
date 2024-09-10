""" 
This script will build a csv of the top 2000 journals based on Scimago. 
It will also fetch the ISSN for each journal separately. 
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time



def scrape_scimagojr_table(year=2023, max_journals=2000):
    """ 
    This function scrapes the Scimago journal rankings table for a given year.

    Args:
        year (int): The year to scrape the data for. Defaults to 2023.
        max_journals (int): The maximum number of journals to scrape. Defaults to 2000.

    Returns:
        df (pd.DataFrame): A DataFrame containing the journal rankings.
    """
    base_url = "https://www.scimagojr.com/journalrank.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.scimagojr.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    all_rows = []
    page = 1
    table_headers = None
    
    while len(all_rows) < max_journals:
        params = {
            'year': year,
            'page': page,
            'total_size': 50  # Number of entries per page
        }
        
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                print(f"No table found on page {page} for year {year}")
                break
            
            # Extract headers from the first page
            if page == 1:
                table_headers = [th.text.strip() for th in table.find('tr').find_all('th')]
                print(f"Detected {len(table_headers)} columns: {table_headers}")
            
            rows = table.find_all('tr')[1:]  # Skip header row
            if not rows:
                break  # No more rows, we've reached the end
            
            for tr in rows:
                row = [td.text.strip() for td in tr.find_all('td')]
                if row:  # Only add non-empty rows
                    all_rows.append(row)
                if len(all_rows) >= max_journals:
                    break
            
            print(f"Extracted {len(all_rows)} journal entries for year {year}")
            page += 1
            time.sleep(2)  # Be polite to the server
            
        except requests.RequestException as e:
            print(f"An error occurred for year {year}, page {page}: {e}")
            break
    
    if not all_rows or not table_headers:
        print(f"No data extracted for year {year}")
        return None
    
    # Ensure all rows have the same number of columns as the header
    all_rows = [row for row in all_rows if len(row) == len(table_headers)]
    
    if not all_rows:
        print(f"No valid rows extracted for year {year}")
        return None
    
    df = pd.DataFrame(all_rows, columns=table_headers)
    df['Year'] = year  # Add year column
    return df

def get_issn_from_title(journal_title):
    """ 
    This function fetches the ISSN for a given journal title from the Crossref API.
    Operates on one journal title at a time. 

    Args:
        journal_title (str): The title of the journal to fetch the ISSN for.

    Returns:
        issn (str): The ISSN of the journal.
    """
    base_url = "https://api.crossref.org/works"
    params = {
        "query.container-title": journal_title,
        "rows": 1,  # We only need the top result
        "select": "ISSN,container-title",  # Only retrieve ISSN and journal title
    }
    headers = {
        "User-Agent": "YourAppName/1.0 (mailto:your@email.com)"  # Replace with your info
    }

    try:
        time.sleep(0.5) # be nice to the API
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data["message"]["items"]:
            item = data["message"]["items"][0]
            issn_list = item.get("ISSN", [])
            if issn_list:
                return issn_list[0]  # Return the first ISSN if multiple are present
            else:
                print(f"No ISSN found for journal: {journal_title}")
        else:
            print(f"No results found for journal: {journal_title}")

    except requests.RequestException as e:
        print(f"An error occurred while searching for {journal_title}: {e}")

    return None


def main():
    df = scrape_scimagojr_table(year=2023, max_journals=2000)
    df['ISSN'] = df['Title'].apply(get_issn_from_title)
    df.to_csv('data/top_journals.csv', index=False)


if __name__ == "__main__":
    main()

