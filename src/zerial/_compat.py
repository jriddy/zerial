from typing import Generic, TypeVar


TypeVarMeta = type(TypeVar)
if TypeVarMeta is type:
    TypeVarMeta = type('fake_metatype', (type,), {})


def isconcretetype(t):
    """Determine if t is a concrete type.

    By concrete, I mean a real, instantiatable datatype in the sense of a
    class that produces real instance objects.  None of this ABC abstractmethod
    mumbo-jumbo, or metaclass tomfoolery, egg-headed generic types, or wishy-
    washy union variants.

    What we want here is an honest, hardworking datatype, like God intended.

    Does not work with ``typing.NewType``s.  They are concrete, and they can
    look like types to the type checker, but they are not type-y enough for us.
    """
    return (
        isinstance(t, type)
    ) and not (
        getattr(t, '__abstractmethods__', False) or
        issubclass(t, type) or
        t is Generic or
        t is TypeVar or
        isinstance(t, TypeVarMeta) or
        getattr(t, '__parameters__', None)
    )


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
