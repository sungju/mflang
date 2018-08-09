class MetafontChar:
    """
    beginchar(⟨code⟩, ⟨width⟩, ⟨height⟩, ⟨depth⟩);

    Here ⟨code⟩ is either a quoted single character like "O" or a number
    that rep- resents the character’s position in the final font.
    The other three quantities ⟨width⟩, ⟨height⟩, and ⟨depth⟩ say how big
    the bounding box is, so that typeset- ting systems like TEX will be
    able to use the character. These three dimensions must be given in
    device-independent units, i.e., in “sharped” form.
    """
    def_string = ""
    body_string = ""

    code = ""
    height = 0
    width = 0
    depth = 0

    def __init__(self, def_string):
        self.set_definition(def_string)

    def set_definition(self, def_string):
        self.def_string = def_string

    def set_values(self, code, height, width, depth):
        self.code = code
        self.height = height
        self.width = width
        self.depth = depth

    def get_definition(self):
        return self.def_string

    def set_body(self, body_string):
        self.body_string = body_string

    def get_body(self):
        return self.body_string

    def __repr__(self):
        return "{" + self.def_string + "}\n{" + self.body_string + "}"



class MetafontDef:
    def_string = ""
    body_string = ""
    func_name = ""
    func_args = None

    def __init__(self, def_string):
        self.set_definition(def_string)

    def set_definition(self, def_string):
        self.def_string = def_string

    def get_definition(self):
        return self.def_string

    def set_func_name(self, func_name):
        self.func_name = func_name

    def get_func_name(self):
        return self.func_name

    def set_func_args(self, func_args):
        self.func_args = func_args

    def get_func_args(self):
        return self.func_args

    def set_body(self, body_string):
        self.body_string = body_string

    def get_body(self):
        return self.body_string

    def __repr__(self):
        return "{" + self.def_string + "}\n{" + self.body_string + "}"
