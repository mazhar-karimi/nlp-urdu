

from ufal.udpipe import Model, Pipeline, ProcessingError
model = Model.load('G:/Softwares/urdu-udtb-ud-2.3-181115.udpipe')
pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
error = ProcessingError()

def get_dict(str):
    word_meta = str.split('\t')
    word_dic = {'id':word_meta[0], 'word' : word_meta[1], 'lemma' : word_meta[2], 'pos': word_meta[3], 'upos': word_meta[4], 'depends': word_meta[6], 'case': word_meta[7]}
    return word_dic

def getwordsinconll(sentence):    
    namelist= []
    
    processed = pipeline.process(sentence, error)
    processed_lines = [s for s in str(processed).split(sep="\n") if not s.startswith('#') and not s.strip() == '']
    
    for l in processed_lines:      
        #print(l)
        namelist.append(get_dict(l))        
    return namelist;