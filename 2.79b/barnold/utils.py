import random
import types


def getRandomString(length):
    random.seed()
    return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
                   for _ in range(length))


def catch_registration_error(func):
    def decorated_function(cls):
        try:
            func(cls)
        except (RuntimeError, AttributeError, ValueError, TypeError) as e:
            if "unregister" in str(func.__name__):
                IO.warning("Class: %s could not register. \n"
                           "Ignore this exception for CollectionProperties"
                           % cls.__name__)
            else:
                IO.warning("Class: %s could not unregister. \n"
                           "Ignore this exception for CollectionProperties"
                           % cls.__name__)
        return


    return decorated_function


def print_dict(rand_dict, indent=0):
    """
    Prints a dictionary in a 'pretty' manner.

    :param rand_dict: A dictionary with items in it.
    :type: dict

    :param indent: How much to indent when printing the dictionary.
    :type: int
    """
    for key, value in rand_dict.items():
        print('  ' * indent + str(key))
        if isinstance(value, dict):
            print_dict(value, indent + 2)
        else:
            print('  ' * (indent + 2) + str(value))


# ----------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- CLASSES --#
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[86m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[124m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''


class IO(object):
    """
    This class handles the outputting of printed information.
    """


    @classmethod
    def warning(cls, message):
        """
        Prints a message with the warning label attached.

        :param message: The message to output.
        :type: str
        """
        print("\n%sWARNING: %s\n" % (bcolors.WARNING, message) + bcolors.ENDC)


    @classmethod
    def info(cls, message):
        """
        Prints a message.

        :param message: The message to output.
        :type: str
        """
        print("\n%s  %s\n" % (bcolors.HEADER, message) + bcolors.ENDC)


    @classmethod
    def debug(cls, message):
        """
        Prints a message with the debug label attached.

        :param message: The message to output.
        :type: str
        """
        print("%s  DEBUG: %s" % (bcolors.OKBLUE, message) + bcolors.ENDC)


    @classmethod
    def error(cls, message):
        """
        Prints a message with the error label attached.

        :param message: The message to output.
        :type: str
        """
        print("\n%s  ERROR: %s\n" % (bcolors.FAIL, message) + bcolors.ENDC)


    @classmethod
    def block(cls, message):
        """
        Prints one line of a block of text.

        :param message: The message to output.
        :type: str
        """
        print("%s  %s" % (bcolors.OKGREEN, message) + bcolors.ENDC)


    @classmethod
    def list(cls, input_list):
        """
        Prints a list in a readable manner.

        :param input_list: The dictionary to print.
        :type: list
        """
        print("\n  LIST CONTENTS:")
        for item in input_list:
            print("%s    %s" % (bcolors.OKBLUE, item) + bcolors.ENDC)


    @classmethod
    def dict(cls, input_dict):
        """
        Prints a dictionary in a readable manner.

        :param input_dict: The dictionary to print.
        :type: dict
        """
        print("\n  DICTIONARY CONTENTS:")
        print_dict(input_dict)


# Autovivification
class Autovivification(dict):
    """
    A dictionary that tries to insert a key, and then resolves that key as
    this dictionary's own type and it's it to itself. Very handy for creating
    auto-nested dicts. Only works up to 2 levels before becoming unwieldy.
    """


    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
