import pandas as pd
import random

all_words = pd.read_csv("https://github.com/dwyl/english-words/raw/master/words_alpha.txt",header=None).dropna()[0]


# Parameters
N_generated_words = 3
N_words = 5000

words = [w for w in all_words.values if len(w)==5][:]
random.shuffle(words)

words = words[:N_words]


abc = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

d = {}
d_ = {}
for i,w in enumerate(abc):
    d[w]=i
    d_[i]=w
    
def word_to_numb(word):
    word_numb = [[0 for i in range(5)] for _ in range(len(abc))]
    for j,w in enumerate(word):
        word_numb[d[w]][j] = 1
    return word_numb
word_to_numb("joan")
    
from ortools.sat.python import cp_model

model = cp_model.CpModel()

# Creates the variables.
# The array index is the column, and the value is the row.

chosen_word_var = {}
for k in range(N_generated_words):
    for w in range(len(words)):
        chosen_word_var[k,w] = model.NewBoolVar('word_{}_{}'.format(k,w)) 


word_var={}  
for k in range(N_generated_words):
    for i in range(5):
        for j in range(len(abc)):    
            word_var[k,i,j] = model.NewBoolVar("w_{}_{}_{}".format(k,i,j))


#define a word
for k in range(N_generated_words):
    for j in range(len(abc)):
        model.Add( sum(word_var[k,i,j] for i in range(5)) <= 1 )

#if word i is chosen: then variable must be the same as chosen word
for k in range(N_generated_words):
    for w in range(len(words)):
        for i in range(5):
            for j in range(len(abc)):   
                model.Add( word_var[k,i,j] == word_to_numb(words[w])[j][i]).OnlyEnforceIf(chosen_word_var[k,w])
             
#choose one word
for k in range(N_generated_words):
    model.Add( sum(chosen_word_var[k,w] for w in range(len(words))) == 1 )
    
#Cannot repeat a letter
for j in range(len(abc)):
    model.Add( sum(word_var[k,i,j] for k in range(N_generated_words) for i in range(5)) <=1 )

            
             
solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = False
status = solver.Solve(model)

print(status==cp_model.OPTIMAL)

result_words_index = []
for k in range(N_generated_words):
    for i in range(len(words)):
        if solver.Value(chosen_word_var[k,i])==1:
            result_words_index.append(i)
            print(k, words[i])
            
        

for k in range(N_generated_words):
    result_word = ""        
    for i in range(5):
        for j in range(len(abc)):    
            if solver.Value(word_var[k,i,j])==1:
                result_word+=d_[j]
    print(k,": ",result_word)


