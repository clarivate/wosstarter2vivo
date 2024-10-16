import os

#Namespaces
from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager, ClosedNamespace, RDF
from rdflib import RDFS, OWL, XSD

#setup namespaces
#code inspired by / borrowed from https://github.com/libris/librislod
#local data namespace
D = Namespace(os.environ['DATA_NAMESPACE'])

VIVO = Namespace('http://vivoweb.org/ontology/core#')
VITROPUBLIC = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/public#')
VITRO = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/0.7#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
BIBO = Namespace('http://purl.org/ontology/bibo/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')
OBO = Namespace('http://purl.obolibrary.org/obo/')
WOS = Namespace("http://webofscience.com/ontology/wos#")
SCHEMA = Namespace("http://schema.org/")
OCRE = Namespace("http://purl.org/net/OCRe/OCRe.owl#")
WGS84 = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
FABIO = Namespace("http://purl.org/spar/fabio/")

#tmp graph for in memory graphs
TMP = Namespace('http://localhost/tmp#')

namespaces = {}
for k, o in list(vars().items()):
    if isinstance(o, (Namespace, ClosedNamespace)):
        namespaces[k] = o

ns_mgr = NamespaceManager(Graph())
for k, v in namespaces.items():
    ns_mgr.bind(k.lower(), v)

rq_prefixes = u"\n".join("prefix %s: <%s>" % (k.lower(), v)
                         for k, v in namespaces.items())

prefixes = u"\n    ".join("%s: %s" % (k.lower(), v)
                          for k, v in namespaces.items()
                          if k not in u'RDF RDFS OWL XSD')
#namespace setup complete
