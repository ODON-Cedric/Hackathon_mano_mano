import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import time



df = pd.read_csv(r'C:\Users\Administrateur\Desktop\hack2\hackathon.csv', sep=",", low_memory=False)
df.drop("Unnamed: 0", axis=1, inplace=True)


# provider -> ABCD (FR)
# provider2 -> ABCD
# provider_country -> FR
def provider_country(x):
    try:
        return str(x).split('(')[1].replace(")","")
    except :
        return ""

df["provider_country"] = df["provider"].apply(provider_country)
df["provider2"] = df["provider"].apply(lambda x: str(x).split(' (')[0])
df_provider = df[["provider2", "provider_country", "score", 'shipping_fees', 'bv_transaction']].copy()
df_provider["provider"] = df_provider["provider2"].apply(lambda x: str(x).strip())
df_provider.drop("provider2", axis=1, inplace=True)


df_mean = df_provider.groupby("provider").mean().copy()
df_mean.rename(columns={'score': 'score_mean','shipping_fees':'shipping_fees_mean', 'bv_transaction':'bv_transaction_mean'}, inplace=True)

df_sum = df_provider.groupby("provider").sum().copy()
df_sum.rename(columns={'shipping_fees':'shipping_fees_sum', 'bv_transaction':'bv_transaction_sum'}, inplace=True)

df_final = pd.merge(df_mean, df_sum, how="left", left_on=df_mean.index, 
                    right_on=df_sum.index)


def score_score(x):
    q1 = df_final.score_mean.describe().to_list()[4]
    q2 = df_final.score_mean.describe().to_list()[5]
    q3 = df_final.score_mean.describe().to_list()[6]
    if x < q1 :
        return 1
    if q1 <= x < q2:
        return 2
    if q2 <= x < q3:
        return 3
    if q3 >= 9.4 :
        return 4

def score_ship(x):
    q1 = df_final.shipping_fees_mean.describe().to_list()[4]
    q2 = df_final.shipping_fees_mean.describe().to_list()[5]
    q3 = df_final.shipping_fees_mean.describe().to_list()[6]
    if x >= q3 :
        return 1
    if q3 > x >= q2:
        return 2
    if  q2 > x > q1:
        return 3
    if x <= q1 :
        return 4

def score_transac_mean(x):
    q1 = df_final.bv_transaction_mean.describe().to_list()[4]
    q2 = df_final.bv_transaction_mean.describe().to_list()[5]
    q3 = df_final.bv_transaction_mean.describe().to_list()[6]
    if x < q1 :
        return 1
    if q2 > x >= q1:
        return 2
    if  q3 > x >= q2:
        return 3
    if x >= q3 :
        return 4

def score_transac_sum(x):
    q1 = df_final.bv_transaction_sum.describe().to_list()[4]
    q2 = df_final.bv_transaction_sum.describe().to_list()[5]
    q3 = df_final.bv_transaction_sum.describe().to_list()[6]
    if x < q1  :
        return 1
    if q2 > x >= q1:
        return 2
    if  q3 > x >= q2:
        return 3
    if x >= q3 :
        return 4

def note(x):
    q1 = df_final.score_total.describe().to_list()[4]
    q2 = df_final.score_total.describe().to_list()[5]
    q3 = df_final.score_total.describe().to_list()[6]
    if x <= q1:
        return "D"
    if q2 >= x > q1:
        return "C"
    if q3 >= x > q2:
        return "B"
    if x > q3:
        return 'A'
    
def full_note(x):
    x["score_score"] = x["score_mean"].apply(score_score)
    x["score_ship"] = x["shipping_fees_mean"].apply(score_ship)
    x["score_transac_mean"] = x["bv_transaction_mean"].apply(score_transac_mean)
    x["score_transac_sum"] = x["bv_transaction_sum"].apply(score_transac_sum)
    x["score_total"] = x["score_score"] + x["score_ship"] + x["score_transac_mean"] + x["score_transac_sum"]
    x["note"] = x["score_total"].apply(note)
    return x
  
df_score_final = full_note(df_final)
df_score_final.rename(columns={"key_0":'provider'}, inplace=True)




