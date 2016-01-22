# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import sys
import os
import pwd

import indexing
import math

from datetime import datetime

import collections

import cfc_tools

def main():
    if len(sys.argv) != 3:
        print('alefrise 2016 - Alef Recumeração de informação [Search Engine]')
        print('  Uso: python3 %s cfcdirectory queryfile', sys.argv[0])
        print('cfcdirectory\t - CFC Database Directory')
        print('queryfile\t - Query file location')
        return 0
    cfcdirectory = sys.argv[1]
    queryfile = sys.argv[2]

        #Start up print
    print('AlefRise - %s [%s]' %
      (pwd.getpwuid(os.getuid())[4],os.getlogin()),
      '\nQueries:', queryfile,
      '\nCFC Location:', cfcdirectory,
      '\nRunning on Python',sys.version)

    print('Checking CFC location...')
    cfclist, indexfile = list_cfcdir(cfcdirectory)

    if indexfile:
        print('Index file', indexfile, 'found! Not processing CFC files!')
        index = cfc_tools.load_index(cfcdirectory + os.sep + indexfile)
    else:
        #Load File
        print('Creating index from CFC files...')
        index = CFCIndex()
        for cfcfile in cfclist:
            print('Processing', cfcdirectory + os.sep + cfcfile)
            doc_dict = cfc_tools.read_docfile(cfcdirectory + os.sep + cfcfile)
            index.add_docstf(doc_dict)
        print('Calculating IDFs...')
        print('Calculating Norms and Weights...')
        index.update_idf()
        index.prepare_weight()

        #process weights
        print('Saving Index...')
        cfc_tools.save_index(index, cfcdirectory + os.sep + 'cfc.index')
        print('Index saved in', cfcdirectory + os.sep + 'cfc.index')

    print('Reading Queries...')
    queries = cfc_tools.read_queryfile(queryfile)
    print(len(queries), ' Queries read!')

    print('All set!')
    starttime = datetime.now()
    print('Starting query processing at ', starttime,'!', sep = '')

    results = process_queries(index, queries)

    endtime = datetime.now()
    print('Finishes at ', endtime,'!', sep = '')
    print('Total time: ', endtime - starttime)

    print('MEAN P@10:', sum(results['precision'])/len(results['precision']))
    print('MAP:', sum(results['avp'])/len(results['avp']))

def process_queries(index, queries):
    results = dict()
    results['precision'] = list()
    results['avp'] = list()
    for qindex, query in enumerate(queries):
        qid = query[0]
        querystring = query[1]
        relevants = query[3]
        sys.stdout.write("\r\033[K")
        print('\rProcessing query: %d/%d (%2.2f%%)' % (qindex+1, len(queries), (qindex+1)/len(queries)*100), end ='')
        rank = index.simple_query(querystring)
        #print('query:', qid, 'rank:', rank)
        queryresult = [res[0] for res in rank]
        p = precision(queryresult, relevants, topn = 10)
        a = averagePrecision(queryresult, relevants)
        results['precision'].append(p)
        results['avp'].append(a)

    return results

def averagePrecision(queryresult, relevants):
    relevance = map_relevant(queryresult, relevants)
    aVPsum = 0.0
    
    cutrelevants = relevance[:len(relevance) - [rel[1] for rel in relevance][::-1].index(True)]
    for k, resTuple in enumerate(cutrelevants):
        aVPsum += precision(queryresult, relevants, k+1) * resTuple[1]

    aVP = aVPsum/len(relevants)
    return aVP

#def cut_relevants(relevance):
#    len(relevance) - (rel[1] for rel in relevance)[::-1].index(True)]

def precision(queryresult, relevants, topn = 10):
    topnlist = queryresult[:topn]
    relevance = map_relevant(topnlist, relevants)

    p = len([doc[1] for doc in relevance if doc[1]])/len(topnlist)

    return p

def recall(queryresult, relevants, topn = 10):
    topnlist = queryresult[:topn]
    relevance = map_relevant(topnlist, relevants)

    r = len([doc[1] for doc in relevance if doc[1]])/len(relevants)

    return r

def map_relevant(queryresult, relevants):
    return [(doc, doc in relevants) for doc in queryresult]

def list_cfcdir(cfcdirectory):
    fulllist = os.listdir(cfcdirectory)
    indexlist = [fname for fname in fulllist if fname.split('.')[-1] == 'index']
    if len(indexlist) > 1:
        raise Exception('More than one index file where found: $s', ', '.join(indexlist))
    if indexlist:
        indexfile = indexlist[0]
    else:
        indexfile = None

    cfclist = [fname for fname in fulllist if len(fname.split('cf',1)) > 1 and fname.split('cf',1)[1].isnumeric()]
    if len(cfclist) == 0:
        raise Exception('No CFC doc file founds!')
    return cfclist, indexfile,

class CFCIndex (indexing.Index):
    '''
'''
    def __init__(self,):
        indexing.Index.__init__(self)

    def prepare_weight(self):

        for term in self:
            for docterm in self[term].doclist:
                docterm.weight = docterm.doctf * self[term].idf
                self.doc[docterm.doc][0] += docterm.weight**2

        for doc in self.doc:
            #self.doc[doc]
            #0 = doc len
            #1 = norma
            self.doc[doc][1] = math.sqrt(self.doc[doc][0])

    def simple_query(self, query):
        '''
    '''
        termslist = query.split()
        acc_dict = {}
        qweight, qnorma = self.get_query_weight(query)

        for term in termslist:
            if self.get(term):
                for doc in self[term].doclist:
                    if not acc_dict.get(doc.doc):
                        acc_dict[doc.doc] = 0.0
                    acc_dict[doc.doc] += doc.weight * self[term].idf * qweight[term]
                    #print(doc.weight * self[term].idf)

        for doc in acc_dict:
            acc_dict[doc] = acc_dict[doc] / (self.doc[doc][1]*qnorma)

        rank = sorted(acc_dict.items(), reverse = True, key = lambda x : x[1])

        return rank

    def get_query_weight(self, query):
        termslist = query.split()
        qtf = dict(collections.Counter(termslist))
        qweight = dict()
        for term in termslist:
            if self.get(term):
                qweight[term] = qtf[term] * self[term].idf
        qnorma = math.sqrt(sum((value**2 for value in qweight.values())))
        return qweight, qnorma

#    def partial_weight(self, term, doc):
#        pweigth = doc.weight * term.idf
#        
#        return partial_scr

if __name__ == '__main__':
    sys.exit(main())
