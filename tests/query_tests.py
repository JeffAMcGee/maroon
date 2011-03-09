#!/usr/bin/env python

import sys
sys.path.append("..")

from mongo import MongoDB
import unittest

import maroon
from maroon import Model, TextProperty, IntProperty, ListProperty, BogusQuery


class NumberModel(Model):
    '''
    A very simple example of a model consisting of a few simple members.  This will
    be used to test simple assignment and also dictionary exporting
    '''
    n = IntProperty('n')
    quad = IntProperty('quad')
    name = TextProperty('name')
    factors = ListProperty('factors')

def _number_set_up():
    names = 'zero one two three four five six seven eight nine ten'.split()
    for i in xrange(len(names)):
        NumberModel(
            n=i,
            quad=((i-5)**2),
            name=names[i],
            factors=[x for x in xrange(1,i+1) if i%x==0]
        ).save()

def _query_to_list(q):
    return sorted( [nm.n for nm in NumberModel.find(q)] )


class TestQueries(unittest.TestCase):

    def test_query(self):
        n = NumberModel.n
        name = NumberModel.name
        self.failUnlessEqual( [8,9,10], _query_to_list( n>7 ) )
        self.failUnlessEqual( [4,5], _query_to_list( (n>3) & (n<6) ) )
        self.failUnlessEqual( [4,5,10], _query_to_list(
            (n>3) & (name//'^[tf]') )
        )
   
    def test_impossible(self):
        n = NumberModel.n
        self.failUnlessRaises( BogusQuery,
            lambda: NumberModel.find( (n==1) & (n==2) ))
        self.failUnlessRaises( BogusQuery,
            lambda: NumberModel.find( (n>1) & (n>2) ))
        self.failUnlessRaises( BogusQuery,
            lambda: NumberModel.find( (n==1) & (n>2) ))
        x = 3
        self.failUnlessRaises( BogusQuery,
            lambda: NumberModel.find( x>2) )
        self.failUnlessRaises( BogusQuery,
            lambda: NumberModel.find( x<=2) )

    def test_and(self):
        n = NumberModel.n
        quad = NumberModel.quad
        name = NumberModel.name
        self.failUnlessEqual( [4,5], _query_to_list( (n>3)&(n<=5) ) )
        self.failUnlessEqual( [3,4,6], _query_to_list( (n>=3)&(n<7)&(n!=5) ))
        self.failUnlessEqual( [2,3,6,7,10], _query_to_list(
            ((name//'^[tfs]')&(n!=4)) &(quad>0)) )
        self.failUnlessEqual( [2,3,6,7,10], _query_to_list(
            (name//'^[tfs]' &((n!=4))&(quad>0))) )

    def test_or(self):
        n = NumberModel.n
        quad = NumberModel.quad
        name = NumberModel.name
        self.failUnlessEqual( [2,4,6], _query_to_list( (n==2)|(n==4)|(n==6) ) )
        self.failUnlessEqual( [2,3,5,7], _query_to_list(
            (((n==2)|(n==3)) |(n==5)) |(n==7) ))
        self.failUnlessEqual( [2,3,5,7], _query_to_list(
            (n==2)| ((n==3)| ((n==5)|(n==7))) ))

    def test_nesting(self):
        n = NumberModel.n
        quad = NumberModel.quad
        self.failUnlessEqual( [1,4,5,9], _query_to_list(
            ((quad>15)&(quad<17)) | ((n>=4)&(n<=5)) ))
        self.failUnlessEqual( [0,3,6,7,10], _query_to_list(
            ((quad>17)|(quad<8)) & ((n<4)|(n>5)) ))
        self.failUnlessEqual( [0,3,7,8,9], _query_to_list(
            (n==0)| ((quad<20)& ((n==3)|(n>6))) ))
        self.failUnlessEqual( [3,4,6,7,8,10], _query_to_list(
            (n>=3)& ((quad==25)| ((quad>0)&(quad<10))) ))

    def test_is_in(self):
        n = NumberModel.n
        self.failUnlessEqual( [1,4,5,9], _query_to_list(
            n.is_in([1,4,5,9]) ))

    def test_is_not_in(self):
        n = NumberModel.n
        self.failUnlessEqual( [0,2,3,6,7,8], _query_to_list(
            n.is_not_in([1,4,5,9,10]) ))

    def test_list_has(self):
        factors = NumberModel.factors
        self.failUnlessEqual( [2,4,6,8,10], _query_to_list(
            factors == 2 ))

    def test_list_has_all(self):
        factors = NumberModel.factors
        self.failUnlessEqual( [6], _query_to_list(
            factors.has_all([2,3]) ))


if __name__ == '__main__':
    Model.database = MongoDB(None,'test_maroon')
    Model.database.NumberModel.remove()
    _number_set_up()
    unittest.main()
