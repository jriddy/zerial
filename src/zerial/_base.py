from abc import ABCMeta, abstractmethod
from typing import Any

from ._compat import with_metaclass


class Ztype(with_metaclass(ABCMeta)):
    """ztype interface

    Despite the name it is not an actual type, but a transfomer object.  It is
    meant to be stored as metadata on record types and extracted to use in
    structuring operations.
    """
    apparent_type = Any

    @abstractmethod
    def destruct(self, inst, ztr):
        """Unstructure inst into a mapping.

        The Ztructurer doing the destructuring is passed for its options and to
        permit further recursive descent if necessary.

        Works with the Ztructurer to take apart more complex types.
        """

    @abstractmethod
    def restruct(self, mapping, ztr):
        """Structure the mapping into the appropriate type.

        The Ztructurer doing the rebuilding is passed for its options and to
        permit recursive rebuilding if needed.

        Works with Ztructurer to rebuild more complext types.
        """
