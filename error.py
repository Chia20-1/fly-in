class MapValidationError(Exception):
    """
    Indicate inconsistent zones names or connections in a map.

    Rejects repeated zone names, repeated connections, unknown
    connection end points, and faulty data type conversion.
    """
    pass


class MapParserError(Exception):
    """
    Indicate a map file could not be read or its syntax is invalid.

    Rejects invalid whitespace, missing `:`, unknown or duplicate declaration
    keys, unknown or duplicate value, wrong first declaration, zone names
    containing `-`, invalid metadata whitspaces, invalid metadata items,
    repeated metadata keys, and unsupported metadata keys.
    """
    pass
