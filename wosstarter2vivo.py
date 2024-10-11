#! /usr/bin/env python
"""
Command line tool for searching the WoS for publications and mapping
to VIVO.

$ python wosstarter2vivo.py

"""

import os
from lib.record import Record
import lib.utils as utils
from rdflib import Graph, Literal, URIRef
from rdflib.resource import Resource
import clarivate.wos_starter.client as client
from clarivate.wos_starter.client.rest import ApiException

import logging
logging.basicConfig(level=logging.INFO)

configuration = client.Configuration()
configuration.api_key['ClarivateApiKeyAuth'] = os.environ["API_KEY"]

def harvest_wos():
    with client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = client.DocumentsApi(api_client)
        q = '(OG=(University of Colorado Boulder)) AND PY=(2024) AND TS=cancer' # str | Web of Science advanced [advanced search query builder](https://webofscience.help.clarivate.com/en-us/Content/advanced-search.html). The supported field tags are listed in description.
        db = 'WOS' # str | Web of Science Database abbreviation * WOS - Web of Science Core collection * BIOABS - Biological Abstracts * BCI - BIOSIS Citation Index * BIOSIS - BIOSIS Previews * CCC - Current Contents Connect * DIIDW - Derwent Innovations Index * DRCI - Data Citation Index * MEDLINE - MEDLINE The U.S. National Library of Medicine® (NLM®) premier life sciences database. * ZOOREC - Zoological Records * PPRN - Preprint Citation Index * WOK - All databases  (optional) (default to 'WOS')
        limit = 50 # int | set the limit of records on the page (1-50) (optional) (default to 10)
        page = 1 # int | set the result page (optional) (default to 1)
        sort_field = 'LD+D' # str | Order by field(s). Field name and order by clause separated by '+', use A for ASC and D for DESC, ex: PY+D. Multiple values are separated by comma. Supported fields:  * **LD** - Load Date * **PY** - Publication Year * **RS** - Relevance * **TC** - Times Cited  (optional)
        modified_time_span = None # str | Defines a date range in which the results were most recently modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)
        tc_modified_time_span = None # str | Defines a date range in which times cited counts were modified. Beginning and end dates must be specified in the yyyy-mm-dd format separated by '+' or ' ', e.g. 2023-01-01+2023-12-31. This parameter is not compatible with the all databases search, i.e. db=WOK is not compatible with this parameter. (optional)

        numResults=page*limit
        g = Graph()

        while page*limit-limit < numResults:
            try:
                # Query Web of Science documents 
                r = api_instance.documents_get(q, db=db, limit=limit, page=page, sort_field=sort_field, modified_time_span=modified_time_span, tc_modified_time_span=tc_modified_time_span)
                numResults = r.metadata.total
                logging.info("Page {} of {}".format(page, numResults//limit+1))

                for doc in r.hits:
                    rec = Record(doc)
                    logging.debug("Processing {}".format(doc.uid))
                    g += rec.to_rdf()

                page+=1

            except ApiException as e:
                logging.debug("Params: {}, {}, {}, {}, {}, {}, {}".format(q, db, limit, page, sort_field, modified_time_span, tc_modified_time_span))
                logging.error("Exception when calling DocumentsApi->documents_get: %s\n" % e)
                break

        utils.write_out(utils.srlz(g, format="turtle"), "test")

if __name__ == "__main__":
    harvest_wos()