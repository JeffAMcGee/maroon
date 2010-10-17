#!/usr/bin/env python

import sys
sys.path.append("..")
import unittest
from operator import attrgetter
import datetime

import pymongo

import maroon
from maroon import Model, IntProperty, Property
from mongo import MongoDB
from couch import CouchDB
from models import SimpleModel, FunModel, PersonModel


class TestBasicModelCreationAndAssignment(unittest.TestCase):

    def setUp(self):
        self.o1 = SimpleModel()
        self.o2 = SimpleModel()
        self.o3 = SimpleModel()

    def test_simple_save(self):
        self.o1.int1 = 44
        self.o1.save()
        self.failIfEqual(self.o1._id, None)

    def test_update_object(self):
        #make sure that we replace objects when they are updated
        self.o1._id = "mustafa"
        self.o1.int1 = 1
        self.o1.int2 = 2
        self.o1.save()
        ob = SimpleModel.get_id("mustafa")
        ob.int2 = 3
        ob.save()
        ob = SimpleModel.get_id("mustafa")
        self.failUnlessEqual(3, ob.int2)

    def test_missing_fields(self):
        obj1 = SimpleModel({'_id':'simba','i1':2})
        obj1.save()
        ob = SimpleModel.get_id('simba')
        self.failUnlessEqual(ob.int2, None)

    def test_set_missing_field(self):
        SimpleModel({'i1':2,'_id':'timon'}).save()
        ob = SimpleModel.get_id('timon')
        ob.int2 = 15
        ob.save()
        ob = SimpleModel.get_id('timon')
        self.failUnlessEqual(ob.int2, 15)

    def test_remove_field(self):
        self.o2._id = "nala"
        self.o2.int1 = 2
        self.o2.int2 = 3
        self.o2.save()
        item = SimpleModel.get_id("nala")
        self.failUnlessEqual( item.int2, 3)
        item.int2 = None
        item.save()
        result = SimpleModel.get_id("nala")
        self.failUnlessEqual( result.int2, None)

    def test_get_all(self):
        for name in ['pumba','zazu']:
            m = PersonModel(name=name, age=(10+len(name)))
            m.save()

        people = sorted(PersonModel.get_all(),key=attrgetter('age'))
        self.failUnlessEqual( people[0].name, 'zazu')
        self.failUnlessEqual( people[0].age, 14)
        self.failUnlessEqual( people[1].name, 'pumba')
        self.failUnlessEqual( people[1].age, 15)

    def test_fun_model(self):
        dic = {"one":2, 'three':"four", 'five':["six",7]}
        names = ['Shenzi', 'Banzai', 'ed']
        now = datetime.datetime.now()
        fun = FunModel(
                _id="fun",
                enum="red",
                real=3.14,
                dic=dic,
                names=names,
                )
        fun.part=PersonModel(name="scar", age=32)
        fun.save()
        fun = FunModel.get_id("fun")
        self.failUnlessEqual( fun.enum, 'red')
        self.failUnlessEqual( fun.real, 3.14)
        self.failUnlessEqual( fun.dic, dic)
        dt = abs(fun.created-now)
        self.failUnless( dt.days==0 and dt.seconds==0 )
        self.failUnlessEqual( fun.names, names)
        self.failUnlessEqual( fun.part.name, "scar")
        self.failUnlessEqual( fun.part.age, 32)


if __name__ == '__main__':
    db = sys.argv[1]
    if db=='mongo':
        Model.database = MongoDB(None,'test_maroon')
        for m in ('SimpleModel', 'FunModel', 'PersonModel'):
            Model.database[m].remove()
    elif db=='couch':
        Model.database = CouchDB('http://127.0.0.1:5984/test_maroon',True)
        Model.database.flush()
    else:
        print "Usage: ./database_tests.py [mongo|couch]"
    if hasattr(Model,'database'):
        del sys.argv[1]
        unittest.main()
