# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import sys
import os

import indexing

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
    #Se existe index
        #load index
    #Else
        #Load File
        #create index
    #load_queries
    #process queries
    #doc_dict = cfc_tools.read_docfile('cfcexemplos/cfcexemplo3')
    #cfc_tools.print_doc_dict(doc_dict)

    queries = cfc_tools.read_queryfile(queryfile)

    #index = CFCIndex()

    #index.add_docstf(doc_dict)
    #print(index.avgdl)
    #cfc_tools.print_idf(index)

class CFCIndex (indexing.Index):
    '''
'''
    def __init__(self,):
        indexing.Index.__init__(self)

if __name__ == '__main__':
    sys.exit(main())
