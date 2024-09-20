# Command line script to scrape a journal (ISSN) given a date_start and date_end
# Science: 0036-8075
import argparse
import os
import logging
import urllib
from google.cloud import firestore
from db.db_utils import write_data
from scraping.fetching_utils import fetch_dois_from_issn, fetch_abstracts_europe_pmc


def setup_logger(issn, start_date, end_date):
    log_dir = os.path.join('.', 'scraping', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{issn}_{start_date}_{end_date}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    root_logger = logging.getLogger(issn)
    root_logger.setLevel(logging.INFO)

    # Remove handlers to avoid duplicate logs:
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    file_handler = logging.FileHandler(log_path, mode='w')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    return root_logger

def main(issn, start_date, end_date, override):
    logger = setup_logger(issn, start_date, end_date)
    logger.info(f"Script started with ISSN: {issn}, Start Date: {start_date}, End Date: {end_date}, Override: {override}")
 

    project_id = 'instascholar'
    db = firestore.Client(project=project_id)
    collection_name = 'papers'
    collection_ref = db.collection(collection_name)
    logger.info("Extracting doi list from ISSN and specified date range")
    doi_dict = fetch_dois_from_issn(issn, start_date, end_date, logger)
    if not doi_dict:
        logger.info(f'No Papers found for {issn} from {start_date} to {end_date}')
        return
    doi_list = doi_dict[issn]

    for doi in doi_list:
        encoded_doi = urllib.parse.quote(doi, safe='') # Remove slash when encoding doi for db
        doc_ref = collection_ref.document(encoded_doi)
        if doc_ref.get().exists and override is False:  # do not process if exists and override is false
            print(f'{doi} already exists in db')
        else:
            logger.info(f"Scraping data for {doi}")
            data = fetch_abstracts_europe_pmc(doi, logger)
            if data is not None:
                write_data(db, collection_name, encoded_doi, data, override=override)            

        
    logger.info("Scraping Complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process ISSN and date range")
    parser.add_argument("--issn", type=str, required=True, help="ISSN number")
    parser.add_argument("--start_date", type=str, required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end_date", type=str, required=True, help="End date in YYYY-MM-DD format")
    parser.add_argument("--override", action="store_true", help="Set the override flag to True")

    
    args = parser.parse_args()
    
    main(args.issn, args.start_date, args.end_date, args.override)