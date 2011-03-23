try:
    import simplejson as json
except:
    import json
from collections import defaultdict
from operator import attrgetter
import operator
import glob

class MockDB(object):
    """Read a tiny database from the filesystem, and modify it in-memory.
    This class is only for testing and debuging purposes!"""
    def __init__(self, path=None, module=None):
        self.data = defaultdict(dict)
        if path and module:
            for filepath in glob.glob(path+"/*.json"):
                self._import_json(filepath,module)

    def _import_json(self,path,module):
        name = path.rpartition('/')[2].replace(".json","")
        cls = getattr(module,name)
        for line in open(path):
            self.save(cls(from_dict=json.loads(line)))

    def bulk_save_models(self, models, cls=None):
        for m in models:
            self.save(m)

    def save(self, model):
        if model._id is None:
            model._id = id(model)
        self.data[model.__class__.__name__][model._id] = model
        return model

    def get_id(self, cls, _id):
        return self.data[cls.__name__].get(_id,None)

    def get_all(self, cls, **kwargs):
        return self.find(cls,None,**kwargs)

    def find(self, cls, q, limit=None, sort=None, descending=False, **kwargs):
        long_names = cls.long_names
        if q:
            try:
                q = q.to_mongo_dict()
            except AttributeError:
                pass
            results = [ obj
                for obj in self.data[cls.__name__].itervalues()
                if _query_matches(q, obj, long_names)
                ]
        else:
            results = self.data[cls.__name__].values()
        if sort is not None:
            try:
                name = sort.name
            except AttributeError:
                name = sort
            results.sort(
                key=attrgetter(long_names.get(name)),
                reverse=descending)
        if limit is not None:
            results = results[0:limit]
        return results

    def in_coll(self, cls, _id):
        return _id in self.data[cls.__name__]


_mongo_ops = {
    '$lte':operator.le,
    '$lt':operator.lt,
    '$ne':operator.ne,
    '$gte':operator.ge,
    '$gt':operator.gt,
    '$in':lambda v,l: v in l,
    '$nin':lambda v,l: v not in l,
    '$exists':lambda v,x: bool(x)==(v is not None),
    '$all':lambda l,g: all(v in l for v in g),
    }


def _query_matches(query,obj,long_names):
    for key,subq in query.iteritems():
        if key=='$or':
            if not any(_query_matches(q,obj,long_names) for q in subq):
                return False
            continue
        val = getattr(obj,long_names.get(key,key))
        if val==subq:
            continue
        elif isinstance(subq,dict):
            for op,goal in subq.iteritems():
                if not _mongo_ops[op](val,goal):
                    return False
        elif isinstance(val,list):
            if subq not in val:
                return False
        elif hasattr(subq,'search'):
            if not subq.search(val):
                return False
        else:
            return False
    return True
