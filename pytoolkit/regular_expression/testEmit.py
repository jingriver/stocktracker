import re

# common variables

rawstr = r"""emit\s*\(\s*SIGNAL\s*\([\s,\w,\",\']+\)\s*,\s*(\([\w,\,\s,\",\',\.]*\))"""
embedded_rawstr = r"""emit\s*\(\s*SIGNAL\s*\([\s,\w,\",\']+\)\s*,\s*(\([\w,\,\s,\",\',\.]*\))"""
                        
#matchstr = """self.emit (      SIGNAL  ( " locked  "  )  , (self,))"""
#matchstr = """self.emit (SIGNAL("locked"), (self, hello))"""
#matchstr = """self.emit (SIGNAL("locked"), (self, ))"""
matchstr = """self.emit (SIGNAL("locked"), ())"""
#matchstr = """self.emit(SIGNAL("changeTab"),("menuTab",))"""
matchstr = """self.emit(SIGNAL("startDateChanged"), (sessionData.startDate,))"""

# method 1: using a compile object
compile_obj = re.compile(rawstr)
match_obj = compile_obj.search(matchstr)

## method 2: using search function (w/ external flags)
#match_obj = re.search(rawstr, matchstr)
#
## method 3: using search function (w/ embedded flags)
#match_obj = re.search(embedded_rawstr, matchstr)

# Retrieve group(s) from match_obj
if match_obj: 
    all_groups = match_obj.groups()
    
    # Retrieve group(s) by index
    group_1 = match_obj.group(1)
    print group_1
    
    if group_1[0]=="(" and group_1[0]=="(": 
        repl=group_1[1:-1]
        group_1 = "\(" + repl + "\)"
        repl = repl.strip()
        if repl=="":
            group_1 = "\s*,\s*\(" + repl + "\)"
        elif repl[-1]==",":
            repl = repl[:-1]    
    print repl
    
    
    # Replace string
    newstr = re.sub(group_1,repl, matchstr)
    print newstr