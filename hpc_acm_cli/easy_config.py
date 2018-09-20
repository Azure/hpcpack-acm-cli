import sys

if sys.version_info >= (3, 0):
    from configparser import ConfigParser as EasyConfig
else:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError

    class EasyConfig(ConfigParser):
        def get(self, section, option, fallback=None):
            try:
                value = ConfigParser.get(self, section, option)
            except (NoSectionError, NoOptionError):
                value = fallback
            return value

        def getint(self, section, option, fallback=None):
            try:
                value = ConfigParser.getint(self, section, option)
            except (NoSectionError, NoOptionError):
                value = fallback
            return int(value)

