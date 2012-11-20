#!/usr/bin/env python
# encoding: utf-8
"""
discourse_mapper.py

Created by Maksim Tsvetovat on 2011-12-20.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import simplejson as json
from collections import defaultdict
import logging 

import linguist as cl
import candidates as can
import media


from wordbag import wordbag
import networkx as net

from hottie import hot

corpusPath='data/'
jsonPath='data/'

l=logging.getLogger("DMAP")

@hot
class discourse_mapper(object):

    def __init__(self,interval=100):
        #self.s3=s3writer.s3writer()
        self.wb=wordbag()
        self.interval=interval
        self.counter=0
        self.gauges=defaultdict(dict)
        
    def _load_corpus(self):
        l.debug("Loading corpus")
        for key in can.candidates.keys():
            try:
                text=open(corpusPath+key+'.txt','rb').read()
            except: 
                continue
        
            tokens=cl.process(text)
            self.wb.add_tokens(key,tokens)
    
        self.wb.prune()
        
        
    def add_to_corpus(self,key,tokens):
        #tokens=cl.process(text)
        print tokens
        self.wb.add_tokens(key,tokens)
        
    
    def add(self,tokens,user):
        l.debug("adding tokens"+str(self.counter))
        self.counter+=1
        #print place['country']
        
        self._update_corpus(tokens,user)
        
        if user in media.media:
            self.wb.add_tokens(user,tokens)
            
        if self.counter>=self.interval:
            self.counter=0
            self._compute_metrics()
            self._normalize()
            self._write_data()
            

    def _update_corpus(self,tokens,user):
        for key in can.candidates.keys(): 
            if user in can.candidates[key]:
                l.info("updating cropus for"+user)
                self.wb.add_tokens(key,tokens)
                open(corpusPath+key+'.txt','a').write(str(tokens)+"\n")


    def _compute_metrics(self):
        ## for every state, every candidate, compute a linguistic match
        for mm in media.media:
            try:
                ss= set(self.wb.word_graph[mm].keys())
            except KeyError:
                continue ## we have no data for this state, we skip it
                
            for key in can.candidates.keys():
                cs= set(self.wb.word_graph[key].keys())
                ## Compute intersection between state discourse and candidate
                p=cs & ss
                self.gauges[mm][key]=float(len(p))/float(len(ss)+len(cs))
                
    def _normalize(self):
        for state in self.gauges.keys():
            total=sum(self.gauges[state].values())
            if total==0: continue
            for can in self.gauges[state].keys():
                self.gauges[state][can]=self.gauges[state][can]/total


    def _write_data(self):
        """Write out map data as JSON files to S3, to a local file OR BOTH"""
        l.info(">>>>Writing out discourse gauges")

        f=jsonPath+"gauges.json"
        out=open(f,'wb')
        out.write(json.dumps(self.gauges))

    def test(self):
        infile=open('/tmp/test_output.json')
        for line in infile:
            
            try :
                js=json.loads(line)
            except:
                l.info(line)
                l.info("discourse mapper parse error")
                continue
                
            tokens=js['tokens']
            geo=js['geo']
            self.add(geo,tokens)


        