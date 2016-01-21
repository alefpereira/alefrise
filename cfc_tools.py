# -*- coding: utf-8 -*-
import string
import collections
import porter

import pickle

replace_dictionary = str.maketrans(string.punctuation+'\n', ' '*len(string.punctuation+'\n'))
def replace_punctuation(text):
    """replace_punctuation(text, replace_dictionary):
"""
    global replace_dictionary
    return text.translate(replace_dictionary)

def replace_chars(text, charstoreplace, replacer = ' '):
    """replace_chars(text, charstoreplace, replacer = ' '):
"""
    rp = string.maketrans(charstoreplace, replacer*len(charstoreplace))
    return text.translate(rp)

def remove_multiple_space(text):
    '''Description
'''
    return " "+" ".join(text.split())+" "

def get_field(data, linestart):
    #Read first line
    nline = linestart
    line = data[nline]
    try:
        field, content = line.split(' ', 1)
    except ValueError:
        raise ValueError('Not possible to extract the field from string: ', line, ' in line: ', nline+1, sep = '')
    buff = content
    nline+=1
    line = data[nline]
    stripedline = line.rstrip()
    while(stripedline != '' and stripedline[0] == ' '):
        buff += stripedline

        nline+=1
        line = data[nline]
        stripedline = line.rstrip()

    return buff, nline

def search(fields, data, linestart):
    nline = linestart
    while (nline < len(data)):
        line =  data[nline]
        stripedline = line.rstrip()
        if stripedline != '' and stripedline.split(' ', 1)[0] in fields:
            break
        nline += 1
    return nline

def read_docfile(fname):

    with open(fname, 'r', encoding = 'ISO-8859-1') as ftoindex:
        data = ftoindex.readlines()

    doc_dict = dict()

    nline = 0
    while(nline < len(data)):
        line = data[nline]
        if line.strip():
            try:
                field, content = line.split(' ', 1)
            except Exception:
                print('File:', fname)
                print('Content:', line)
                raise


            if field == 'RN':
                try:

                    #Read Record Number 'RN'
                    rnstring, nline = get_field(data, nline)
                    #print('RN', rnstring)
                    #Read Author(s)
                    nline = search(['AU'], data, nline)
                    austring, nline = get_field(data, nline)
                    #print('AU', austring)
                    #Read Title
                    nline = search(['TI'], data, nline)
                    tistring, nline = get_field(data, nline)
                    #print('TI', tistring)
                    #Read Major Subject
                    nline = search('MJ', data, nline)
                    mjstring, nline = get_field(data, nline)
                    #print('MJ', mjstring)
                    #Read Minor Subject
                    nline = search('MN', data, nline)
                    mnstring, nline = get_field(data, nline)
                    #print('MN', mnstring)
                    #Abstract Minor Subject
                    nline = search(['AB', 'EX'], data, nline)
                    abstring, nline = get_field(data, nline)
                    #print('AB:', abstring)
                    nline = search('PN', data, nline)
                    #nline =- 1

                    rn = int(rnstring.strip())
                    au = remove_multiple_space(replace_punctuation(austring)).strip()
                    ti = remove_multiple_space(replace_punctuation(tistring)).strip()
                    mn = remove_multiple_space(replace_punctuation(mnstring)).strip()
                    mj = remove_multiple_space(replace_punctuation(mjstring)).strip()
                    ab = remove_multiple_space(replace_punctuation(abstring)).strip()

                    doc_string = " ".join([au, ti, mn, mj, ab]).lower()
                    termslist = doc_string.split()
                    apply_stem(termslist)
                    doc_dict[rn] = (rn, len(doc_string.split()), calc_doctf(termslist))
                except Exception:
                    print('fname', fname,'linha:(', nline,')', line)
                    raise
        nline += 1
    return doc_dict

def read_queryfile(fname):
    """
"""
    with open(fname, 'r') as ftoindex:
        data = ftoindex.readlines()

        queries = list()

        current_field = ''
        nline = 0
        while(nline < len(data)):
            line = data[nline]
            if line.strip():
                field, content = line.split(' ', 1)

                #Read Record Number
                if(field == 'QN'):
                    qn = int(content.strip())

                    #Read Query String [QU]
                    nline+=1
                    buff = ''
                    line = data[nline]
                    field, content = line.split(' ', 1)
                    while(field != 'NR'):
                        buff += content

                        nline+=1
                        line = data[nline]
                        field, content = line.split(' ', 1)

                    qu = remove_multiple_space(replace_punctuation(buff))

                    #Read Number of relevant documents [NR]
                    line = data[nline]
                    field, content = line.split(' ', 1)
                    nr = int(content.strip())

                    #Read Relevant docs
                    nline+=1
                    buff = ''
                    line = data[nline]
                    field, content = line.split(' ', 1)
                    while(field != 'QN'):
                        buff += content

                        nline+=1
                        line = data[nline]
                        if line == '\n' or nline + 1>= len(data): #Fix EOF AND EMPTY LINE ERROR
                            nline+=1
                            break
                        field, content = line.split(' ', 1)

                    rd_docstring = remove_multiple_space(replace_punctuation(buff))
                    rd = docstring_split(rd_docstring, 2, returned = lambda docS: docS[0])

                    queries.append((qn, qu, nr, rd,))

            #nline+=1

    return queries

docstring_split = lambda docstring, n, returned = lambda x: x: [returned(docstring.split()[i:i+n]) for i in range(0, len(docstring.split()), n)]

def print_idf(index):
    for term in index:
        print(term+':', index[term].idf)
        print(index[term].doclist)

def apply_stem(termslist):
    '''
'''
    for i, term in enumerate(termslist):
        termslist[i] = porter.stem(term)

#vocabulary = dict()

def print_doc_dict(doc_dict):
    '''
'''
    for rn in doc_dict:
        print(doc_dict[rn])

def calc_doctf(doc_stringlist):
    '''
'''
    return dict(collections.Counter(doc_stringlist))

def save_index(cfcindex, findexname):
    '''
'''
    with open(findexname, "wb") as index_file:
        pickle.dump(cfcindex, index_file)

def load_index(findexname):
    '''
'''
    with open(findexname, "rb") as index_file:
            cfcindex = pickle.load(index_file)
    return cfcindex
