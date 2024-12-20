# Obtain publication citation records and their tags from Zotero library: https://www.zotero.org/groups/4567966/eosdis_dci/collections/KVUXVEN9

import os
import json
import re
import glob
import time
from pyzotero import zotero

zot_cred_file = 'zotero_credentials.json'
json_folder_path = 'data'

with open(os.path.join(json_folder_path+'/'+zot_cred_file), 'r') as fp: 
    z_credentials = json.load(fp)

zot = zotero.Zotero(z_credentials['library_id'], z_credentials['library_type'], z_credentials['api_key'])

zot_doi_list = []
zot_notes = []
zot_pubs = []
zot_atts = []
json_folder_path = "data"
regex = r"(?:[(<>)]|)"

# All DAACs collection contains citations collected for all Earth dataset DOIs
# If Citations 
coll_key = {	
            'All':'KVUXVEN9'
	}

coll = 'All'

try:
  items = zot.collection_items(coll_key[coll], limit=1000) 
  while True:
    for pub_item in items:
      # skip notes and attachments
      if re.search("note", pub_item['data']['itemType']) or re.search("attachment", pub_item['data']['itemType']):
        pass
      else:
        zot_pubs.append(pub_item)
    items = zot.follow()
    time.sleep(1)
except StopIteration:
  print('\nAll items processed')
except Exception as ex:
  print(ex)

with open(os.path.join(json_folder_path, "zot_pubs_"+coll.lower()+".json"), "w") as fp:
  json.dump(zot_pubs, fp, indent=4)
