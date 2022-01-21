
import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly.offline import plot
import random
import numpy as np
from nltk.corpus import wordnet
import string
import nltk
from nltk import pos_tag
nltk.download('stopwords')
from nltk.tokenize import WhitespaceTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords



df = pd.read_csv(r'C:\Users\Administrateur\Desktop\hack2\df_uk_review.csv', sep=",")
df_mm = pd.read_csv(r'C:\Users\Administrateur\Desktop\hack2\hackathon.csv', sep=",", low_memory=False)
#df_uk = commentaires sur trustpilot
df_uk = pd.read_csv(r'C:\Users\Administrateur\Desktop\hack2\uk_com.csv', sep=",")


def get_wordnet_pos(pos_tag):
    if pos_tag.startswith('J'):
        return wordnet.ADJ
    elif pos_tag.startswith('V'):
        return wordnet.VERB
    elif pos_tag.startswith('N'):
        return wordnet.NOUN
    elif pos_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN
    
def clean_text(text):
    # lower text
    text = str(text).lower()
    # tokenize text and remove puncutation
    text = [word.strip(string.punctuation) for word in text.split(" ")]
    # remove words that contain numbers
    text = [word for word in text if not any(c.isdigit() for c in word)]
    # remove stop words
    stop = set(stopwords.words('english'))
    exclude_words = set(("not", "s", "no"))
    new_stop = stop.difference(exclude_words)
    text = [x for x in text if x not in new_stop]
    # remove empty tokens
    text = [t for t in text if len(t) > 0]
    # pos tag text
    pos_tags = pos_tag(text)
    # lemmatize text
    text = [WordNetLemmatizer().lemmatize(t[0], get_wordnet_pos(t[1])) for t in pos_tags]
    # remove words with only one letter
    text = [t for t in text if len(t) > 1]
    # join all
    text = " ".join(text)
    return(text)

# clean text data
df_mm["comment_clean"] = df_mm["comment"].apply(lambda x: clean_text(x))
df_uk["comment_clean"] = df_uk["review"].apply(lambda x: clean_text(x))

df_mm["comment_clean"] = df_mm["comment_clean"].apply(lambda x: np.NaN if x == "nan" else x)




df_comm = pd.concat([df_mm[df_mm["score"] < 7 & df_mm["comment_clean"].notnull()]["comment_clean"], df_uk["comment_clean"]])

df_commentaire = df_comm.to_frame()
df_hehe = df_commentaire.comment_clean.str.split(expand=True).stack().value_counts().rename_axis('unique_values').reset_index(name='counts')
df_hehehe = df_hehe[df_hehe["counts"] > 50].copy()




# keywords de cet aprem + trouvés sur un site qui référence les negatives keywords pour le ecommerce
keywords = ['chargeback', 'complaint', 'customer', 'email', 'emails', 'fraud', 'guarantee', 'guarantees',  
            'manual', 'manuals', 'negative', 'recall', 'recalls', 'refund', 'refunds', 'replace', 
            'replacement', 'return', 'returns', 'service', 'support', 'trouble',
            'troubleshooting', 'warranty', 'warranties', 'apart', 'broke', 'broken', 'burn', 'burned', 'burnt', 
            'care', 'caring', 'condition', 'crack', 'cracked', 'cracking', 'cut', 'deform', 'deformed', 'discolor', 
            'drop', 'dropped', 'fix', 'maintenance', 'odor', 'odors', 'part', 'parts', 'repair', 'shrank', 
            'shrunk', 'smell', 'smells', 'stain', 'stained', 'stolen', 'cheap', 'cheapest', 'code', 'coupon', 
            'coupons', 'counterfeit', 'deals', 'discount', 'fake', 'inexpensive', 'price', 'prices', 'refurbish',
            'refurbished', 'surplus', 'report', 'reports', 'shipping', 'shipment',
            'high', 'product', 'fees', 'fee', 'broken','break', 'broke','shipped' 'late', 'delivery', 'expensive', 'time', 'refund', 'provider', 'seller', 'damage', 'damaged', 'payment',
            'profil', 'login', 'stressful', 'cost', 'price', 'break', 'cart', 'access', 'metal', 'plastic', 'rubber', 
            'wood', 'business', 'container', 'factory', 'factories', 'fees', 'whole sale', 
            'wholesale', 'wholesalers', 'manufacturing', 'manufacturer', 'manufacture']

# pour créer des catégories pour 'size' sinon ya trop de différence de taille entre les mots
def perc(x):
    stupid_list = []
    for item in np.percentile(df_hehehe["counts"], np.arange(0, 100, 10)):
        if x >= item:
            stupid_list.append(item)
    return stupid_list[-1]
            
    
df_hehehe["percentile"] = df_hehehe["counts"].apply(perc)

colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(100)]))]

data = go.Scatter(x=[random.random() for i in range(80)],
                 y=[random.random() for i in range(50)],
                 mode='text',
                 text=df_hehehe[df_hehehe.unique_values.isin(keywords)][:30]["unique_values"],
                 marker={'opacity': 0.3},
                 textfont={'size': (df_hehehe[df_hehehe.unique_values.isin(keywords)][:30]["percentile"]/5),
                           'color': colors})
layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                    'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})
fig = go.Figure(data=[data], layout=layout)

plot(fig)

# idea is to click on the word, for example "delivery" and it switches to the worldcloud based on delivery-related word


delivery = ['shipping', 'shipment', 'high', 'product', 'fees', 'fee', 'broken', 'late', 'delivery', 'expensive', 
            'time', 'provider', 'seller', 'damage', 'damaged', 'payment', 'profil', 'login', 'stressful', 
            'cost', 'price', 'break', 'cart', 'access', 'apart', 'broke', 'broken', 'burn', 'burned', 'burnt', 'care', 'caring', 'condition', 
            'crack', 'cracked', 'cracking', 'cut', 'deform', 'deformed', 'discolor', 'drop', 'dropped', 
            'maintenance', 'odor', 'odors', 'part', 'parts', 'repair', 'shrank', 'shrunk', 'smell', 'smells', 
            'stain', 'stained', 'stolen','shipping', 'shipment', 'high', 'product', 'fees', 'fee', 'broken', 
            'late', 'delivery', 'expensive', 'time', 'provider', 'seller', 'damage', 'damaged', ]

data = go.Scatter(x=[random.random() for i in range(80)],
                 y=[random.random() for i in range(50)],
                 mode='text',
                 text=df_hehehe[df_hehehe.unique_values.isin(delivery)][:30]["unique_values"],
                 marker={'opacity': 0.3},
                 textfont={'size': (df_hehehe[df_hehehe.unique_values.isin(delivery)][:30]["percentile"]/5),
                           'color': colors})
layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                    'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})
fig = go.Figure(data=[data], layout=layout)

plot(fig)
