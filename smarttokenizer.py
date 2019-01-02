import re
from ufal.udpipe import Model, Pipeline, ProcessingError
import pandas as pd
import conllformat

model = Model.load('G:/Softwares/urdu-udtb-ud-2.3-181115.udpipe')
pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
error = ProcessingError()

def smarttokenizer(sentence):    
    namelist= []

    #text = '1934ء میں موہن داس گاندھی پونے میں اپنی اہلیہ کستوربا گاندھی کے ساتھ پونے آئے۔'
    processed = pipeline.process(sentence, error)
    processed_lines = [s for s in str(processed).split(sep="\n") if not s.startswith('#') and not s.strip() == '']

    pname = ''
    nname = ''
    i = 1
    for l in processed_lines:      
        #print(l)
        dic = conll.format.get_dict(l)
        if (dic["pos"] == 'PROPN' or dic["pos"] == 'NOUN'): 
            pname += dic["word"] + ' '
        elif pname != "":
            namelist.append(pname.strip())
            pname = ''
            namelist.append(dic["word"])
        else:
            namelist.append(dic["word"])        
    
        if len(processed_lines) == i and pname != "":
            namelist.append(pname.strip())
            pname = ''                       
            
        i = i +1
                    
    return namelist;