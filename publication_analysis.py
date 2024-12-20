import os
import json
import re
import glob
import csv
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import requests

pubs_file = "pubs_all.json"
json_folder_path = 'data'

with open(os.path.join(json_folder_path, pubs_file)) as json_publications_file:
  pubs = json.load(json_publications_file)

dois = dict()
daacs = dict()
plevels = dict()
formats = dict()
snames = dict()
cocit_cnt = dict()
codaac_cnt = dict()
colevel_cnt = dict()
cofrmt_cnt = dict()
cosn_cnt = dict()

for pub in pubs:
    #print(pub['title'])
    if pub.get('DAACs', ''):
        if codaac_cnt.get(len(pub['DAACs']), ''):
            codaac_cnt[len(pub['DAACs'])] += 1
        else:
            codaac_cnt[len(pub['DAACs'])] = 1
        #if len(pub['DAACs']) == 5:
        #    print(pub['doi'])
        for daac1 in pub['DAACs']:
            for daac2 in pub['DAACs']:
                if daacs.get(daac1, ''):
                    if daacs[daac1].get(daac2, ''):
                        daacs[daac1][daac2] += 1
                    else:
                        daacs[daac1][daac2] = 1
                else:
                    daacs[daac1] = { daac2: 1 }
    if pub.get('ShortNames', ''):
        if cosn_cnt.get(len(pub['ShortNames']), ''):
            cosn_cnt[len(pub['ShortNames'])] += 1
        else:
            cosn_cnt[len(pub['ShortNames'])] = 1
        for sn1 in pub['ShortNames']:
            for sn2 in pub['ShortNames']:
                if snames.get(sn1, ''):
                    if snames[sn1].get(sn2, ''):
                        snames[sn1][sn2] += 1
                    else:
                        snames[sn1][sn2] = 1
                else:
                    snames[sn1] = { sn2: 1 }
    if pub.get('DOIs', ''):
        for doi in pub['DOIs']:
            dois[doi] = 1
        if cocit_cnt.get(len(pub['DOIs']), ''):
            cocit_cnt[len(pub['DOIs'])] += 1
        else:
            cocit_cnt[len(pub['DOIs'])] = 1
        if len(pub['Levels']) and colevel_cnt.get(len(pub['Levels']), ''):
            colevel_cnt[len(pub['Levels'])] += 1
        else:
            colevel_cnt[len(pub['Levels'])] = 1
        if len(pub['Formats']) and cofrmt_cnt.get(len(pub['Formats']), ''):
            cofrmt_cnt[len(pub['Formats'])] += 1
        else:
            cofrmt_cnt[len(pub['Formats'])] = 1
        for pl1 in pub['Levels']:
            for pl2 in pub['Levels']:
                if plevels.get(pl1, ''):
                    if plevels[pl1].get(pl2, ''):
                        plevels[pl1][pl2] += 1
                    else:
                        plevels[pl1][pl2] = 1
                else:
                    plevels[pl1] = { pl2: 1 }
        for fm1 in pub['Formats']:
            for fm2 in pub['Formats']:
                if formats.get(fm1, ''):
                    if formats[fm1].get(fm2, ''):
                        formats[fm1][fm2] += 1
                    else:
                        formats[fm1][fm2] = 1
                else:
                    formats[fm1] = { fm2: 1 }
        #nmlzd_fmts = ['ASCII','Binary','HDF-EOS','HDF-EOS2','HDF-EOS4','HDF-EOS5','HDF','HDF4','HDF5','GeoTIFF','GRIB','PNG','GIF','ICARTT',

print('Total pubs', len(pubs))
print('Total dataset DOI count in publications',len(dois.keys()))
print('Co-citations',cocit_cnt)
print('Co-DAACs',codaac_cnt)
print('Co-levels',colevel_cnt)
print('Co-formats',cofrmt_cnt)
print('Co-ShortNames',cosn_cnt)

#print(plevels)
#print(formats)


exit()

DAACs = ['PO.DAAC','NSIDC DAAC','LP DAAC', 'ASDC DAAC', 'ORNL DAAC', 'SEDAC', 'GES DISC', 'LAADS', 'OB.DAAC', 'GHRC DAAC', 'ASF DAAC']
df = pd.DataFrame(columns = DAACs, index = DAACs)

for rowIndex, row in df.iterrows(): #iterate over rows
    flag = False
    for columnIndex, value in row.items():
        if daacs.get(rowIndex) and daacs[rowIndex].get(columnIndex):
            df.at[rowIndex,columnIndex] = daacs[rowIndex][columnIndex]
        if rowIndex == columnIndex:
            flag = True
df = df.astype(float)
plt.figure(figsize = (10,10))
ax=sns.heatmap(df, annot=True, fmt='g', vmin=0, vmax=200, cbar=False, cmap="Blues")
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()
plt.xticks(rotation=90)
plt.savefig('myfig_daacs.png')
plt.figure().clear()


PLEVELS=['0','1','1A','1B','1T','2','2A','2B','2G','2P','3','4'] #,'NA']
df = pd.DataFrame(columns = PLEVELS, index = PLEVELS)

for rowIndex, row in df.iterrows(): #iterate over rows
    flag = False
    for columnIndex, value in row.items():
        if plevels.get(rowIndex) and plevels[rowIndex].get(columnIndex):
            df.at[rowIndex,columnIndex] = plevels[rowIndex][columnIndex]
        if rowIndex == columnIndex:
            flag = True

df = df.astype(float)
plt.figure(figsize = (10,10))
ax=sns.heatmap(df, annot=True, fmt='g', vmin=0, vmax=200, cbar=False, cmap="Blues")  #cmap="Reds"
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()
plt.xticks(rotation=90)
plt.savefig('myfig_pl.png')
plt.figure().clear()

#exit()

FORMATS=['ASCII','Binary','HDF-EOS','HDF-EOS2','HDF-EOS5','NetCDF','NetCDF-4','NetCDF-5','HDF','HDF4','HDF5','GeoTIFF','GRIB','PNG','ICARTT','JPEG', 'Shapefile','Grid']
#FORMATS=['ASCII','Binary','HDF-EOS','HDF-EOS2','NetCDF','NetCDF-3','NetCDF-4','HDF-EOS5','HDF','HDF4','HDF5','GeoTIFF','GRIB','PNG','ICARTT']
df = pd.DataFrame(columns = FORMATS, index = FORMATS)

for rowIndex, row in df.iterrows(): #iterate over rows
    flag = False
    for columnIndex, value in row.items():
        if formats.get(rowIndex) and formats[rowIndex].get(columnIndex):
            df.at[rowIndex,columnIndex] = formats[rowIndex][columnIndex]
        if rowIndex == columnIndex:
            flag = True

df = df.astype(float)
plt.figure(figsize = (10,10))
ax=sns.heatmap(df, annot=True, fmt='g', vmin=0, vmax=200, cbar=False, cmap="Blues")  #cmap="Reds"
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()
plt.xticks(rotation=90)
plt.savefig('myfig_f.png')
plt.figure().clear()


