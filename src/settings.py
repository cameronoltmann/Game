'''
Created on 2012-08-08

@author: grud
'''

import ConfigParser

class Settings(object):
    '''
    Persistent program settings management class
    Uses ConfigParser to load/save/parse config files
    Designed to simplify dealing with a config file if you have simple needs
    - eg a single section
    '''
    default_section = 'Main'
    defaults = {default_section:
                    {'Option' : 'Setting'
                     }
                }

    def __init__(self, defaults = None, configfile='settings.cfg', default_section = None):
        '''
        Constructor
        * Set config filename instance variable
        * Load file if present
        * Assign any default values that haven't been set
        '''
        if not default_section:
            default_section = Settings.default_section
        if not defaults:
            defaults = Settings.defaults
        self._defaults = defaults
        self._configfile=configfile
        self._config = ConfigParser.SafeConfigParser()
        self._config.read(self._configfile)
        self._default_section = default_section
        self.set_missing_defaults(defaults)

    def __repr__(self):
        #return 'Settings object'
        val = ''
        for section in self._config.sections():
            val += '[%s]\n' % section
            for option in self._config.options(section):
                val += '%s = %s\n' % (option, self._config.get(section, option))
        return val
            
    def set_missing_defaults(self, defaults=None):
        '''
        Set any missing defaults according to Settings.defaults
        '''
        if not defaults:
            defaults = Settings.defaults
        for section in defaults:
            for setting in defaults[section]:
                if not self._config.has_option(section, setting):
                    self.set(setting, defaults[section][setting], section)

    def get(self, setting, section = default_section):
        '''
        Fetch a setting, choosing default section if unspecified
        - quality of life function
        '''
        if self._config.has_option(section, setting):
            return self._config.get(section, setting)
        return None

    def get_bool(self, setting, section = default_section):
        '''
        Fetch a setting as a boolean value, choosing default section if unspecified
        - quality of life function
        '''
        if self._config.has_option(section, setting):
            return self._config.getboolean(section, setting)
        return None

    def set(self, setting, val, section = default_section):
        '''
        Set an option, choosing default section if unspecified
        - quality of life function
        '''
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, setting, val)
    
    def save(self, filename = None):
        '''
        Save the settings to the file specified, or to _configfile if unspecified
        '''
        if not filename:
            filename = self._configfile
        with open(filename, 'wb') as configfile:
            self._config.write(configfile)
    
    def load(self, filename = None):
        '''
        Load settings from the file specified, or from _configfile if unspecified
        Set any missing defaults afterwards
        '''
        if not filename:
            filename = self._configfile
        self._config.read(filename)
        self.set_missing_defaults(self._defaults)
    