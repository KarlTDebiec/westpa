import os, sys, re

class ConfigDict(dict):
    true_values = set(('1', 'true', 't', 'yes', 'y'))
    false_values = set(('0', 'false', 'f', 'no', 'n'))
    default_list_split = re.compile(r'\s*,?\s*')

    defaults = {}
    
    def __init__(self, *args, **kwargs):
        self.update(self.defaults)
        super(ConfigDict,self).__init__(*args, **kwargs)
            
    def read_config_file(self, config_filename):
        from ConfigParser import SafeConfigParser
        
        config_file = open(config_filename, 'r')
        cparser = SafeConfigParser()
        cparser.optionxform = str
        cparser.readfp(config_file)
        
        self.filename = self['__file__'] = os.path.abspath(config_filename)
        self.dirname  = self['__dir__'] = os.path.dirname(self.filename)
        
        for section in cparser.sections():
            for (key, value) in cparser.items(section):
                self['%s.%s' % (section, key)] = value
                
    def _get_typed(self, key, type_, *args):
        
        try:
            return type_(self[key])
        except KeyError, ke:
            try:
                return args[0]
            except IndexError:
                return ke

    def get_int(self, key, *args):
        if len(args) > 1:
            raise TypeError('unexpected positional argument encountered')

        try:
            return int(self[key])
        except KeyError, ke:
            try:
                return args[0]
            except IndexError:
                raise ke
    
    def get_bool(self, key, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('unexpected positional argument encountered')

        try:
            strict = kwargs['strict']
            del kwargs['strict']
        except KeyError:
            strict = True
            
        if kwargs:
            raise TypeError('unexpected keyword argument %r encountered'
                            % kwargs.pop()[0] )
            
        try:
            val = str(self[key]).lower()
        except KeyError, ke:
            try:
                return args[0]
            except IndexError:
                raise ke

        if val in self.false_values:
            return False
        else:
            if strict:
                if val in self.true_values:
                    return True
                else:
                    raise ValueError('invalid boolean literal %r' % val)
            else:
                return True

    def get_float(self, key, *args):
        if len(args) > 1:
            raise TypeError('unexpected positional argument encountered')

        try:
            return float(self[key])
        except KeyError, ke:
            try:
                return args[0]
            except IndexError:
                raise ke
    
    
    def get_list(self, key, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('unexpected positional argument encountered')

        split = re.compile(kwargs.get('split', self.default_list_split))
        try:
            return split.split(self[key])
        except KeyError, ke:
            try:
                return args[0]
            except IndexError:
                raise ke
            
    def get_path(self, key, *args):
        if len(args) > 1:
            raise TypeError('unexpected positional argument encountered')

        try:
            path = self[key]
        except KeyError, ke:
            try:
                path = args[0]
            except IndexError:
                raise ke
            
        if os.path.isabs(path):
            return os.path.normpath(path)
        else:
            return os.path.normpath(os.path.join(self['__dirname__'], path))
        
    def get_python_object(self, key, *args):
        if len(args) > 1:
            raise TypeError('unexpected positional argument encountered')
        
        try:
            qualname = self[key]
        except KeyError, ke:
            try:
                return args[0]
            except IndexError:
                raise ke
        
        (module_name, symbol) = qualname.rsplit('.', 1)

        try:
            module = sys.modules[module_name]
        except KeyError:
            module = __import__(module_name)
            
        return getattr(module, symbol)