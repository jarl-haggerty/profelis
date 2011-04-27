"""
Copyright 2010 Jarl Haggerty

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
       
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from org.xml.sax.helpers import XMLReaderFactory
from org.xml.sax import XMLReader
from org.xml.sax import InputSource
from org.xml.sax.helpers import DefaultHandler
from org.xml.sax import SAXException
from java.lang import ClassLoader
from org.xml.sax import InputSource

xmlDictionary = {"&" : "&amp;",
                 "\"" : "&quot;"}

def handleXMLCharacters(input):
    result = ""
    for q in input:
        result += xmlDictionary[q] if q in xmlDictionary else q
    return result

class GeneDeleter(DefaultHandler):
    """
    A SAX handler for Deleting Genes.
    """
    def __init__(self, starts, output):
        self.output = output
        self.starts = starts
        self.text = []
        self.iterationQueryDef = True
        self.iterationQueryDefString = ""
        self.holding = False
        self.printing = True

    def startDocument(self):
        self.output.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")

    def startElement(self, uri, tag, name, attributes):
        if tag == "Iteration":
            self.holding = True
        self.iterationQueryDef = tag == "Iteration_query-def"
        self.iterationQueryDefString = ""
            
        if self.printing:
            if self.holding:
                self.text += "<" + tag + ">"
            else:
                self.output.write("<" + tag + ">")
    
    def endElement(self, uri, tag, name):
        if self.iterationQueryDef:
            self.iterationQueryDef = False
            if not int(self.iterationQueryDefString[self.iterationQueryDefString.rfind(":")+1:self.iterationQueryDefString.rfind("-")]) in self.starts:
                self.printing = True
                self.holding = False
                self.output.write("".join(self.text))
                self.text = []
            else:
                self.printing = False
                self.holding = False
                self.text = []
              
        if self.printing:
            if self.holding:
                self.text += "</" + tag + ">"
            else:
                self.output.write("</" + tag + ">")

        if tag == "Iteration":
            self.holding = False
            self.printing = True

    def endDocument(self):
        self.output.write("\n")
        self.output.close()

    def characters(self, raw, start, length):
        if self.iterationQueryDef:
            self.iterationQueryDefString += raw[start:start+length].tostring()
        if self.printing:
            if self.holding:
                self.text += handleXMLCharacters(raw[start:start+length].tostring())
            else:
                self.output.write(handleXMLCharacters(raw[start:start+length].tostring()))

class BreakParsingException(Exception):
    pass

class GeneWriter(DefaultHandler):
    def __init__(self, output):
        self.output = output
        self.writing = False

    def startElement(self, uri, tag, name, attributes):
        if tag == "Iteration":
            self.writing = True
        if self.writing:
            self.output.write("<" + tag + ">")

    def endElement(self, uri, tag, name):
        if tag == "BlastOutput_iterations":
            self.output.write("  ")
            raise BreakParsingException()
        if self.writing:
            self.output.write("</" + tag + ">")

    def characters(self, raw, start, length):
        print handleXMLCharacters(raw[start:start+length].tostring())
        if self.writing:
            self.output.write(handleXMLCharacters(raw[start:start+length].tostring()))

    def resolveEntity(self, publicId, systemId):
        return InputSource(ClassLoader.getSystemResourceAsStream("dtds/" + os.path.split(systemId)[1]))

    def ignorableWhitespace(self, raw, start, length):
        print handleXMLCharacters(raw[start:start+length].tostring())
        if self.writing:
            self.output.write(handleXMLCharacters(raw[start:start+length].tostring()))

class GeneAdder(DefaultHandler):
    def __init__(self, source, output):
        self.source = source
        self.output = output
        self.added = False

    def startDocument(self):
        self.output = open(self.output, "w")
        self.output.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")

    def endDocument(self):
        self.output.close()

    def startElement(self, uri, tag, name, attributes):
        if tag == "Iteration" and not self.added:
            self.added = True
            reader = XMLReaderFactory.createXMLReader()
            reader.entityResolver = reader.contentHandler = GeneWriter(self.output)
            try:
                reader.parse(self.source)
            except BreakParsingException:
                print "Hello"
        self.output.write("<" + tag + ">")
        
    def endElement(self, uri, tag, name):
        self.output.write("</" + tag + ">")

    def characters(self, raw, start, length):
        self.output.write(handleXMLCharacters(raw[start:start+length].tostring()))

def deleteGenes(fileName, geneStarts):
    reader = XMLReaderFactory.createXMLReader()
    reader.contentHandler = GeneDeleter(geneStarts, "profelis.temp.blastp.xml")
    reader.parse(fileName)
    os.remove(fileName)
    os.rename("profelis.temp.blastp.xml", fileName)

def addGenes(fileName, source):
    reader = XMLReaderFactory.createXMLReader()
    reader.contentHandler = GeneAdder(source, "profelis.temp.blastp.xml")
    reader.parse(fileName)
    os.remove(fileName)
    os.rename("profelis.temp.blastp.xml", fileName)
