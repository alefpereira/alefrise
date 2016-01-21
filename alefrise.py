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


    cfclist, indexfile = list_cfcdir(cfcdirectory)

    if indexfile:
        print('Index file', indexfile, 'found!')
        index = cfc_tools.load_index(cfcdirectory + os.sep + indexfile)
    else:
        #Load File
        index = CFCIndex()
        for cfcfile in cfclist:
            print('Opening', cfcdirectory + os.sep + cfcfile)
            doc_dict = cfc_tools.read_docfile(cfcdirectory + os.sep + cfcfile)
            index.add_docstf(doc_dict)
        cfc_tools.save_index(index, cfcdirectory + os.sep + 'cfc.index')

    queries = cfc_tools.read_queryfile(queryfile)

    #TODO Avaliação

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

if __name__ == '__main__':
    sys.exit(main())
