"""XML utilities."""

###########################################################################
# PYTHON FILE: xmlutils.py
# CREATED BY:  Peter Taylor (November 2002)
#
# Some XML utilities.
#
# $Header$
###########################################################################

# system libraries
import copy
import xml.dom.minidom 

class XMLUtilsError(Exception):
    """Exceptions for XMLUtils operations."""
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return `self.value`

class Document:
    """Data structure with natural correspondence to XML documents.

    At the document level, there is a single Node. A Node in an XML document
    is something defined by one complete set of angled brackets.
    
    Thus a Node has a name (mandatory), text (optional), attributes (optional)
    and a list of child Nodes (optional)."""
    def __init__ (self,
          node=None,
          xmlFile=None,
          xmlString=None,
          dom=None):
        """Constructs the Document from either the field, xmlFile, xmlString
        or existing DOM document.
        
        Construction attempts are in that order."""
        self.xmlFile = xmlFile
        if node is not None:
            self.node = node
        elif xmlFile is not None:
            self._fromXmlFile (xmlFile)
        elif xmlString is not None:
            self._fromXmlString (xmlString)
        elif dom is not None:
            self._fromDom (dom)
        else: self.node = None

    def toxml(self, indent = "", newl = ""):
        """Converts document to an XML string."""
        dom = self._makeDom()
        xml = dom.toprettyxml(indent, newl)
        dom.unlink()
        return xml

    def writexml(self, file=None, indent = "", addIndent = "", newl = ""):
        """Writes document to file in XML format."""
        dom = self._makeDom()
        if file is None:
            file = self.xmlFile
            xml = dom.toprettyxml("\t", "\n")
            fileo = open(file,'w')
            fileo.write(xml)
        else:
            dom.writexml(file, indent, addIndent, newl)
            dom.unlink()

    def _isValid (self):
        if self.node is None:
            return False
        return True
    
    def _makeDom (self ):
        if not self._isValid():
            raise XMLUtilsError,"Invalid Document - cannot be converted to DOM"
        
        dom = xml.dom.minidom.Document()
        dom.appendChild (self.node.makeDomElement (dom))
        return dom
    
    def _fromXmlFile (self, xmlFile):
        dom = xml.dom.minidom.parse(xmlFile)
        self._fromDom (dom)
        dom.unlink()

    def _fromXmlString (self, xmlString):
        dom = xml.dom.minidom.parseString(xmlString)
        self._fromDom (dom)
        dom.unlink()

    def _fromDom (self, dom):
        if dom.nodeType == dom.DOCUMENT_NODE:
            self.node = NodeFromDomElement (dom.documentElement)
        else:
            raise XMLUtilsError, "Must be created from a DOM document node"
    
class Node:
    """Defines a node within an XML document.

    A node has a name, text, attributes and a list of child nodes.

    For example:

    <hello />

    would have name=hello, no text, no attributes and no child nodes.

    For example:

    <hello world="true" />

    would have name=hello, one attribute "world" with the value "true", no text
    and no child nodes. Note that attribute values are always strings.

    For example:

    <sentence>the quick brown fox jumps over a lazy dog</sentence>

    would have name="sentence", text="the quick brown fox jumps over a lazy
    dog", no attributes and no child nodes.

    For example:
    <para><contents>hello world</contents><font>Courier,10</font></para>

    would have name="para", no text, no attributes and two child nodes. The
    child nodes would respectively have name="contents" and text="hello world"
    and name="font" and text="Courier,10".

    Note that you can have child nodes with the same name in the list of child
    nodes - and that is quite normal!

    One major difference between Node and equivalent structures within DOM is
    that we will combine adjacent text objects into a single text values into
    a single text value. With DOM you will often get multiple text values.
    """
    def __init__ (self, name, text=None, attributes=None, childNodes=None):
        """Node constructor.
    
        name is mandatory - represents the name tag with <...>
        text is optional - if None then defaults to an empty string
        attributes is optional - if None then defaults to an empty dictionary
        childNodes is optional - if None then defaults to an empty list
    
        If text, attributes or childNodes are provided, then they are only
        reference copied. Thus changes to the variable in the calling code
        will be reflected within the Node object."""
        self.name = name
        
        if text is None: self.text = ""
        else: self.text = text
    
        if attributes is None: self.attributes = {}
        else: self.attributes = attributes
    
        if childNodes is None: self.childNodes = []
        else: self.childNodes = childNodes

    def __str__ (self):
        """Converts itself to a temporary document, then prints out the XML"""
        dom       = xml.dom.minidom.Document()
        domNode   = self.makeDomElement (dom)
        xmlString = domNode.toprettyxml (indent=" ", newl="\n")
        dom.unlink()
        return xmlString
    
    def append (self,node):
        """Appends a node to the list of child nodes"""
        if isinstance(node, Node):
            self.childNodes.append (node)
        else: 
            raise XMLUtilsError, "Appended value must of type Node"
        
    def makeDomElement(self, dom):
        """Creates a DOM element for a DOM document."""
        domElement = dom.createElement (self.name)
    
        for attrName in self.attributes.keys():
            domElement.setAttribute (attrName, self.attributes[attrName])
    
        if self.text is not None and self.text != "":
            domElement.appendChild (dom.createTextNode(self.text))
            
        for node in self.childNodes:
            domElement.appendChild (node.makeDomElement (dom))
            
        return domElement

    def getAttribute(self, attrName, default=""):
        """Gets an attribute.
    
        Returns the default value (by default="") if the attrName is undefined.
        """
        return self.attributes.get (attrName, default)

    def setAttribute(self, attrName, attrValue):
        """Sets an attribute value - overwriting anything there beforehand."""
        self.attributes[attrName] = attrValue

    def getChildAttributesDQBTimeSeries(self):
        selected , expression, name, id = None, None , None, None
        for n in self.childNodes:
            if n.name =='selected': 
                selected = n.text
                continue
            if n.name =='expression':
                expression = n.text
                continue
            if n.name == 'name':
                name = n.text
                continue
            if n.name == "id":
                id = n.text
                continue
        return selected , expression, name, id
    
def NodeFromDomElement (domNode):
    """Returns a Node from a dom element node which must be an ELEMENT_NODE"""
    if domNode.nodeType != domNode.ELEMENT_NODE:
       raise XMLUtilsError, "DOM node must be an ELEMENT node"

    nodeList   = [] # ordered list of nodes
    textLines  = [] # lines of text - will be joined together to form text
    attributes = {} # node attributes as a dictionary

    if domNode.attributes is not None:
        for i in range(domNode.attributes.length):
            attribute = domNode.attributes.item(i)
            attributes[attribute.nodeName] = attribute.value
    
        textLines = []
        for item in domNode.childNodes:
            if item.nodeType == item.TEXT_NODE:
                textLines.append(item.data)
            elif item.nodeType == item.ELEMENT_NODE:
                subNode = NodeFromDomElement (item)
                nodeList.append (subNode)
    """
    else:
        raise XMLUtilsError, "Child node must be TEXT or ELEMENT node"
    """
    pass # end-for

    text = "".join(textLines).strip()
    
    node = Node (domNode.nodeName, text, attributes, nodeList)
    return node

if __name__ == "__main__":
    import sys
    for name in sys.argv[1:]:
        print "Processing file: %s" % name
        file = open(name, "r")
        doc  = Document(xmlFile = file)
        file.close()
        #print doc.toxml (indent=" ", newl="\n")
