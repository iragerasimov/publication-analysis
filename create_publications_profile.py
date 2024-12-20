import os
import json
import re
import glob
import csv
from date_extractor import extract_dates
import unicodedata # used to transform unicode to ascii such as '\u2026' to '...'
from bs4 import BeautifulSoup # used together with unescape to remove html tags such as &lt;
from html import unescape # used together with unescape to remove html tags such as &lt;

zot_doi_list = []
refs_list = []
json_folder_path = 'data'
pset = 'all'

zot_pubs_file = "zot_pubs_"+pset+".json"
with open(os.path.join(json_folder_path, zot_pubs_file)) as json_publications_file:
  zot_list = json.load(json_publications_file)

with open(os.path.join(json_folder_path,'doi2cmr.json')) as doi2cmr_file:
  doi2cmr = json.load(doi2cmr_file)

regex1 = r"\d{4}"
def get_year(date):
  years = re.search(regex1, date)
  return years[0]

pubs = []

for pub_item in zot_list:
    pub = {}
    doi = pub_item['data'].get('DOI', '')
    pub['title'] = pub_item['data']['title']
    pub['title'] = BeautifulSoup(unescape(pub['title']), 'lxml').text #sanitize title from html tags
    pub['title'] = unicodedata.normalize('NFKD', pub['title']).encode('ascii', 'ignore').decode('ascii') # sanitize title from unicode

    date = pub_item['data'].get('date', '')
    if date:
      date = get_year(date)
      pub['year'] = date
    else:
      print("No year for "+pub['title'])
      continue
    if not doi and re.search("DOI: ", pub_item['data']['extra']):
      doi = re.sub("DOI: ", '', pub_item['data']['extra'])
    pub['doi'] = doi.upper()
    if len(pub_item['data']['tags']):
      for tag in pub_item["data"]["tags"]:
        if re.match('doi:', tag["tag"]):
          doi = re.sub('doi:', '', tag["tag"])
          if pub.get('DOIs', ''):
            pub['DOIs'].append(doi)
          else:
            pub['DOIs'] = [doi]
        elif re.match('DAAC:', tag["tag"]):
          daac = re.sub('DAAC:', '', tag["tag"])
          if pub.get('DAACs', ''):
            pub['DAACs'].append(daac)
          else:
            pub['DAACs'] = [daac]
    if not pub.get('DOIs', ''):
      continue
    pub['ShortNames'] = []
    pub['Formats'] = []
    pub['Levels'] = []
    for ds_doi in pub['DOIs']:
      if not doi2cmr.get(ds_doi, ''):
        continue
      pub['ShortNames'].append(doi2cmr[ds_doi]['ShortName'])
      pub['Formats'].append(doi2cmr[ds_doi]['Format'])
      level = doi2cmr[ds_doi]['Level']
      level = re.sub('Level ', '', level)
      level = re.sub('Not provided', 'NA', level)
      pub['Levels'].append(level)

    pub['DOIs'] = list(set(pub['DOIs']))
    pub['DAACs'] = list(set(pub['DAACs']))
    pub['ShortNames'] = list(set(pub['ShortNames']))
    pub['Formats'] = list(set(pub['Formats']))
    pub['Levels'] = list(set(pub['Levels']))
    pubs.append(pub)

with open(os.path.join(json_folder_path, "pubs_"+pset+".json"), "w") as fp:
  json.dump(pubs, fp, indent=4)

