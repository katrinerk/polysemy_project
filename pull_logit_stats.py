import statsmodels.stats.stattools as st
import statsmodels.api as sm
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from polysemy_visualization import compute_embeddings_for
import sys

#helper funcs will need em later

def get_pairs(num):
    pairs = []
    for x in range(num):
        for y in range(x, num):
            if x!=y:
                pairs.append((x,y))
    return pairs

def load_df(inputfilename):
    df = pd.read_csv(inputfilename)
    modeltype = 'bert-base-uncased'
    #until i resolve all parsing issues, do not use a case sensitive model, and leave this following line uncommented:
    df['sent'] = df['sent'].apply(str.lower)
    verb_embeddings = compute_embeddings_for(df, what = "tgt", modeltype = modeltype)
    subj_embeddings = compute_embeddings_for(df, what = "subj", modeltype = modeltype)
    obj_embeddings = compute_embeddings_for(df, what = "dobj", modeltype = modeltype)
    df['verb_embedding'] = list(np.array(verb_embeddings))
    df['subj_embedding']= list(np.array(subj_embeddings))
    df['dobj_embedding'] = list(np.array(obj_embeddings))
    return df

def form_comparison_df(df):
    pairs = get_pairs(len(df))
    rows = []
    for (x,y) in pairs:
        xrow = df.iloc[x]
        yrow = df.iloc[y]
        obj_sim = cosine_similarity(xrow['dobj_embedding'].reshape(1,-1), yrow['dobj_embedding'].reshape(1,-1))[0][0]
        subj_sim = cosine_similarity(xrow['subj_embedding'].reshape(1,-1), yrow['subj_embedding'].reshape(1,-1))[0][0]
        tgt_sim = cosine_similarity(xrow['verb_embedding'].reshape(1,-1), yrow['verb_embedding'].reshape(1,-1))[0][0]
        row = {"pair": (x,y), "sent1": xrow['sent'], "sent2": yrow["sent"], "obj_similarity": obj_sim, "verb_similarity": tgt_sim, "subj_similarity": subj_sim}
        rows.append(row)
    pairwise_df = pd.DataFrame(rows)
    return pairwise_df

def stats_as_dict(df, subj=True):
    if subj: x = df["subj_similarity"]
    else: x = df["obj_similarity"]
    y = df["verb_similarity"]
    x = sm.add_constant(x)
    model = sm.OLS(y, x)
    results = model.fit()
    rsq = results.rsquared
    slope = results.params.iloc[1]
    pval = results.pvalues.iloc[1]
    pomni = st.omni_normtest(results.resid)[1]
    jb = st.jarque_bera(results.resid)[0]
    aic = results.aic
    return {"rsq": rsq, "slope": slope, "pval": pval, "pomni": pomni, "jb": jb, "aic": aic}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please pass filename")
    else:
        filename = sys.argv[1]
        df = load_df(filename)
        df = form_comparison_df(df)
        print("for subj", stats_as_dict(df))
        print("for obj", stats_as_dict(df, subj=False))
        #leaving it like this for now
        #will eventually have it create csv, each of these dicts as a row, just want to know the desired structure first