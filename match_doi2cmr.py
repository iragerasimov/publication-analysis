# This program tries to find matching CMR entries for registered EOSDIS DOIs 
# It also tries to sort the data format indicated in CMR entries to some uniform format names
# FORMATS=['ASCII','Binary','HDF-EOS','HDF-EOS2','HDF-EOS4','HDF-EOS5','NetCDF','NetCDF-4','NetCDF-5','HDF','HDF4','HDF5','GeoTIFF','GRIB','PNG','ICARTT','GIF','JPEG', 'Shapefile','Multimedia','Grid']
# The program needs:
#   * data/doi2cmr_manual.json - matches of retired DOIs to current CMR entries
#   * data/all_eosdis_dois_20240223.csv - dump of EOSDIS database of registered DOIs with prefix 10.5067
#   * data/sedac_ornl_dois_20240223.csv - dump of EOSDIS database of ORNL and SEDAC DOIs
#   * data/cmr_collections.json - this is output from search_cmr_collections.py
# The program outputs data/doi2cmr.json

import json
import requests
import os
import re
import pandas as pd

# data/doi2cmr_manual.json is list of doi2cmr matches that we composed by hand. 
# It matches DOIs of retired collections to CMR entries of collections currently offered in CMR
# It also lists DOIs that are registered as datasets, however they are assigned to the artifacts like software or documents
with open('data/doi2cmr_manual.json') as f1:
  doi2cmr_man = json.load(f1)

# load CMR collection that have either 10.5067, 10.3334 or 10.7  DOIs or RelatedURL DOI Web page
with open('data/cmr_collections.json') as f2:
  cmr_colls = json.load(f2)

csv_all_file = 'data/all_eosdis_dois_20240223.csv'
csv_so_file = 'data/sedac_ornl_dois_20240223.csv'

def getDataFrameFromCSV(csv_file):
  column_names = ['RESOURCE_TYPE','DOI_NAME', 'SPECIAL', 'URL', 'YEAR']
  df = pd.read_csv(csv_file, encoding='unicode_escape') # note to self: change to variable filename
  df = df[column_names]
  df = df.rename(columns={'DOI_NAME': 'DOI', 'SPECIAL': 'ShortName'})
  return df.to_dict('records')

def getDataFrameFromCSV_SO(csv_file):
  column_names = ['RESOURCE_TYPE','DOI_NAME','DOI_SPECIAL', 'URL','YEAR']
  df = pd.read_csv(csv_file, encoding='unicode_escape') # note to self: change to variable filename
  df = df[column_names]
  df = df.rename(columns={'DOI_NAME': 'DOI', 'DOI_SPECIAL': 'ShortName'})
  return df.to_dict('records')


doi_dict_all = getDataFrameFromCSV(csv_all_file)
doi_dict_so = getDataFrameFromCSV_SO(csv_so_file)
doi_dict = doi_dict_all+doi_dict_so

def get_doi_by_shortname(shortName, cmr_sname_dict):
    if cmr_sname_dict.get(shortName, ''):
        return cmr_sname_dict[shortName]
    for sn in cmr_sname_dict.keys():
        if sn == 'NOAA' or sn == 'ACE':
            continue
        if len(sn) <= len(shortName) and len(sn) >= (len(shortName) - 4) and re.match(sn, shortName[:len(sn)]):
            return cmr_sname_dict[sn]
    return None

def get_doi_by_doi1(doi, cmr_doi_dict):
  for doi_dup in cmr_doi_dict.keys():
    if re.match(r'10\.5067',doi_dup) and len(doi) == len(doi_dup) and re.match(doi_dup[:(len(doi_dup)-5)], doi[:(len(doi)-5)], re.IGNORECASE):
      return cmr_doi_dict[doi_dup]
  return None

def get_doi_by_doi2(doi, cmr_doi_dict):
  if re.match(r'\/\d{2}$', doi[-3:]):
    for doi_dup in cmr_doi_dict.keys():
      if re.match(r'10\.5067\/GPM',doi_dup, re.IGNORECASE) and re.match(doi_dup[:(len(doi)-3)], doi[:(len(doi)-3)], re.IGNORECASE):
        return cmr_doi_dict[doi_dup]
  else:
    for doi_dup in cmr_doi_dict.keys():
      if re.match(r'10\.5067\/GPM',doi_dup, re.IGNORECASE) and re.match(doi_dup[:len(doi)], doi, re.IGNORECASE):
        return cmr_doi_dict[doi_dup]
  return None