# CSV DE CEDRIC, je le met dans manomano hackathon, mais j'ai pas le code pour le créer
df_review = pd.read_csv(r'C:\Users\Administrateur\Desktop\hack2\df_provider.csv', sep=",")
df_review.drop("Unnamed: 0", axis=1, inplace=True)


df_review["score"] = df_review["score"].apply(lambda x: float(x.replace(",", ".")))
df_review_2 = df_review[df_review["score"] > 0].copy()



df_note = pd.merge(df_score_final, df_review_2, how="left", left_on="provider", right_on="provider")
df["provider_country"] = df["provider"].apply(provider_country)
df["provider2"] = df["provider"].apply(lambda x: str(x).split(' (')[0])
df_provider = df[["provider2", "provider_country", "score", 'shipping_fees', 'bv_transaction', 'nb_articles',
                 'comment']].copy()
df_provider["provider"] = df_provider["provider2"].apply(lambda x: str(x).strip())
df_provider.drop("provider2", axis=1, inplace=True)

df_comment_count = df_provider.groupby("provider").count()["comment"].copy()
df_nbarticles = df_provider.groupby("provider").sum()["nb_articles"].copy()


df_note = pd.merge(df_note, df_comment_count, how="left", left_on="provider", right_on=df_comment_count.index)
df_note = pd.merge(df_note, df_nbarticles, how="left", left_on="provider", right_on=df_nbarticles.index)

df_note.rename(columns={"comment" : "comment_count"}, inplace=True)
df_note.rename(columns={'score_y' : 'score_trustpilot'}, inplace=True)


df_note["score_trustpilot"] = df_note["score_trustpilot"].apply(lambda x: x*2)
df_note["score_10"] = df_note["score_total"].apply(lambda x: x/1.6)

df_note_final = df_note[["provider", "score_mean", "shipping_fees_mean", "bv_transaction_mean", "shipping_fees_sum", 
                         "bv_transaction_sum", "comment_count", "nb_articles", "provider_site", "note", "score_10",
                        "score_trustpilot"]].copy()
df_ultime = df_note_final[df_note_final.score_trustpilot.notnull()].copy()
df_ultime["diff"] = df_ultime["score_10"] - df_ultime["score_trustpilot"]


    ### SCRAPING NB REVIEWS TRUSTPILOT
def reviewnb(x):
        url = str(x)
        navigator = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
        result = requests.get(url, headers={'User-Agent': navigator})
        soup = BeautifulSoup(result.text, "html.parser")
        review = soup.find_all("span", {'class':"typography_typography__QgicV typography_bodysmall__irytL typography_color-gray-7__9Ut3K typography_weight-regular__TWEnf typography_fontstyle-normal__kHyN3 styles_text__W4hWi"})
        nb_rev=[]
        for item in review :
            y = item.text
            y = y.replace("\xa0  •  \xa0", "")
            for item in list(y):
                if item.isdigit() == True:
                    nb_rev.append(item)
        return "".join(nb_rev)
    
df_ultime["nb_reviews_trustpilot"] = df_ultime["provider_site"].apply(reviewnb)
df_vraiment_ultime = df_ultime[df_ultime["diff"] < 0].copy()    

df_vraiment_ultime.drop("shipping_fees_sum", axis=1, inplace=True)
df_vraiment_ultime.rename(columns={"provider":"Provider",
                                  "score_mean":"score_mean_MM",
                                  "comment_count" : "nb_comment_MM",
                                  "provider_site" : "provider_trustpilot_url",
                                  "note" : "provider_note",
                                  "score_10" : "provider_score",
                                  "diff" : "diff_MM_TP"}, inplace=True)



df_cellelacestlabonne = df_vraiment_ultime[["Provider","provider_note", 
                                          "provider_score",'score_trustpilot', 
                                          'diff_MM_TP','nb_reviews_trustpilot', 'provider_trustpilot_url',
                                          'nb_articles', 'nb_comment_MM','score_mean_MM', 
                                          'shipping_fees_mean','bv_transaction_mean', 'bv_transaction_sum'
                                         ]].copy()
