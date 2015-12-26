#!/usr/bin/env python

#
# Generated Mon Feb 25 14:31:39 2008 by generateDS.py.
#

import sys
import getopt
from xml.dom import minidom
from xml.dom import Node

#
# If you have installed IPython you can uncomment and use the following.
# IPython is available from http://ipython.scipy.org/.
#

## from IPython.Shell import IPShellEmbed
## args = ''
## ipshell = IPShellEmbed(args,
##     banner = 'Dropping into IPython',
##     exit_msg = 'Leaving Interpreter, back to program.')

# Then use the following line where and when you want to drop into the
# IPython shell:
#    ipshell('<some message> -- Entering ipshell.\nHit Ctrl-D to exit')

#
# Support/utility functions.
#

def showIndent(outfile, level):
    for idx in range(level):
        outfile.write('    ')

def quote_xml(inStr):
    s1 = inStr
    s1 = s1.replace('&', '&amp;')
    s1 = s1.replace('<', '&lt;')
    s1 = s1.replace('"', '&quot;')
    return s1

def quote_python(inStr):
    s1 = inStr
    if s1.find("'") == -1:
        if s1.find('\n') == -1:
            return "'%s'" % s1
        else:
            return "'''%s'''" % s1
    else:
        if s1.find('"') != -1:
            s1 = s1.replace('"', '\\"')
        if s1.find('\n') == -1:
            return '"%s"' % s1
        else:
            return '"""%s"""' % s1


