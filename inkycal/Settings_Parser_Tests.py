import unittest
from inkycal.configuration.settings_parser import inkycal_settings

class Settings_Parser_Tests(unittest.TestCase):

    def testinit_with_default_file(self):
        settings = inkycal_settings("inkycal/configuration")