FORMATS=['ASCII','Binary','HDF-EOS','HDF-EOS2','HDF-EOS4','HDF-EOS5','NetCDF','NetCDF-4','NetCDF-5','HDF','HDF4','HDF5','GeoTIFF','GRIB','PNG','ICARTT','GIF','JPEG', 'Shapefile','Multimedia','Grid']
def get_format(cmr_ft):
  if re.search('GeoTIFF', cmr_ft, re.IGNORECASE):
    return 'GeoTIFF'
  if re.search('GRIB', cmr_ft, re.IGNORECASE):
    return 'GRIB'
  if re.search('PNG', cmr_ft, re.IGNORECASE):
    return 'PNG'
  if re.search('ICARTT', cmr_ft, re.IGNORECASE):
    return 'ICARTT'
  if re.search('HDF-EOS5', cmr_ft, re.IGNORECASE):
    return 'HDF-EOS5'
  if re.search('HDF-EOS4', cmr_ft, re.IGNORECASE):
    return 'HDF-EOS4'
  if re.search('HDF-EOS2', cmr_ft, re.IGNORECASE):
    return 'HDF-EOS2'
  if re.search('EOS', cmr_ft, re.IGNORECASE):
    return 'HDF-EOS'
  if re.search('(HDF5|HDF 5|HDF-5|H5)', cmr_ft, re.IGNORECASE):
    return 'HDF5'
  if re.search('(HDF4|HDF 4|HDF-4)', cmr_ft, re.IGNORECASE):
    return 'HDF4'
  if re.search('HDF', cmr_ft, re.IGNORECASE):
    return 'HDF'
  if re.search('(NetCDF-4|NetCDF 4|NetCDF4)', cmr_ft, re.IGNORECASE):
    return 'NetCDF-4'
  if re.search('(NetCDF-5|NetCDF 5|NetCDF5)', cmr_ft, re.IGNORECASE):
    return 'NetCDF-5'
  if re.search('CDF', cmr_ft, re.IGNORECASE):
    return 'NetCDF'
  if re.search('GIF', cmr_ft, re.IGNORECASE):
    return 'GIF'
  if re.search('JPEG', cmr_ft, re.IGNORECASE):
    return 'JPEG'
  if re.search('Shapefile', cmr_ft, re.IGNORECASE):
    return 'Shapefile'
  if re.search('(AVI|MP4|MOV)', cmr_ft, re.IGNORECASE):
    return 'Multimedia'
  if re.search('(ASCII|TEXT|CSV|TXT|Excel|XML)', cmr_ft, re.IGNORECASE):
    return 'ASCII'
  if re.search('(Binary|BIN|Tape|PDF)', cmr_ft, re.IGNORECASE):
    return 'Binary'
  if re.search('(Geo|ArcGIS|Esri|Grid)', cmr_ft, re.IGNORECASE):
    return 'Grid'

cmr_doi_dict = dict()
cmr_sname_dict = dict()
for cmr_coll in cmr_colls:
  if cmr_coll['DOI']:
    cmr_doi_dict[cmr_coll['DOI'].upper()] = cmr_coll
  cmr_sname_dict[cmr_coll['ShortName'].upper()] = cmr_coll


doi2cmr = dict()

eosdis_doi_cnt = 0
cmr_cnt = 0
cmr_cnt_by_doi = 0
cmr_cnt_by_sn = 0
doi2year = dict()
for entry in doi_dict:
  if not pd.isna(entry['RESOURCE_TYPE']) and (re.match('Text', entry['RESOURCE_TYPE']) or re.match('Documentation', entry['RESOURCE_TYPE'])):
    continue
  doi = entry['DOI'].upper()
  doi2year[doi] = entry['YEAR'][:4]
  eosdis_doi_cnt += 1
  if cmr_doi_dict.get(doi.upper(), ''):
    doi2cmr[doi] = cmr_doi_dict[doi]
    cmr_cnt += 1
    cmr_cnt_by_doi += 1
    continue
  if entry['ShortName']:
      cmr_entry = get_doi_by_shortname(str(entry['ShortName']).upper(), cmr_sname_dict)
      if cmr_entry:
        doi2cmr[doi] = cmr_entry
        #print('ShortName', doi, entry['ShortName'], cmr_entry['ShortName'])
        cmr_cnt += 1
        cmr_cnt_by_sn += 1
        continue

  if re.search('(2014|2018)$',doi):
      cmr_entry = get_doi_by_doi1(doi, cmr_doi_dict)
      if cmr_entry:
        doi2cmr[doi] = cmr_entry
        #print('(2014|2018)', doi, cmr_entry['DOI'])
        cmr_cnt += 1
        continue
  if re.match('10.5067\/GPM\/',doi, re.IGNORECASE): # and re.match('\/\d{2}', doi[-3:]):
      cmr_entry = get_doi_by_doi2(doi, cmr_doi_dict)
      if cmr_entry:
        doi2cmr[doi] = cmr_entry
        #print('10.5067/GPM/', doi, cmr_entry['DOI'])
        cmr_cnt += 1
        continue
  #cmr_entry = get_by_dsl(entry['URL'], cmr_colls)

print('All matched EOSDIS DOIs', eosdis_doi_cnt, cmr_cnt)
print('EOSDIS DOIs matched by CMR DOI only', eosdis_doi_cnt, cmr_cnt_by_doi)
print('EOSDIS DOIs matched by CMR ShortName', eosdis_doi_cnt, cmr_cnt_by_sn)

for doi in doi2cmr_man.keys():
    if re.match('NA', doi2cmr_man[doi]['Concept']):
        continue
    doi2cmr[doi] = doi2cmr_man[doi]
    if cmr_doi_dict.get(doi2cmr_man[doi]['DOI'].upper(), '') and cmr_doi_dict[doi2cmr_man[doi]['DOI'].upper()].get("ScienceKeywords", ''):
        doi2cmr[doi]["ScienceKeywords"] = cmr_doi_dict[doi2cmr_man[doi]['DOI'].upper()]["ScienceKeywords"]
    cmr_cnt += 1

for doi in doi2cmr.keys():
    #print(doi)
    if doi2cmr[doi]['DOI'] and re.search('K7Y2D8QQVZ4L', doi2cmr[doi]['DOI']):
        print(doi, doi2cmr[doi]['DOI'], doi2year[doi])
    if doi2year.get(doi, ''):
        doi2cmr[doi]['Year'] = doi2year[doi]
    elif not doi2cmr[doi].get('Year', ''):
        print('No year', doi)

print(eosdis_doi_cnt, cmr_cnt)

with open("data/doi2cmr.json", "w") as fp:
  json.dump(doi2cmr, fp, indent=4)

exit()