class MixedContainer:
    # Constants for category:
    CategoryNone = 0
    CategoryText = 1
    CategorySimple = 2
    CategoryComplex = 3
    # Constants for content_type:
    TypeNone = 0
    TypeText = 1
    TypeString = 2
    TypeInteger = 3
    TypeFloat = 4
    TypeDecimal = 5
    TypeDouble = 6
    TypeBoolean = 7
    def __init__(self, category, content_type, name, value):
        self.category = category
        self.content_type = content_type
        self.name = name
        self.value = value
    def getCategory(self):
        return self.category
    def getContenttype(self, content_type):
        return self.content_type
    def getValue(self):
        return self.value
    def getName(self):
        return self.name
    def export(self, outfile, level, name):
        if self.category == MixedContainer.CategoryText:
            outfile.write(self.value)
        elif self.category == MixedContainer.CategorySimple:
            self.exportSimple(outfile, level, name)
        else:    # category == MixedContainer.CategoryComplex
            self.value.export(outfile, level, name)
    def exportSimple(self, outfile, level, name):
        if self.content_type == MixedContainer.TypeString:
            outfile.write('<%s>%s</%s>' % (self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeInteger or \
                self.content_type == MixedContainer.TypeBoolean:
            outfile.write('<%s>%d</%s>' % (self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeFloat or \
                self.content_type == MixedContainer.TypeDecimal:
            outfile.write('<%s>%f</%s>' % (self.name, self.value, self.name))
        elif self.content_type == MixedContainer.TypeDouble:
            outfile.write('<%s>%g</%s>' % (self.name, self.value, self.name))
    def exportLiteral(self, outfile, level, name):
        if self.category == MixedContainer.CategoryText:
            showIndent(outfile, level)
            outfile.write('MixedContainer(%d, %d, "%s", "%s"),\n' % \
                (self.category, self.content_type, self.name, self.value))
        elif self.category == MixedContainer.CategorySimple:
            showIndent(outfile, level)
            outfile.write('MixedContainer(%d, %d, "%s", "%s"),\n' % \
                (self.category, self.content_type, self.name, self.value))
        else:    # category == MixedContainer.CategoryComplex
            showIndent(outfile, level)
            outfile.write('MixedContainer(%d, %d, "%s",\n' % \
                (self.category, self.content_type, self.name,))
            self.value.exportLiteral(outfile, level + 1)
            showIndent(outfile, level)
            outfile.write(')\n')


class _MemberSpec(object):
    def __init__(self, name='', data_type='', container=0):
        self.name = name
        self.data_type = data_type
        self.container = container
    def set_name(self, name): self.name = name
    def get_name(self): return self.name
    def set_data_type(self, data_type): self.data_type = data_type
    def get_data_type(self): return self.data_type
    def set_container(self, container): self.container = container
    def get_container(self): return self.container


#
# Data representation classes.
#

class invoke:
    subclass = None
    def __init__(self, returntype=None, name=None, arguments=None):
        self.returntype = returntype
        self.name = name
        self.arguments = arguments
    def factory(*args_, **kwargs_):
        if invoke.subclass:
            return invoke.subclass(*args_, **kwargs_)
        else:
            return invoke(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_arguments(self): return self.arguments
    def set_arguments(self, arguments): self.arguments = arguments
    def get_returntype(self): return self.returntype
    def set_returntype(self, returntype): self.returntype = returntype
    def get_name(self): return self.name
    def set_name(self, name): self.name = name
    def export(self, outfile, level, name_='invoke'):
        showIndent(outfile, level)
        outfile.write('<%s' % (name_, ))
        self.exportAttributes(outfile, level, name_='invoke')
        outfile.write('>\n')
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write('</%s>\n' % name_)
    def exportAttributes(self, outfile, level, name_='invoke'):
        outfile.write(' returntype="%s"' % (self.get_returntype(), ))
        outfile.write(' name="%s"' % (self.get_name(), ))
    def exportChildren(self, outfile, level, name_='invoke'):
        if self.arguments:
            self.arguments.export(outfile, level)
    def exportLiteral(self, outfile, level, name_='invoke'):
        level += 1
        self.exportLiteralAttributes(outfile, level, name_)
        self.exportLiteralChildren(outfile, level, name_)
    def exportLiteralAttributes(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('returntype = "%s",\n' % (self.get_returntype(),))
        showIndent(outfile, level)
        outfile.write('name = "%s",\n' % (self.get_name(),))
    def exportLiteralChildren(self, outfile, level, name_):
        if self.arguments:
            showIndent(outfile, level)
            outfile.write('arguments=arguments(\n')
            self.arguments.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        if attrs.get('returntype'):
            self.returntype = attrs.get('returntype').value
        if attrs.get('name'):
            self.name = attrs.get('name').value
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'arguments':
            obj_ = arguments.factory()
            obj_.build(child_)
            self.set_arguments(obj_)
# end class invoke


class arguments:
    subclass = None
    def __init__(self, string='', array=None):
        self.string = string
        self.array = array
    def factory(*args_, **kwargs_):
        if arguments.subclass:
            return arguments.subclass(*args_, **kwargs_)
        else:
            return arguments(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_string(self): return self.string
    def set_string(self, string): self.string = string
    def get_array(self): return self.array
    def set_array(self, array): self.array = array
    def export(self, outfile, level, name_='arguments'):
        showIndent(outfile, level)
        outfile.write('<%s>\n' % name_)
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write('</%s>\n' % name_)
    def exportAttributes(self, outfile, level, name_='arguments'):
        pass
    def exportChildren(self, outfile, level, name_='arguments'):
        showIndent(outfile, level)
        outfile.write('<string>%s</string>\n' % quote_xml(self.get_string()))
        if self.array:
            self.array.export(outfile, level)
    def exportLiteral(self, outfile, level, name_='arguments'):
        level += 1
        self.exportLiteralAttributes(outfile, level, name_)
        self.exportLiteralChildren(outfile, level, name_)
    def exportLiteralAttributes(self, outfile, level, name_):
        pass
    def exportLiteralChildren(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('string=%s,\n' % quote_python(self.get_string()))
        if self.array:
            showIndent(outfile, level)
            outfile.write('array=array(\n')
            self.array.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        pass
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'string':
            string_ = ''
            for text__content_ in child_.childNodes:
                string_ += text__content_.nodeValue
            self.string = string_
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'array':
            obj_ = array.factory()
            obj_.build(child_)
            self.set_array(obj_)
# end class arguments


class array:
    subclass = None
    def __init__(self, property=None):
        if property is None:
            self.property = []
        else:
            self.property = property
    def factory(*args_, **kwargs_):
        if array.subclass:
            return array.subclass(*args_, **kwargs_)
        else:
            return array(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_property(self): return self.property
    def set_property(self, property): self.property = property
    def add_property(self, value): self.property.append(value)
    def insert_property(self, index, value): self.property[index] = value
    def export(self, outfile, level, name_='array'):
        showIndent(outfile, level)
        outfile.write('<%s>\n' % name_)
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write('</%s>\n' % name_)
    def exportAttributes(self, outfile, level, name_='array'):
        pass
    def exportChildren(self, outfile, level, name_='array'):
        for property_ in self.get_property():
            property_.export(outfile, level)
    def exportLiteral(self, outfile, level, name_='array'):
        level += 1
        self.exportLiteralAttributes(outfile, level, name_)
        self.exportLiteralChildren(outfile, level, name_)
    def exportLiteralAttributes(self, outfile, level, name_):
        pass
    def exportLiteralChildren(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('property=[\n')
        level += 1
        for property in self.property:
            showIndent(outfile, level)
            outfile.write('property(\n')
            property.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        pass
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'property':
            obj_ = property.factory()
            obj_.build(child_)
            self.property.append(obj_)
# end class array


class property:
    subclass = None
    def __init__(self, id=None, object=None, string=''):
        self.id = id
        self.object = object
        self.string = string
    def factory(*args_, **kwargs_):
        if property.subclass:
            return property.subclass(*args_, **kwargs_)
        else:
            return property(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_object(self): return self.object
    def set_object(self, object): self.object = object
    def get_string(self): return self.string
    def set_string(self, string): self.string = string
    def get_id(self): return self.id
    def set_id(self, id): self.id = id
    def export(self, outfile, level, name_='property'):
        showIndent(outfile, level)
        outfile.write('<%s' % (name_, ))
        self.exportAttributes(outfile, level, name_='property')
        outfile.write('>\n')
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write('</%s>\n' % name_)
    def exportAttributes(self, outfile, level, name_='property'):
        outfile.write(' id="%s"' % (self.get_id(), ))
    def exportChildren(self, outfile, level, name_='property'):
        if self.get_object() != None :
            if self.object:
                self.object.export(outfile, level)
        if self.get_string() != None :
            showIndent(outfile, level)
            outfile.write('<string>%s</string>\n' % quote_xml(self.get_string()))
    def exportLiteral(self, outfile, level, name_='property'):
        level += 1
        self.exportLiteralAttributes(outfile, level, name_)
        self.exportLiteralChildren(outfile, level, name_)
    def exportLiteralAttributes(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('id = "%s",\n' % (self.get_id(),))
    def exportLiteralChildren(self, outfile, level, name_):
        if self.object:
            showIndent(outfile, level)
            outfile.write('object=object(\n')
            self.object.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        showIndent(outfile, level)
        outfile.write('string=%s,\n' % quote_python(self.get_string()))
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        if attrs.get('id'):
            self.id = attrs.get('id').value
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'object':
            obj_ = object.factory()
            obj_.build(child_)
            self.set_object(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'string':
            string_ = ''
            for text__content_ in child_.childNodes:
                string_ += text__content_.nodeValue
            self.string = string_
# end class property


class object:
    subclass = None
    def __init__(self, property=None):
        if property is None:
            self.property = []
        else:
            self.property = property
    def factory(*args_, **kwargs_):
        if object.subclass:
            return object.subclass(*args_, **kwargs_)
        else:
            return object(*args_, **kwargs_)
    factory = staticmethod(factory)
    def get_property(self): return self.property
    def set_property(self, property): self.property = property
    def add_property(self, value): self.property.append(value)
    def insert_property(self, index, value): self.property[index] = value
    def export(self, outfile, level, name_='object'):
        showIndent(outfile, level)
        outfile.write('<%s>\n' % name_)
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write('</%s>\n' % name_)
    def exportAttributes(self, outfile, level, name_='object'):
        pass
    def exportChildren(self, outfile, level, name_='object'):
        for property_ in self.get_property():
            property_.export(outfile, level)
    def exportLiteral(self, outfile, level, name_='object'):
        level += 1
        self.exportLiteralAttributes(outfile, level, name_)
        self.exportLiteralChildren(outfile, level, name_)
    def exportLiteralAttributes(self, outfile, level, name_):
        pass
    def exportLiteralChildren(self, outfile, level, name_):
        showIndent(outfile, level)
        outfile.write('property=[\n')
        level += 1
        for property in self.property:
            showIndent(outfile, level)
            outfile.write('property(\n')
            property.exportLiteral(outfile, level)
            showIndent(outfile, level)
            outfile.write('),\n')
        level -= 1
        showIndent(outfile, level)
        outfile.write('],\n')
    def build(self, node_):
        attrs = node_.attributes
        self.buildAttributes(attrs)
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildAttributes(self, attrs):
        pass
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'property':
            obj_ = property.factory()
            obj_.build(child_)
            self.property.append(obj_)
# end class object


from xml.sax import handler, make_parser

class SaxStackElement:
    def __init__(self, name='', obj=None):
        self.name = name
        self.obj = obj
        self.content = ''

#
# SAX handler
#
class Sax_invokeHandler(handler.ContentHandler):
    def __init__(self):
        self.stack = []
        self.root = None

    def getRoot(self):
        return self.root

    def setDocumentLocator(self, locator):
        self.locator = locator
    
    def showError(self, msg):
        print '*** (showError):', msg
        sys.exit(-1)

    def startElement(self, name, attrs):
        done = 0
        if name == 'invoke':
            obj = invoke.factory()
            stackObj = SaxStackElement('invoke', obj)
            self.stack.append(stackObj)
            done = 1
        elif name == 'arguments':
            obj = arguments.factory()
            stackObj = SaxStackElement('arguments', obj)
            self.stack.append(stackObj)
            done = 1
        elif name == 'string':
            stackObj = SaxStackElement('string', None)
            self.stack.append(stackObj)
            done = 1
        elif name == 'array':
            obj = array.factory()
            stackObj = SaxStackElement('array', obj)
            self.stack.append(stackObj)
            done = 1
        elif name == 'property':
            obj = property.factory()
            stackObj = SaxStackElement('property', obj)
            self.stack.append(stackObj)
            done = 1
        elif name == 'object':
            obj = object.factory()
            stackObj = SaxStackElement('object', obj)
            self.stack.append(stackObj)
            done = 1
        if not done:
            self.reportError('"%s" element not allowed here.' % name)

    def endElement(self, name):
        done = 0
        if name == 'invoke':
            if len(self.stack) == 1:
                self.root = self.stack[-1].obj
                self.stack.pop()
                done = 1
        elif name == 'arguments':
            if len(self.stack) >= 2:
                self.stack[-2].obj.set_arguments(self.stack[-1].obj)
                self.stack.pop()
                done = 1
        elif name == 'string':
            if len(self.stack) >= 2:
                content = self.stack[-1].content
                self.stack[-2].obj.set_string(content)
                self.stack.pop()
                done = 1
        elif name == 'array':
            if len(self.stack) >= 2:
                self.stack[-2].obj.set_array(self.stack[-1].obj)
                self.stack.pop()
                done = 1
        elif name == 'property':
            if len(self.stack) >= 2:
                self.stack[-2].obj.add_property(self.stack[-1].obj)
                self.stack.pop()
                done = 1
        elif name == 'object':
            if len(self.stack) >= 2:
                self.stack[-2].obj.set_object(self.stack[-1].obj)
                self.stack.pop()
                done = 1
        if not done:
            self.reportError('"%s" element not allowed here.' % name)

    def characters(self, chrs, start, end):
        if len(self.stack) > 0:
            self.stack[-1].content += chrs[start:end]

    def reportError(self, mesg):
        locator = self.locator
        sys.stderr.write('Doc: %s  Line: %d  Column: %d\n' % \
            (locator.getSystemId(), locator.getLineNumber(), 
            locator.getColumnNumber() + 1))
        sys.stderr.write(mesg)
        sys.stderr.write('\n')
        sys.exit(-1)
        #raise RuntimeError

USAGE_TEXT = """
Usage: python <Parser>.py [ -s ] <in_xml_file>
Options:
    -s        Use the SAX parser, not the minidom parser.
"""

def usage():
    print USAGE_TEXT
    sys.exit(-1)


#
# SAX handler used to determine the top level element.
#
class SaxSelectorHandler(handler.ContentHandler):
    def __init__(self):
        self.topElementName = None
    def getTopElementName(self):
        return self.topElementName
    def startElement(self, name, attrs):
        self.topElementName = name
        raise StopIteration


def parseSelect(inFileName):
    infile = file(inFileName, 'r')
    topElementName = None
    parser = make_parser()
    documentHandler = SaxSelectorHandler()
    parser.setContentHandler(documentHandler)
    try:
        try:
            parser.parse(infile)
        except StopIteration:
            topElementName = documentHandler.getTopElementName()
        if topElementName is None:
            raise RuntimeError, 'no top level element'
        topElementName = topElementName.replace('-', '_').replace(':', '_')
        if topElementName not in globals():
            raise RuntimeError, 'no class for top element: %s' % topElementName
        topElement = globals()[topElementName]
        infile.seek(0)
        doc = minidom.parse(infile)
    finally:
        infile.close()
    rootNode = doc.childNodes[0]
    rootObj = topElement.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0)
    return rootObj


def saxParse(inFileName):
    parser = make_parser()
    documentHandler = Sax_invokeHandler()
    parser.setDocumentHandler(documentHandler)
    parser.parse('file:%s' % inFileName)
    root = documentHandler.getRoot()
    sys.stdout.write('<?xml version="1.0" ?>\n')
    root.export(sys.stdout, 0)
    return root


def saxParseString(inString):
    parser = make_parser()
    documentHandler = Sax_invokeHandler()
    parser.setDocumentHandler(documentHandler)
    parser.feed(inString)
    parser.close()
    rootObj = documentHandler.getRoot()
    #sys.stdout.write('<?xml version="1.0" ?>\n')
    #rootObj.export(sys.stdout, 0)
    return rootObj


def parse(inFileName):
    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    rootObj = invoke.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="invoke")
    return rootObj


def parseString(inString):
    doc = minidom.parseString(inString)
    rootNode = doc.documentElement
    rootObj = invoke.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_="invoke")
    return rootObj


def parseLiteral(inFileName):
    doc = minidom.parse(inFileName)
    rootNode = doc.documentElement
    rootObj = invoke.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('from invoke import *\n\n')
    sys.stdout.write('rootObj = invoke(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="invoke")
    sys.stdout.write(')\n')
    return rootObj


def main():
    args = sys.argv[1:]
    if len(args) == 2 and args[0] == '-s':
        saxParse(args[1])
    elif len(args) == 1:
        parse(args[0])
    else:
        usage()


if __name__ == '__main__':
    main()
    #import pdb
    #pdb.run('main()')

