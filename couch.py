import couchdbkit
from couchdbkit import Database


class CouchDB(Database):
    def save(self, model):
        d = model.to_d()
        d.setdefault('doc_type',model.__class__.__name__)
        self.save_doc(d)
        model._id = d['_id'] # save the unique id from couchdb
        model._rev = d['_rev'] # save the unique id from couchdb
        return model

    def get_id(self, cls, _id):
        d = self.open_doc(_id)
        return cls(d)

    def get_all(self, cls):
        #FIXME: this should page results so it doesn't crash and burn!
        for doc in self.all_docs(include_docs=True):
            if doc['doc'].get('doc_type',None) == cls.__name__:
                yield cls(doc['doc'])

    def paged_view(self, view_name, page_size=1000, **params):
        #FIXME: you can't set a limit with a paged view!
        params['limit']=page_size+1
        while True:
            res = list(self.view(view_name, **params))
            for r in res[0:page_size]:
                yield r
            if len(res) != page_size+1:
                break
            params['startkey']=res[-1]['key']
            params['startkey_docid']=res[-1]['id']
