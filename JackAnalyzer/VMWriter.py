__author__ = 'paulpatterson'

class VMWriter():

    def __init__(self):
        """ Creates a new output.vm file and prepares it for writing. """
        pass

    def write_push(self, segment, index):
        """ Writes a vm push command.

        Segment: one of CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        Index: an integer
        """
        pass

    def write_pop(self, segment, index):
        """ Writes a vm pop command.

        Segment: one of CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        Index: an integer"""
        pass

    def writes_arithmetic(self, command):
        """ Writes a vm arithmetic logical command.

        command: one of ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        """
        pass

    def write_label(self, label):
        """ Writes a vm label command. """
        pass

    def write_goto(self, label):
        """ Writes a vm goto command. """
        pass

    def write_if(self, label):
        """ Writes a vm if-goto command. """
        pass

    def write_call(self, label):
        """ Writes a vm call command. """
        pass

    def write_function(self, name, num_locals):
        """ Writes a vm function command. """
        pass

    def write_return(self):
        """ Writes a vm return command. """
        pass

    def close(self):
        """Closes the output file. """
        pass


