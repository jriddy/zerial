def isconcretetype(t):
    return not getattr(t, '__abstractmethods__', False)


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass.

    This method is blatently stolen from the six_ project, which I like, but
    don't want to make an additional dependency of this project.

    .. _six: https://pypi.org/project/six/
    """
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(type):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

        @classmethod
        def __prepare__(cls, name, this_bases):
            return meta.__prepare__(name, bases)
    return type.__new__(metaclass, 'temporary_class', (), {})
