import spacy
import sys 
import pandas as pd
import copy
import get_subj_and_obj as gso

def get_dependency(token, dep):
    return [child for child in token.children if child.dep_ == dep]

def filtered(dir, word): 
    df_init = {"tgt":[], "subj":[], "dobj":[], "sent":[],"meta_file":[], "meta_indices":[] }
    spacy_obj = spacy.load('en_core_web_sm')
    data = pd.DataFrame(copy.deepcopy(df_init))
    currRow = {}
    with open(dir) as f:
        for line in f:
            if line.strip().startswith("#"):
                metadata = line.split(sep=" ")
                if len(metadata) != 5:
                    continue
                currRow =copy.deepcopy(df_init)
                currRow["tgt"].append(metadata[4].removesuffix("\n"))
                currRow["meta_file"].append(metadata[1])
                currRow["meta_indices"].append((metadata[2], metadata[3]))
            else:
                analysis = spacy_obj(line)
                if (len(currRow["sent"])==1):
                    currRow["sent"][0]+=line
                else: currRow["sent"].append(line)
                # now using tomas' parsing functions
                for token in analysis:
                    if token.pos_ == "VERB" and token.lemma_ == word:
                        currRow["tgt"] = [token.text]
                        subj = gso.get_subject(token)
                        dobj = gso.get_direct_object(token)
                        if subj:
                            currRow["subj"].append(subj.lemma_)
                        if dobj:
                            currRow["dobj"].append(dobj.lemma_)
                        # if token.dep_ == "dobj": 
                        #     currRow["dobj"].append(token.lemma_)
                        # if token.dep_ == "nsubj":
                        #     currRow["subj"].append(token.lemma_)
                if len(currRow["dobj"]) ==1 and len(currRow["subj"]) == 1: 
                    row = pd.DataFrame(currRow)
                    data = pd.concat([data,row], ignore_index=True)
    data.to_csv(f"csvs/{word}.csv") #if you don't want a separate csvs folder remove the csvs/
    print(len(data), "occurrences with subj obj")
                
        

if __name__ == "__main__":
    if len(sys.argv) == 2:
        word = sys.argv[1].removesuffix(".txt").removeprefix("texts/")
        #my file structure has a texts folders for the files but you can remove that last bit if they are in the same directory
        filtered(sys.argv[1], word)