from invoke import invoke
from xml.dom import minidom

FLEXFUNCNAME = "setSymbols"
XMLTEMPLATE = """<invoke name="getPanelData"><arguments><string>%s</string><string>%s</string><string>%s</string></arguments></invoke>"""

def generateXML(panelid, label, provider):
    return  XMLTEMPLATE % (panelid, label, provider)
    
def parseFlexXML(inString=None, inFileName=None):
    if inString:
        doc = minidom.parseString(inString)
    elif inFileName:
        doc = minidom.parse(inFileName)
    else:
        raise "No input!"
    
    rootNode = doc.documentElement
    rootObj = invoke.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    
    func_name = rootObj.get_name()
    if func_name!=FLEXFUNCNAME:
        return None    
    arg = rootObj.get_arguments()
    event_name = arg.get_string()
    props = arg.get_array().get_property()
    msgs = []
    for p in props:
        #id = p.get_id()
        obj = p.get_object()
        #print obj.get_property()[0].get_id()
        expression = obj.get_property()[0].get_string()
        #print obj.get_property()[1].get_id()
        label = obj.get_property()[1].get_string()
        msgs.append([expression, label])    
    return (event_name, msgs)

if __name__ == '__main__':
    print parseFlexXML(inFileName = "invoke-replace.xml")
    

