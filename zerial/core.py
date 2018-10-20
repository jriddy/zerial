import attr


deztructure = attr.asdict


def reztructure(typ, dct):
    return typ(**dct)
