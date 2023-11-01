from uuid import *

def merge_uuid (uuid1, uuid2):
    # check if we need to convert from strings
    if isinstance(uuid1, str):
        uuid1 = UUID(uuid1)
    if isinstance(uuid2, str):
        uuid2 = UUID(uuid2)

    return UUID(int=uuid1.int ^ uuid2.int, version=4)
