# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import sys
import indexing

import itertools

import time

import pickle
import os

import lepref_util

DEBUG = False

TOPN = 40

maxtime = 0.0

if len(sys.argv) != 4:
    print('Python 2015')
    print('Uso: python3 bm25.py argv[1]')
    print('argv[1]: arquivo da base de dados')
    print('argv[2]: nome do arquivo onde serão salvos os dados')
    print('argv[3]: nome do arquivo onde serão salvos os resultados')
#    print('argv[x]:')
    sys.exit(-1)
else:
    dbname = sys.argv[1]
    fdataname = sys.argv[2]
    fresultname = sys.argv[3]

#Filters
filters = {
    'fil' :  {'name': 'filter', 'query': False, 'posproc': True},
    'and' :     {'name': 'and', 'query': True, 'posproc': True},
    'def' : {'name': 'default(or)', 'query': True, 'posproc': False}
}


def main():

    if os.path.exists(fdataname):
        print("Carregando dados do arquivo ", fdataname, '...',sep = '')
        queries, index = load_data(fdataname)

    else:
        #Obter dados de treino
        print("Lendo queries...")
        queries, lista_invertida = lepref_util.carregar_queries(sys.argv[1])
        print('Queries lidas:', len(queries))

        index = Bm25Index()

        print("Adicionando queries ao índice")
        index.generate_from_queries(queries)

        save_data(queries, index, fdataname)

    lepref_util.configurar_idcg_medio(queries, topN = TOPN)

###Evaluations
##Simple
#    print('MeanNDCG: ', evaluate(queries, index, topN = TOPN))
##Filters permutations
    doit = False
    if os.path.exists(fresultname):
        print("Arquivo ", fresultname, " de resultado encontrado!", sep = '')

        while (True):
            inputstring = input('Deseja calcular novamente?(N,y): ')
            if inputstring in ['Y','y']:
                doit = True
                break

            elif inputstring in ['N','n', '']:
                print('Saindo...')
                sys.exit()
            else:
                print('Opção <', inputstring, '> Invalida!', sep='')
    else:
        doit = True

#    print_idf(index)
    if doit:
        start_time = time.clock()
        print(time.strftime("Start at: %a, %d %b %Y %H:%M:%S", time.localtime()))
        results = evaluate_filters(queries, index, topN = TOPN)
        print(time.strftime("Ends at: %a, %d %b %Y %H:%M:%S", time.localtime()))
        print("--- %s seconds ---" % (time.clock() - start_time))

        save_results(results, fresultname)
        print('Docs lidos:', len(index.doc))
        print('AVGDL:', index.avgdl)
        print('Vocabulary Length:', len(index))

class Bm25Index (indexing.Index):
    '''
'''
    def __init__(self,):
        indexing.Index.__init__(self)

    def generate_from_queries(self, queries):
        '''
    '''
        for query in queries:

            for doc in query.doc:
                docid = doc.docid
                doclen = doc.lenbody

                self.doc[docid] = doclen

                for term in doc.term:
                    doctf = term.tfdocument
                    #if (doctf > 0):
                    try:
                        self.add_term_doctf(term.word, docid, doctf)
                    except KeyError:
                        self.add_term(term.word)
                        self.add_term_doctf(term.word, docid, doctf)

        doclensum = sum(self.doc.values())
        self.avgdl = doclensum/len(self.doc)

        self._update_idf()
        self._generate_doc_dict()

    def simple_query(self, query, topN = TOPN):
        '''
    '''
        termlist = query.split()
        acc_dict = {}

        for term in termlist:
            if self.get(term):
#                for doc in self[term].doclist:
#                    if not acc_dict.get(doc.doc):
#                        acc_dict[doc.doc] = 0
#                    acc_dict[doc.doc] += self.partial_score(self[term], doc)
                #maxtopn
                i = 0
                while i < len(self[term].doclist) and i < TOPN:
                    doc = self[term].doclist[i]
                    if not acc_dict.get(doc.doc):
                        acc_dict[doc.doc] = 0
                    acc_dict[doc.doc] += self.partial_score(self[term], doc)
                    i += 1

        rank = sorted(acc_dict.items(), reverse = True, key = lambda x : x[1])

        return rank

    def filters_query(self, query, termsfilters = None, topN = TOPN):
        '''
    '''
        termlist = query.split()
        if termsfilters:
            if len(termlist) != len(termsfilters):
                print('TermList:', termlist)
                print('TermsFilters:', termsfilters)
                raise(Exception("Número de parâmetros diferentes do número de termos"))
        else:
            termsfilters = ['default']*len(termlist)
        #filter process
        querylist = []
        posproclist = []
        for i, term in enumerate(termlist):

            termfilter = termsfilters[i]
            if filters[termfilter]['query']:
                querylist.append(term)

            if filters[termfilter]['posproc']:
                posproclist.append(term)

        #execute query
        prerank = self.simple_query(' '.join(querylist))

        #process pos query
        rank = []

#        for rankresult in prerank:
#            global maxtime
#            start_time = time.clock()

#            if self.doc_has_terms(rankresult[0], posproclist):
#                rank.append(rankresult)

