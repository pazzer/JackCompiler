__author__ = 'paulpatterson'

SEGMENT_NAMES_MAP = {"CONST" : "constant", "ARG" : "argument", "VAR" : "local", "STATIC" : "static", "THIS" : "this",
                     "THAT": "that", "POINTER" : "pointer", "TEMP" : "temp", "FIELD" : "this"}


class VMWriter():

    def __init__(self, vm_file_path):
        """ Creates a new output.vm file and prepares it for writing. """
        self.vm_file_path = vm_file_path
        self.outfile = open(self.vm_file_path.as_posix(), mode="w+")

    def write_push(self, segment, index):
        """ Writes a vm push command.

        Segment: one of CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        Index: an integer
        """
        self.outfile.write("push {} {}\n".format(SEGMENT_NAMES_MAP[segment], index))

    def write_pop(self, segment, index):
        """ Writes a vm pop command.

        Segment: one of CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        Index: an integer"""
        self.outfile.write("pop {} {}\n".format(SEGMENT_NAMES_MAP[segment], index))

    def write_arithmetic(self, command):
        """ Writes a vm arithmetic logical command.

        command: one of ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        """
        self.outfile.write(command.lower() + "\n")

    def write_label(self, label):
        """ Writes a vm label command. """
        self.outfile.write("label {}\n".format(label))

    def write_goto(self, label):
        """ Writes a vm goto command. """
        self.outfile.write("goto {}\n".format(label))

    def write_if_goto(self, label):
        """ Writes a vm if-goto command. """
        self.outfile.write("if-goto {}\n".format(label))

    def write_call(self, name, num_args):
        """ Writes a vm call command. """
        self.outfile.write("call {} {}\n".format(name, num_args))

    def write_function(self, name, num_locals):
        """ Writes a vm function command. """
        self.outfile.write("function {} {}\n".format(name, num_locals))

    def write_return(self):
        """ Writes a vm return command. """
        self.outfile.write("return\n")

    def write_string(self, string):
        """ Writes a string constant. """
        ascii_codes = [ord(character) for character in string[1:-1]]
        self.write_push("CONST", len(ascii_codes))
        self.write_call("String.new", 1)
        for ascii_code in ascii_codes:
            self.write_push("CONST", ascii_code)
            self.write_call("String.appendChar", 2)


    def close(self):
        """Closes the output file. """
        pass


