"""
mflang preprocessor

It's expanding 'input' to include other files.
"""

import sys
import os
import io
import base64

INTERNAL_FUNC_NAME = "__mflang_generated_function_name__"

file_path = ""

def get_file_lines(filename):
    file_lines = None
    try:
        f = open(filename)
        file_lines = f.readlines()
        f.close()
    except:
        file_lines = None

    return file_lines


def expand_lines(file_lines):
    mode_beginchar = False
    content_beginchar = ""
    mode_def = False
    content_def = ""
    mode_vardef = False
    content_vardef = ""

    if file_lines == None:
        return

    for line in file_lines:
        a_line = line.strip()
        if a_line.startswith("input "):
            if a_line.find("%") > -1:
                a_line = a_line[:a_line.find("%")]

            filename = a_line[6:].strip()
            if filename.endswith(";"):
                filename = filename[:-1]
            print ("%s %s" % ("%", a_line))
            if not filename.endswith(".mf"):
                filename = filename + ".mf"
                print ("%s Replaced the name to %s" % ("%", filename))

            filename = file_path + filename
            print ("%s Begin of <%s>" % ("%", filename))
            expand_lines(get_file_lines(filename))
            print ("%s End of <%s>" % ("%", filename))
        elif a_line.startswith("def ") or \
             a_line.startswith("vardef "):
            idx_equal = a_line.find("=")
            if idx_equal >= 0:
                a_line = a_line[:idx_equal].strip()

            if a_line.startswith("def "):
                print ("def%s(\"%s\");" % (INTERNAL_FUNC_NAME,
                                           base64.b64encode(a_line[4:].encode())))
                mode_def = True
            else:
                print ("vardef%s(\"%s\");" % (INTERNAL_FUNC_NAME,
                                              base64.b64encode(a_line[7:].encode())))
                mode_vardef = True
        elif a_line.startswith("enddef;") or \
             a_line.find(" enddef;") >= 0: # Stupid coding allows the line ending with 'enddef;'.

            if mode_def:
                content = content_def
            else:
                content = content_vardef
            idx = a_line.find(" enddef;")
            if (idx > -1):
                content = content + a_line[:idx]
            print ("enddef%s(\"%s\");" % (INTERNAL_FUNC_NAME, base64.b64encode(content.encode())))
            mode_def = False
            content_def = ""
            mode_vardef = False
            content_vardef = ""
        elif mode_def == True:
            content_def = content_def + line
        elif mode_vardef == True:
            content_vardef = content_vardef + line
        elif a_line.startswith("endchar;"):
            print ("endchar%s(\"%s\");" % (INTERNAL_FUNC_NAME,
                                           base64.b64encode(content_beginchar.encode())))
            mode_beginchar = False
            content_beginchar = ""
        elif mode_beginchar == True:
            content_beginchar = content_beginchar + line
        elif  a_line.replace(" ", "").startswith("beginchar("):
            idx_lbrace = a_line.find("(")
            idx_rbrace = a_line.rfind(")")
            a_line = a_line[idx_lbrace + 1:idx_rbrace]
            print ("beginchar%s(\"%s\");" % (INTERNAL_FUNC_NAME, base64.b64encode(a_line.encode())))
            mode_beginchar = True
        else:
            print (line.rstrip())

def preprocessor(filename):
    global file_path

    file_path = os.path.dirname(filename)
    if file_path == "":
        file_path = "."
    file_path = file_path + "/"
    file_lines = get_file_lines(filename)
    expand_lines(file_lines)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        preprocessor(sys.argv[1])
