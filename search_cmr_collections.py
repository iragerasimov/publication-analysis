# We utilize Earthdata Common Metadata Repository API, see https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
# Specifically, we query CMR for extended UMM fields: https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#umm-json
# only records that have non-empty DOI attribute with one of the prefixes 10.5067, 10.3334, or 10.7927 are retained
# the output is stored in data/cmr_collections.json

import json
import requests
import os
import re
import pandas as pd

cmr_recs = list()
page_cnt=55
cnt = 0
for page in range(1,page_cnt):
  url=f'https://cmr.earthdata.nasa.gov/search/collections.umm_json?page_num={page}&page_size=1000'
  response = requests.get(url)
  # print(url)
  if response.status_code == 200:
    data = response.json()
  else:
    print(url)
    print("response code", response.status_code)

  if data["hits"]:
    for element in data['items']:
      shortName = element['umm']['ShortName']
      version = element['umm']['Version']
      concept = element["meta"]["concept-id"]
      doi = None
      if element['umm'].get('DOI', '') and element['umm']['DOI'].get('DOI', ''):
        doi = element['umm']['DOI']['DOI']
        if not re.match('(10\.5067)|(10\.3334)|(10\.7927)',doi):
          continue
      dsl = None
      if element['umm'].get('RelatedUrls', ''):
        for url in element['umm']['RelatedUrls']:
          if re.match('DATA SET LANDING PAGE', url['Type']):
            dsl = url['URL']
      if not dsl and not doi:
        continue
      plevel = element['umm']['ProcessingLevel']['Id']
      fformat = 'None'
      if element['umm'].get('ArchiveAndDistributionInformation', '') and element['umm']['ArchiveAndDistributionInformation'].get('FileDistributionInformation', '') and element['umm']['ArchiveAndDistributionInformation']['FileDistributionInformation'][0].get('Format', ''):
        fformat = element['umm']['ArchiveAndDistributionInformation']['FileDistributionInformation'][0]['Format']

      print(shortName, version, doi, dsl)
      services = list()
      tools = list()
      if element["meta"].get("associations", ''):
        if element["meta"]["associations"].get("services"):
          services = element["meta"]["associations"]["services"]
        if element["meta"]["associations"].get("tools", ''):
          tools = element["meta"]["associations"]["tools"]
      SKs = list()
      if element['umm'].get("ScienceKeywords", ''):
        for sk_dict in element['umm']["ScienceKeywords"]: 
          print(sk_dict, sk_dict['Category'])
          if not re.match(sk_dict['Category'], "EARTH SCIENCE"):
            continue
          sk = sk_dict['Topic']
          if sk_dict.get('Term', ''):
            sk = sk+' > '+sk_dict['Term']
          if sk_dict.get('VariableLevel1', ''):
            sk = sk+' > '+sk_dict['VariableLevel1']
          if sk_dict.get('VariableLevel2', ''):
            sk = sk+' > '+sk_dict['VariableLevel2']
          if sk_dict.get('VariableLevel3', ''):
            sk = sk+' > '+sk_dict['VariableLevel3']
          if sk_dict.get('DetailedVariable', ''):
            sk = sk+' > '+sk_dict['DetailedVariable']
          #sk = ' > '.join(sk_dict.values())
          #print(sk)
          #exit()
          SKs.append(sk)
      cmr_recs.append({'Concept': concept, 'ShortName': shortName, 'VersionId': version, 'DOI': doi, 'DSL': dsl, 'Format': fformat, 'Level': plevel, 
          'Services': services, 'Tools': tools, 'ScienceKeywords': SKs})
      cnt+=1
      print(cnt)

with open("data/cmr_collections.json", "w") as fp:
  json.dump(cmr_recs, fp, indent=4)


exit()
