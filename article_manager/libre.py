# coding=UTF-8

from dokuwiki.parsers import Parser, LineParser
from dokuwiki.elements import LineElement
from dokuwiki.dokuwikixmlrpc import DokuWikiClient 
from dokuwiki.html import HTMLParser

from article_manager.translit import cir_lat_map
from article_manager.translit import cir_to_lat
from article_manager.translit import check_cyr 

import re

class LibreTextParser(Parser): 
        def onDocumentStart(self): 
                self.libre_title = ""
                self.libre_author = ""
                self.libre_status = "U_PRIPREMI"
                self.contents = ""
        def onHeading(self, level, text):
                if level == 6: 
                        self.libre_title = text.strip()
        def onText(self, text):
                
                # do some libre-specific stuff 
                if text.strip() in ["U_PRIPREMI", "ORIGINAL", "PRIHVACEN", "LEKTORISAN", "PROVEREN"]:
                        self.libre_status = text.strip()
                        return 
                m = re.compile(r"(Autor|autor|autori|Autori|Аутор):? *(.*)") # check for author matching 
                match = m.match(cir_to_lat(text)) 
                if match: 
                        self.libre_author = match.group(2)
                        return  
                self.contents += text + "\n" # if text is not match from above, add it to contents 

class LibreText(object): 
        
        def __init__(self, text, source = ""): 
                
                self.id = source

                parser = LibreTextParser() 
                blocks = text.split("\n")
                for line in blocks: 
                    parser.parse(line) 
                parser.finish()
                self.title = parser.libre_title 
                self.author = parser.libre_author 
                self.status = parser.libre_status
                contents = parser.contents

                html_parser = HTMLParser() 
                contents_blocks = contents.split("\n")
                for line in contents_blocks: 
                    html_parser.parse(line)
                html_parser.finish()
                self.html = html_parser.output
                self.text = text 

        def isChecked(self): 
                """
                Checks whether text has a status PROVEREN 
                """
                return self.status == "PROVEREN"
        
        def isCyr(self): 
                """
                Returns True if text is written in cyrilic script, False otherwise. 

                NOTE: This method will check if 40% of characters is in cyrilic text
                """
                return check_cyr(self.text)

        def getId(self): 
                return self.id

        def getTitle(self): 
                """
                Returns text title
                """
                return cir_to_lat(self.title)
        
        def getText(self): 
                """
                Returns text
                """
                return self.text 
        
        def getLatText(self): 
                """
                Returns text forcing latin script
                """
                return cir_to_lat(self.text)

        def getAuthor(self): 
                """
                Returns author information
                """
                return cir_to_lat(self.author)
        def getStatusString(self): 
                """
                Returns status as a string representation
                """
                return self.status 
        def getHTML(self): 
                """
                Returns HTML of a text
                """
                return self.html

        def getLatHTML(self):
            """
            Returns HTML of article but forces latin text 
            """
            return cir_to_lat(self.html)


class LibreManager(object): 
        
        def __init__(self, username, password): 
                self.remote = DokuWikiClient("https://libre.lugons.org/wiki", username, password)

        def getPage(self, page): 
                """
                Returns specified page id as a LibreText object

                NOTE: page should be with namespace
                """
                # try without namespace
                l = LibreText(self.remote.page(page), page)
                if l.getTitle() == "":
                        l = LibreText(self.remote.page("wiki:" + page), "wiki:" + page) # try with namespace 
                return l
        
        def getLocalLinks(self, source):
                """
                Returns a list of all available links (local page ids) as strings

                Example: ["wiki:page_a", "page_b", "namespace1:page_c"]
                """
                res = []
                links = self.remote.links(source) 
                for link in links:
                        if link["type"] == "local": 
                                #print link["page"]
                                #print "getting page " + link["page"]
                                #print "Title: " + libretext.getTitle() 
                                #print
                                #print "Title: " + libretext.getTitle()
                                res.append(link["page"])
                return res

        def getAllLinked(self, source): 
                """
                Returns a list of LibreText objects which are all pages linked from specified page
                """
                res = []
                links = self.getLocalLinks(source)
                for link in links:
                        libretext = self.getPage(link)
                        res.append(libretext)
                return res