#            difftime = (time.clock() - start_time)
#            if difftime > maxtime:
#                maxtime = difftime
        #maxtopn
        i = 0
        while i < len(prerank) and len(rank) < topN:
            rankresult = prerank[i]
            global maxtime
            start_time = time.clock()

            if self.doc_has_terms(rankresult[0], posproclist):
                rank.append(rankresult)

            difftime = (time.clock() - start_time)
            if difftime > maxtime:
                maxtime = difftime
            i += 1

        return rank

    def doc_has_terms(self, docid, termslist):
        '''
    '''
        for term in termslist:
            try:
                if not self[term].in_doc(docid):
                    return False
            except KeyError:
                return False
        return True

    def _generate_doc_dict(self):
        '''
    '''
        for term in self:
            #maxtopn
            self[term].doclist.sort(reverse = True, key = lambda doc : doc.score)

            self[term].docdict = {doc.doc: (doc.doctf, doc.score) for doc in self[term].doclist}

def print_idf(index):
    for term in index:
        print(term+':', index[term].idf, end =  ' ')
        print("Ndocs:", len(index[term].doclist))

def print_doc(term):
    for i, doc in enumerate(term.doclist):
        print(i+1, doc)

def print_termdoc(queries):
    for query in queries:
        print('Query id:', query.queryid)
        print('Termos')
        for term in query.term:
            print(term.word)
        for doc in query.doc:
            print(doc.docid)
            termlist = [term.word for term in doc.term]
            print(termlist)

#            doclist = [doc.docid for doc in query.doc]
#            print(doclist)

def debug(*args, **kargs):
    '''
'''
    if DEBUG:
        print(*args, **kargs)

def save_data(queries, index, fdataname):
    '''
'''
    data_buff = dict(queries = queries, index = index)
    with open(fdataname, "wb") as data_file:
        pickle.dump(data_buff, data_file)

def load_data(fdataname):
    '''
'''
    with open(fdataname, "rb") as data_file:
            data = pickle.load(data_file)
    return data['queries'], data['index']

def save_results(results, fresultname):
    '''
'''
    result_buff = dict(results = results)
    with open(fresultname, "wb") as result_file:
        pickle.dump(result_buff, result_file)

def load_results(fresultname):
    '''
'''
    with open(fresultname, "rb") as result_file:
            data = pickle.load(result_file)
    return data['results']

def obter_vetor_ganho(rank, query):
    '''Description
'''
    vetor_ganho = []
    for doc in rank:
        vetor_ganho.append(obter_doc_label(doc[0], query))
    return vetor_ganho

def obter_doc_label(doc, query):
    #XXX Funciona mas não é a melhor forma
    for qdoc in query.doc:
        if doc == qdoc.docid:
            return qdoc.label
    return 0

def evaluate(queries, index, topN = TOPN):
    acumulador_ndcg = 0.0
    for query in queries:
        #rank = efetuar consulta
        rank = index.simple_query(' '.join([term.word for term in query.term]))
        ##computados
        #vetor_ganho_consulta = obter_vetor_ganho(rank, queries)
        vetor_ganho_consulta = obter_vetor_ganho(rank, query)
        #ndcg_q = lepref_util.ndcg_unico(vetor_ganho, query.idcg, topN, chave = lambda e: e[0])
        if (len(query.idcg) != 40): #TODO remover
            print(len(query.idcg), query.queryid)
        ndcg_q = lepref_util.ndcg_unico(vetor_ganho_consulta, query.idcg, topN, chave = lambda e: e)
        #query.mean_ndcg_atual = lepref_util.ndcg_medio_unico(ndcg_q)
        query.mean_ndcg_atual = lepref_util.ndcg_medio_unico(ndcg_q)
        #acumulador_ndcg += query.mean_ndcg_atual
        acumulador_ndcg += query.mean_ndcg_atual

    return acumulador_ndcg/len(queries)

def evaluate_filters(queries, index, topN = TOPN):
    products = {}
    results = []
    for iq, query in enumerate(queries):
        termslist = [term.word for term in query.term]

        #create filterpergumation
        productslist = products.get(len(termslist))
        if (productslist == None):
            products[len(termslist)] = list(itertools.product(filters, repeat = len(termslist)))
            productslist = products[len(termslist)]

        productsresults = []
        for ic, filterproduct in enumerate(productslist):

            #Process tracker
            #(56%) 1541 of 5125 queries. Query 650 processing (34%) 14 of 59 filters...
            processq = (iq+1)/len(queries)*100
            processf = (ic+1)/len(productslist)*100
            print('(%2.2f%%) %d of %d queries. Query %d processing (%2.2f%%) %d of %d filters... [Max Time = %f]'
                % (processq, iq+1, len(queries), query.queryid, processf, ic+1, len(productslist), maxtime), end = '\r')

            #Evalue query
            rank = index.filters_query(' '.join(termslist), filterproduct)
            vetor_ganho_consulta = obter_vetor_ganho(rank, query)
            ndcg_q = lepref_util.ndcg_unico(vetor_ganho_consulta, query.idcg, topN, chave = lambda e: e)
            query.mean_ndcg_atual = lepref_util.ndcg_medio_unico(ndcg_q)

            #Add result to products results
            
            productsresults.append((filterproduct, query.mean_ndcg_atual))

        #Add query results to final results
        queryresult = (query.queryid, termslist, productsresults)
        results.append(queryresult)
    print('')
    return results

if __name__ == "__main__":
    main()
    #sys.exit(main())
