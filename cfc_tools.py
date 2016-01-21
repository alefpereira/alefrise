# -*- coding: utf-8 -*-
import string
import collections
import porter

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

def read_docfile(fname):
    """
"""
    with open(fname, 'r') as ftoindex:
        data = ftoindex.readlines()

        doc_dict = dict()

        current_field = ''
        nline = 0
        while(nline < len(data)):
            line = data[nline]
            if line.strip():
                field, content = line.split(' ', 1)

                #Read Record Number
                if(field == 'RN'):
                    rn = int(content.strip())

                    #Pass AN and Read Author(s)
                    nline+=2
                    line = data[nline]
                    field, content = line.split(' ', 1)
                    au = remove_multiple_space(replace_punctuation(content)).strip()

                    #Read Title
                    nline+=1
                    buff = ''
                    line = data[nline]
                    field, content = line.split(' ', 1)
                    while(field != 'SO'):
                        buff += content

                        nline+=1
                        line = data[nline]
                        field, content = line.split(' ', 1)

                    ti = remove_multiple_space(replace_punctuation(buff)).strip()

                    #Pass Source
                    while field != 'MJ':
                        nline+=1
                        line = data[nline]
                        field, content = line.split(' ', 1)

                    #Read Major Subject
                    buff = ''
                    while(field != 'MN'):
                        buff += content

                        nline+=1
                        line = data[nline]
                        field, content = line.split(' ', 1)

                    mn = remove_multiple_space(replace_punctuation(buff)).strip()

                    #Read Minor Subject
                    buff = ''
                    while(field != 'AB'):
                        buff += content

                        nline+=1
                        line = data[nline]
                        field, content = line.split(' ', 1)

                    mj = remove_multiple_space(replace_punctuation(buff)).strip()

                    #Abstract Minor Subject
                    buff = ''
                    while(field != 'RF'):
                        buff += content

                        nline+=1
                        line = data[nline]
                        field, content = line.split(' ', 1)

                    ab = remove_multiple_space(replace_punctuation(buff)).strip()

                    doc_string = " ".join([au, ti, mn, mj, ab]).lower()
                    termslist = doc_string.split()
                    apply_stem(termslist)
                    doc_dict[rn] = (rn, len(doc_string.split()), calc_doctf(termslist))

            nline+=1

    doctf_dict = dict()

    for rn in doc_dict:
        print(doc_dict[rn])

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
                    print(qn)

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
