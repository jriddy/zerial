from typing import List

builtin_type = type


def zdata(type):
    if not isinstance(type, builtin_type):
        raise TypeError("{} is not a type".format(type))
    return {'zerial': {
        'type': type,
    }}


def Zequence(t):
    return List[t]
