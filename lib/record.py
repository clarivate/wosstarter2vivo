# -*- coding: utf-8 -*-
"""
Read WoS records and map to VIVO.
"""

import os
from rdflib import Namespace, Graph, RDF, Literal, RDFS, XSD
from rdflib.resource import Resource
from time import strptime
from nameparser import HumanName
from namespaces import VIVO, BIBO, FABIO, OBO, VCARD, WOS, D

import logging
logger = logging.getLogger(__name__)


class Record(object):
    """
    Parse the XML returned by the WoS API.
    Convert to VIVO RDF with to_rdf.
    """

    def __init__(self, element):
        self.root = element

    def ut(self):
        return self.root.uid

    def title(self):
        return self.root.title

    def authors(self):
        out = []
        if self.root.names.authors:
            for au in self.root.names.authors:
                out.append(au.display_name)
        return out

    def doi(self):
        return self.root.identifiers.doi

    def venue(self):
        return self.root.source.source_title

    def issue(self):
        return self.root.source.issue

    def volume(self):
        return self.root.source.volume

    def pages(self):
        return self.root.source.pages.range

    def date(self):
        month = self.root.source.publish_month
        year = self.root.source.publish_year
        return month, year

    def issn(self):
        return self.root.identifiers.issn

    def eissn(self):
        return self.root.identifiers.eissn

    def isbn(self):
        return self.root.identifiers.isbn

    """
    VIVO publication from WoS.
    """

    @property
    def localid(self):
        """
        Property used in building URIS.
        """
        return self.ut().replace(':', '-')

    @property
    def pub_uri(self):
        return D['pub-' + self.localid]

    @staticmethod
    def vivo_type():
        """
        For now return all WoS records as AcademicArticles.
        ToDo: add more specific types.
        """
        return BIBO.AcademicArticle

    def vivo_types(self):
        """
        WOS record types, mapped to closest class included in VIVO ontology
        https://webofscience.zendesk.com/hc/en-us/articles/26916283577745-Document-Types
        :return: list
        """
        d = {
            "Article": BIBO.AcademicArticle,
            "Academic Article": BIBO.AcademicArticle,
            "Abstract of Published Item": VIVO.Abstract,
            "Art Exhibit Review": VIVO.Review,
            "Biographical-Item": BIBO.Article,
            "Book": BIBO.Book,
            "Book Chapter": BIBO.Chapter,
            "Book Review": VIVO.Review,
            "Chronology": BIBO.AcadmicArticle,
            "Correction": FABIO.Erratum,
            "Correction, Addition": FABIO.Erratum,
            "Dance Performance Review": VIVO.Review,
            "Database Review": VIVO.Review,
            "Data Set": VIVO.Dataset,
            "Discussion": FABIO.Comment,
            "Early Access": BIBO.AcademicArticle,
            "Editorial Material": FABIO.Comment,
            "English Abstract": VIVO.Abstract,
            "Excerpt": BIBO.Article,
            "Fiction, Creative Prose": BIBO.Article,
            "Film Review": VIVO.Review,
            "Hardware Review": VIVO.Review,
            "Item About An Individual": BIBO.Article,
            "Letter": BIBO.Letter,
            "Meeting Abstract": VIVO.Abstract,
            "Meeting Summary": BIBO.Report,
            "Music Performance Review": VIVO.Review,
            "Music Score": BIBO.AudioDocument,
            "Music Score Review": VIVO.Review,
            "News Item": VIVO.NewsRelease,
            "Note": FABIO.Comment,
            "Poetry": BIBO.Article,
            "Proceedings Paper": BIBO.Proceedings,
            "Record Review": VIVO.Review,
            "Reprint": BIBO.AcadmicArticle,
            "Review": VIVO.Review,
            "Script": BIBO.Book,
            "Software Review": VIVO.Review,
            "TV Review, Radio Review": VIVO.Review,
            "TV Review, Radio Review, Video Review": VIVO.Review,
            "Theater Review": VIVO.Review,
            "Main Cite": BIBO.AcadmicArticle,
            "Item Withdraw": FABIO.Comment,
            "Bibliography": BIBO.AcadmicArticle,
            "Expression of Concern": FABIO.Comment,
            "Meeting": BIBO.Proceedings,
            "Data Paper": BIBO.AcadmicArticle,
            "Retraction": FABIO.Comment,
            "Press Digest": VIVO.NewsRelease
            # VIVO ontology does not account for retractions or withdrawn publications
            # "Withdrawn Publication": WOS.WithdrawnPublication,
            # "Publication With Expression Of Concern": WOS.PubWithExpOfConcern,
            # "Retracted Publication": WOS.RetractedPublication
        }
        dtypes = []
        for wdt in self.root.source_types:
            vtype = d.get(wdt)
            if vtype is None:
                logging.info("Publication type unknown for {}, {}.".format(self.ut, wdt))
            else:
                dtypes.append(vtype)
        if dtypes == []:
            return [BIBO.AcadmicArticle]
        return dtypes

    def wos_vivo_types(self):
        """
        WOS record types
        https://webofscience.zendesk.com/hc/en-us/articles/26916283577745-Document-Types
        :return: list
        """
        d = {
            "Article": WOS.Article,
            "Academic Article": WOS.Article,
            "Abstract of Published Item": WOS.Abstract,
            "Art Exhibit Review": WOS.ArtExhibitReview,
            "Biographical-Item": WOS.BiographicalItem,
            "Book": WOS.Book,
            "Book Chapter": WOS.BookChapter,
            "Book Review": WOS.BookReview,
            "Chronology": WOS.Chronology,
            "Correction": WOS.Correction,
            "Correction, Addition": WOS.CorrectionEdition,
            "Dance Performance Review": WOS.DancePerformanceReview,
            "Database Review": WOS.DatabaseReview,
            "Data Set": WOS.Dataset, # From DRCI
            "Discussion": WOS.Discussion,
            "Early Access": WOS.EarlyAccess,
            "Editorial Material": WOS.EditorialMaterial,
            "English Abstract": WOS.Abstract,
            "Excerpt": WOS.Excerpt,
            "Fiction, Creative Prose": WOS.FictionCreativeProse,
            "Film Review": WOS.FilmReview,
            "Hardware Review": WOS.HardwareReview,
            "Item About An Individual": WOS.ItemAboutAnIndividual,
            "Letter": WOS.Letter,
            "Meeting Abstract": WOS.MeetingAbstract,
            "Meeting Summary": WOS.MeetingSummary,
            "Music Performance Review": WOS.MusicPerformanceReview,
            "Music Score": WOS.MusicScore,
            "Music Score Review": WOS.MusicScoreReview,
            "News Item": WOS.NewsItem,
            "Note": WOS.Note,
            "Poetry": WOS.Poetry,
            "Proceedings Paper": WOS.ProceedingsPaper,
            "Record Review": WOS.RecordReview,
            "Reprint": WOS.Reprint,
            "Review": WOS.Review,
            "Script": WOS.Script,
            "Software Review": WOS.SoftwareReview,
            "TV Review, Radio Review": WOS.TVRadioReview,
            "TV Review, Radio Review, Video Review": WOS.TVRadioVideoReview,
            "Theater Review": WOS.TheaterReview,
            "Main Cite": WOS.MainCite,
            "Item Withdraw": WOS.ItemWithdraw,
            "Withdrawn Publication": WOS.WithdrawnPublication,
            "Bibliography": WOS.Bibliography,
            "Expression of Concern": WOS.ExpOfConcern,
            "Meeting": WOS.Meeting,
            "Publication With Expression Of Concern": WOS.PubWithExpOfConcern,
            "Data Paper": WOS.DataPaper,
            "Retraction": WOS.Retraction,
            "Retracted Publication": WOS.RetractedPublication,
            "Press Digest": WOS.PressDigest
        }
        dtypes = []
        for wdt in self.root.source_types:
            vtype = d.get(wdt)
            if vtype is None:
                logging.info("Publication type unknown for {}, {}.".format(self.ut, wdt))
            else:
                dtypes.append(vtype)
        if dtypes == []:
            return [WOS.Publication]
        return dtypes

    def in_book(self):
        """
        Determine if item is published in a book.
        :return: boolean
        """
        if self.isbn() is not None:
            return True
        else:
            return False

    def pub_date(self):
        """
        Convert WoS date to year and month.
        """
        month, year = self.date()
        if month:
            try:
                month_num = strptime(month.split(" ")[0], "%b").tm_mon
                month_num = f"{month_num:02d}" # change to two digit format
            except (ValueError, AttributeError):
                month_num = None
        else:
            month_num = None
        return year, month, month_num

    def add_date(self):
        """
        Add vivo:DateTimeValue for publication.
        :return: rdflib.Graph
        """
        g = Graph()
        date_uri = D['date-' + self.localid]
        de = Resource(g, date_uri)
        de.set(RDF.type, VIVO.DateTimeValue)
        year, month, month_num = self.pub_date()
        # Add year and month if possible.
        if month_num is not None:
            de.set(RDFS.label, Literal("{}, {}".format(month, year)))
            de.set(
                VIVO.dateTime,
                Literal("{}-{}-01T00:00:00".format(year, month_num), datatype=XSD.dateTime)
            )
            de.set(VIVO.dateTimePrecision, VIVO.yearMonthPrecision)
        else:
            de.set(RDFS.label, Literal(year))
            de.set(
                VIVO.dateTime,
                Literal("{}-01-01T00:00:00".format(year), datatype=XSD.dateTime)
            )
            de.set(VIVO.dateTimePrecision, VIVO.yearPrecision)

        g.add((self.pub_uri, VIVO.dateTimeValue, date_uri))
        return g

    def add_venue(self):
        """
        Add publication venue.
        :return: rdflib.Graph
        """
        g = Graph()

        isbn = self.isbn()
        issn = self.issn() or self.eissn()

        if isbn is not None:
            vtype = BIBO.Book
            uri = D['venue-' + isbn]
        elif issn is not None:
            vtype = BIBO.Journal
            uri = D['venue-' + issn]
        else:
            # Place holder
            logger.info("No source/venue ISSN or ISBN found for {}.".format(self.ut()))
            vtype = BIBO.Journal
            uri = D['venue-' + self.localid]

        venue = Resource(g, uri)
        venue.set(RDF.type, vtype)
        venue.set(RDFS.label, Literal(self.venue()))
        if vtype == BIBO.Journal:
            venue.set(BIBO.issn, Literal(issn))
        else:
            venue.set(BIBO.isbn, Literal(isbn))
        g.add((self.pub_uri, VIVO.hasPublicationVenue, uri))

        return g

    def add_vcard(self, position, name):
        """
        :param position: number in author order
        :param name: name as string - last, first, middle
        :return: rdflib.Graph
        """
        g = Graph()

        # vcard individual
        vci_uri = D['vcard-individual-' + position + '-' + self.localid]
        g.add((vci_uri, RDF.type, VCARD.Individual))

        # vcard name
        vcn_uri = D['vcard-name-' + position + '-' + self.localid]
        g.add((vcn_uri, RDF.type, VCARD.Name))
        g.add((vcn_uri, RDFS.label, Literal(name)))
        # Parse name into first, last, middle
        name = HumanName(name)
        g.add((vcn_uri, VCARD.givenName, Literal(name.first)))
        g.add((vcn_uri, VCARD.familyName, Literal(name.last)))
        if name.middle != "":
            g.add((vcn_uri, VIVO.middleName, Literal(name.middle)))
        # Relate vcard individual to vcard name
        g.add((vci_uri, VCARD.hasName, vcn_uri))
        return vci_uri, g

    def authorship(self):
        """
        Add authorship statements and vcards for authors.
        :return: rdflib.Graph
        """
        g = Graph()
        for num, au in enumerate(self.authors()):
            position = str(num + 1)

            vcard_individual_uri, vcard_stmts = self.add_vcard(position, au)
            g += vcard_stmts

            # Authorship
            aship_uri = D['authorship-' + position + '-' + self.localid]
            g.add((aship_uri, RDF.type, VIVO.Authorship))
            g.add((aship_uri, VIVO.rank, Literal(int(position))))

            # Relate pub and authorship
            g.add((aship_uri, VIVO.relates, self.pub_uri))

            # Relate vcard and authorship
            g.add((aship_uri, VIVO.relates, vcard_individual_uri))

        return g

    def add_vcard_weblink(self):
        """
        Build statements for weblinks in VIVO.
        :return: rdflib.Graph
        """
        base_url = "http://ws.isiknowledge.com/cps/openurl/service?url_ver=Z39.88-2004&rft_id=info:ut/WOS:{}"
        g = Graph()

        # vcard individual for pub
        vci_uri = D['vcard-individual-pub-' + self.localid]
        g.add((vci_uri, RDF.type, VCARD.Individual))

        # vcard URL
        vcu_uri = D['vcard-url-pub-' + self.localid]
        g.add((vcu_uri, RDF.type, VCARD.URL))
        g.add((vcu_uri, RDFS.label, Literal(u"Web of Science™")))
        g.add((vcu_uri, VCARD.url, Literal(base_url.format(self.ut()))))

        # Relate vcard individual to url
        g.add((vci_uri, VCARD.hasURL, vcu_uri))
        return vci_uri, g

    def to_rdf(self):
        """
        Convert the API publication object to VIVO RDF.

        :return: rdflib.Graph
        """
        g = Graph()
        pub = Resource(g, self.pub_uri)
        for type in self.vivo_types():
            pub.add(RDF.type, type)

        # For more precise type mapping, uncomment these lines and load the
        # Web of Science ontology to your VIVO instance
        # for type in self.wos_vivo_types():
        #     pub.add(RDF.type, type)

        pub.set(RDFS.label, Literal(self.title()))
        pub.set(VIVO.identifier, Literal(self.ut()))
        # Map WoS UT to customer property. Used by other Web of Science Group Python tools
        #pub.set(WOS.wosId, Literal(self.ut().replace('WOS:','')))
        # DOI
        doi = self.doi()
        if doi is not None:
            pub.set(BIBO.doi, Literal(doi))
        # Volume
        volume = self.volume()
        if volume is not None:
            pub.set(BIBO.volume, Literal(volume))
        # Issue
        issue = self.issue()
        if issue is not None:
            pub.set(BIBO.issue, Literal(issue))
        # Pages
        pages = self.pages()
        if pages is not None:
            start, end = pages.split('-')
            pub.set(BIBO.start, Literal(start))
            pub.set(BIBO.end, Literal(end))
        # publication venue
        g += self.add_venue()
        # date
        g += self.add_date()

        # authorship and vcards
        g += self.authorship()

        # links
        web_link, linkg = self.add_vcard_weblink()
        g += linkg
        # relate web link and publication
        g.add((self.pub_uri, OBO['ARG_2000028'], web_link))

        return g

    def to_nt(self):
        g = self.to_rdf()
        return g.serialize(format='nt')
