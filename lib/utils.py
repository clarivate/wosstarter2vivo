from rdflib import Graph
from datetime import datetime
import os
from namespaces import ns_mgr

import logging
logger = logging.getLogger('backend')

def write_out(content, prefix='rdf-'):
    timestamp = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    path = os.path.normpath(prefix + "-" + timestamp + "-in.ttl")
    logger.info(path)
    try:
        with open(path, "w") as f:
            f.write(content)
            logger.info('Wrote RDF to ' + path)
    except IOError:
        # Handle the error.
        logger.error("Failed to write RDF file. "
              "Does a directory named 'data' exist?")
        logger.warning("The following RDF was not saved: \n" +
             content)
    except Exception as e:
        logger.error("Failed to write RDF file. ")
        logger.warning("The following RDF was not saved: \n" +
             content)
        logger.error(e)


def srlz(g, format="turtle"):
    ng = Graph()
    ng.namespace_manager = ns_mgr
    ng += g
    return(ng.serialize(format=format))