from __future__ import unicode_literals
import re
from ufal.udpipe import Model, Pipeline, ProcessingError
import pandas as pd 
from conllu import parse

model = Model.load('G:/Softwares/urdu-udtb-ud-2.3-181115.udpipe')
pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
error = ProcessingError()

# -*- coding: utf-8 -*-
STOP_WORDS = """
 ابھی از 
 اس استعمال اسی اسے البتہ الف ان اندر اور اوپر اکثر اگر
 اگرچہ اگلے ایسا ایسی ایسے اے بار بارے باوجود باہر بظاہر بعض بغیر بلکہ بن
 بھر بھریں بھی بہت بے تا تاکہ تب تحت تر تمام
 تو تک جب سوال 
 جبکہ جو حالانکہ حالاں خلاف
 خود سے میں چنانچہ دیر ذریعے تھا هے ایک آپ
 سا ساتھ سامنے سب تھی تھے
 سکا سکتا سکتے سی سے شان شاید صرف صورت ضرورت ضروری طرح طرف طور علاوہ عین غیر 
 لہذا لیکن لیں لیے لے مجھ مجھے مزید مقابلے مل مکمل مگر 
 نا نہ نہیں نیچے واقعی والا والوں والی والے وجہ وغیرہ وہ وہاں وہی وہیں وی ویسے پاس
 پایا پر پوری پھر پیچھے چونکہ چکی
 ڈالے کئے کافی کبھی کسی کم 
 کوئی کچھ کہ کہا کہہ کہیں کہے کیونکہ کیے کے گئی
 گئے گا گویا گی گے ہاں ہر ہمیشہ ہو ہوئی ہوئیں ہوئے ہوا ہوتا
 ہوتی ہوتیں ہوتے ہونا ہونگے ہونی ہونے ہوں ہی ہیں ہے یا یات یعنی یقینا یہ یہاں یہی یہیں ھیں
  حضرت ہوگی رض
 کا کو کی نے ہوتو پہلے کر
 اپنا حتى كہ ميں لئیے  
 بعد ارادہ افاقہ آخر
""".split()

print('loading w2v...')
from gensim.models import word2vec
import gensim
model = gensim.models.KeyedVectors.load_word2vec_format('urduvec_140M_100K_300d.bin', binary=True)

import pyodbc
from gensim.models import Word2Vec
import sys
import time
import numpy as np

no_of_docs_cache = {}
idf_cache = {}
term_freq_doc_cache = {}
print('loading dataset...')
conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=G:\Softwares\EQWH-V6.4-190407\EasyHadees - Copy.mdb;')
cursor = conn.cursor()
cursor.execute("select id, urdutext from ahadith where urdutext is not null and urdutext like '%وضو%'")

# and urdutext like '%وضو%'

Y = []
corpus = []
lens_of_d= []
for row in cursor.fetchall():
    hadith = row[1]#.replace('صلی اللہ علیہ وآلہ وسلم','')    
    corpus.append(hadith)
    lens_of_d.append(len(hadith.split()))
    Y.append(row[0])
cursor.close()
conn.close()

avg_docs_len = np.mean(lens_of_d, axis=0)

print('generating bag of words...')
#from sklearn.feature_extraction.text import TfidfVectorizer as vectorizer
from sklearn.feature_extraction.text import CountVectorizer

vec = CountVectorizer(stop_words=STOP_WORDS).fit(corpus)
bag_of_words = vec.transform(corpus)
vocab = vec.vocabulary_.items()


def term_freq_doc(myword,doc_index):
    if myword not in vec.vocabulary_:
        return 0
    
    qindex = vec.vocabulary_[myword]
    sm = None
    if doc_index in term_freq_doc_cache:
        sm = term_freq_doc_cache[doc_index]
    else:
        #sm = bag_of_words[doc_index].sum(axis=0)
        sm = bag_of_words[doc_index].toarray()[0]
        term_freq_doc_cache[doc_index] = sm
    freq = sm[qindex]
    return freq


def no_of_docs(q):
    if q in no_of_docs_cache:
        return no_of_docs_cache[q]
    
    if q not in vec.vocabulary_:
        return 0
    
    qindex = vec.vocabulary_[q]
    
    no_of_ds = 0
    
    for bw in bag_of_words:
        if bw[0][0, qindex] > 0:
            no_of_ds += 1
    
    no_of_docs_cache[q] = no_of_ds;
    return no_of_ds    

import math

def idf(q):
    if q in idf_cache:
        return idf_cache[q]
    
    nq = no_of_docs(q)
    ans = math.log10(  (len(Y)- nq + 0.5) / (nq+ 0.5)  )
    idf_cache[q] = ans;
    return ans

def bm25_score(qwords,doc_index):
    score = 0;
    for qw in qwords:
        #start = time.time()
        tfd = term_freq_doc(qw, doc_index)
        score += idf(qw) * ( (tfd * (1.2 + 1))/ (tfd + 1.2 * (1-0.75 + 0.75 * (lens_of_d[doc_index] / avg_docs_len))) + 1.0)
        #end = time.time()
        #print(" time taken: "+str(end - start)+ ", for word: " + qw + ", for doc: " + str(doc_index))
    return score

from IPython.display import Markdown, display
def printmd(string):
    display(Markdown(string))
    
def getanswer(question,strict=False,pagesize=10):
    try:

        question_arr = question.split()

        query_words = []

        for qs in question_arr:
            query_words.append(qs)

        if strict == False:
            for question_word in question_arr:
                alltop = model.most_similar(positive=question_word, topn=20)
                for key, val in [item for item in alltop if item[1] > 0.51 and item[0] in vec.vocabulary_]:
                    query_words.append(key)

        doc_scores = []
        for i in range(0, len(Y)):
            start = time.time()
            score = bm25_score(query_words, i)
            end = time.time()
            #print(" time taken: "+str(end - start)+ ", for doc: " + str(i))
            doc_scores.append({'docid':i, 'score': score})

        doc_scores = sorted(doc_scores, key = lambda i: i['score'],reverse=True) 

        hadiths = []
        for i in range(0,pagesize):
            hadiths.append(corpus[doc_scores[i]['docid']])
            #printmd(""+corpus[doc_scores[i]['docid']]+'')
            #print()
        return hadiths
        
    except Exception as e:
        return [str(e)]
    
print('finished loading qa system.')

#question = 'آپ کس طرح وضو کرتے تھے'
question = 'وضو کس طرح ٹوٹتا ہے'
##question = 'وضو کس طرح کریں'
##question = 'وضو کا کیا طریقہ ہے'
#question = 'استنجا کیسے کریں'

getanswer(question, strict=False)