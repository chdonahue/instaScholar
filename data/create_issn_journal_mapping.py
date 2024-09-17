"""
Quick script that creates the ISSN_journal_dict.json file used for mappings
"""
import pandas as pd
import json
from utils.path import resolve_data_path

# Dataframe of 2023 top 2000 journals scraped from scigo:
journal_issn_df = pd.read_csv(resolve_data_path('top_journals.csv'))
mapping = dict(zip(journal_issn_df['ISSN'], journal_issn_df['Title']))
mapping = {k:v for k,v in mapping.items() if pd.notna(k)} # remove NaN
with open(resolve_data_path('ISSN_journal_dict.json'), 'w') as f:
    json.dump(mapping, f)
