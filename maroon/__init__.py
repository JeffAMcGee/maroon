from maroon import *
from tee import TeeDB
from mock import MockDB
from maroondb import MaroonDB, ASCENDING, DESCENDING

from mongo import MongoDB

try:
    from maroon.couch import CouchDB
except ImportError:
    pass
