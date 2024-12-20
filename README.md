# Publication Analysis
Publication Analysis

## Description
This code is used to analyze dataset co-citation patterns in the NASA Earth science dataset-citing publications. 

Publication citations are maintained in Zotero: https://www.zotero.org/groups/4567966/eosdis_dci/library, which is updated a few times a year. 
The citations in this library are linked to dataset DOIs whose prefixes are 10.5067, 10.3334, or 10.7927. 
Our repository utilizes Zotero Python library PyZotero to retrieve citations from Zotero.

The corresponding CMR records by quering CMR via API for all its collections and retaining only collections that have DOIs with prefixes 10.5067, 10.3334, or 10.7927.

Once we have records from Zotero and CMR, we match the records by DOI and dataset ShortName, when possible. 

Combined repository of dataset DOIs and matching CMR records is analized for dataset DOI co-citatons, dataset archiver (DAAC) co-citation, and cocitation of dataset formats and processing levels.

## The code is executed as follows:

### Obtain publication citations and their tags from Zotero

To execute this code, use Zotero library ID, 4567966, and API token that can be obtained by establishing account at https://zotero.org
Script needs data/zotero_credentials.json which should contain:
```
{
        "library_id" : "4567966",
        "library_type" : "group",
        "api_key" : _Your Zotero API token_
}
``` 
the script outputs data/zot_pubs_all.json - a dump of publication sitations with citation metadata and tags 
```
python get_zotero_pubs_and_tags.py
```

### Reformat Zotero output in more consise form for future analysis
```
create_publications_profile.py
```

### Obtain CMR records matching any of these dataset DOIs: 10.5067, 10.3334, or 10.7927

Search CMR via its API (https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html#umm-json) for Collections whose prefixes are 10.5067, 10.3334, or 10.7927.
Store results in data/cmr_collections.json
```
python search_cmr_collections.py
```

### Match dataset DOIs to CMR collections
Output is stored in data/doi2cmr.json

```
python match_doi2cmr.py
```

### Perform publication analysis
Takes data/pubs_all.json as input and outputs results for DOI, DAAC, Format, and Level dataset co-citations 

```
python publication_analysis.py
```


