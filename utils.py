from inspect import ismethod

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class NamingEnum:
    @classmethod
    def __init_names__(cls):
        for attr in cls.keys():
            getattr(cls, attr).name = attr
            # print(f"{attr}: {type(getattr(cls, attr))}")

    @classmethod
    def keys(cls):
        return [a for a, v in cls.__dict__.items() if not a.startswith('__') and not ismethod(v)]
    
    @classmethod
    def items(cls):
        return [(a,v) for a, v in cls.__dict__.items() if not a.startswith('__') and not ismethod(v)]

    @classmethod
    def values(cls):
        return [v for a, v in cls.__dict__.items() if not a.startswith('__') and not ismethod(v)]