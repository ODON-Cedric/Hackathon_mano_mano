import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import time

    ### SCRAPING PAGE 1 - .UK
def scrap_uk():
        start = time.time()
        url = "https://fr.trustpilot.com/review/manomano.co.uk?languages=en&stars=1&stars=2&stars=3"
        navigator = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
        result = requests.get(url, headers={'User-Agent': navigator})
        soup = BeautifulSoup(result.text, "html.parser")
        stars = soup.find_all("div", {"class" :"styles_reviewHeader__iU9Px", })
        reviews = soup.find_all('p', {"class":"typography_typography__QgicV typography_body__9UBeQ typography_color-black__5LYEn typography_weight-regular__TWEnf typography_fontstyle-normal__kHyN3"})
        time_ = soup.find_all('time')
        localisation = soup.find_all('span', {'data-consumer-country-typography': "true"})


        reviews_list_p1 = []
        stars_rev_p1 = []
        time_list_p1 = []
        loc_list_p1 = []
        for x in stars:
            stars_rev_p1.append(x["data-service-review-rating"])

        for x in reviews[2:]:
            reviews_list_p1.append(x.text)

        for x in time_ :
            time_list_p1.append(x["title"])

        for x in localisation:
            loc_list_p1.append(x.text)

        zipped = zip(reviews_list_p1, stars_rev_p1, loc_list_p1, time_list_p1)
        zz = list(zipped)
        df_page1 = pd.DataFrame(zz, columns = ['review', 'stars', 'localisation', 'date'])

        ### SCRAPING AUTRES PAGES - .UK
        reviews_list = []
        stars_rev = []
        time_list = []
        loc_list = []
        for i in range(2,101,1):
            url = f"https://fr.trustpilot.com/review/manomano.co.uk?languages=en&page={i}&stars=1&stars=2&stars=3"
            navigator = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)'
            result = requests.get(url, headers={'User-Agent': navigator})
            soup = BeautifulSoup(result.text, "html.parser")
            stars = soup.find_all("div", {"class" :"styles_reviewHeader__iU9Px", })
            reviews = soup.find_all('p', {"class":"typography_typography__QgicV typography_body__9UBeQ typography_color-black__5LYEn typography_weight-regular__TWEnf typography_fontstyle-normal__kHyN3"})
            time_ = soup.find_all('time')
            localisation = soup.find_all('span', {'data-consumer-country-typography': "true"})

            for x in stars:
                stars_rev.append(x["data-service-review-rating"])

            for x in reviews[2:]:
                reviews_list.append(x.text)

            for x in time_ :
                time_list.append(x["title"])

            for x in localisation:
                loc_list.append(x.text)

        zipped = zip(reviews_list, stars_rev, loc_list, time_list)
        zz = list(zipped)
        df_full = pd.DataFrame(zz, columns = ['review', 'stars', 'localisation', 'date'])
        df = pd.concat([df_page1, df_full])
        return df
        

df_uk = scrap_uk()


# nlp review

# return the wordnet object value corresponding to the POS tag
from nltk.corpus import wordnet
import string
import nltk
from nltk import pos_tag
nltk.download('stopwords')
from nltk.tokenize import WhitespaceTokenizer
from nltk.stem import WordNetLemmatizer

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
    stop = stopwords.words('english')
    text = [x for x in text if x not in stop]
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
df_uk["review_clean"] = df_uk["review"].apply(lambda x: clean_text(x))



#### scrap note trustpilot

def provider_country(x):
    try:
        return str(x).split('(')[1].replace(")","")
    except :
        return ""

df["provider_country"] = df["provider"].apply(provider_country)
df["provider2"] = df["provider"].apply(lambda x: str(x).split(' (')[0])
df_provider = df[["provider2", "provider_country", "score"]].copy()
df_provider = df_provider[df_provider['score'] < 8]
df_provider["provider"] = df_provider["provider2"].apply(lambda x: str(x).strip())
provider_list = df_provider.groupby("provider").mean().index.tolist()


base = 'https://fr.trustpilot.com/review/'
domain_list = ['.com','.fr','.co.uk','.es','.it','.de']
site_lst = []
N = len(domain_list)
k = 0
while k != N:
  for provider in provider_list:
    url = base + provider + domain_list[k]
    # print(url)
    if requests.get(url).status_code == 200:
      print('ok')
      site_lst += [url]
      provider_list.remove(provider)
    else:
      pass
  k+=1
    
 final_provider = [provider for provider in provider_list if provider not in new_provider]

# for url in site_lst
lst_score = []
for url in site_lst:
  page = requests.get(url)
  data = page.text
  soup = BeautifulSoup(data, 'html.parser')
  # print(soup)
  score = soup.findAll("p", {"class":"typography_typography__QgicV typography_bodysmall__irytL typography_color-gray-7__9Ut3K typography_weight-regular__TWEnf typography_fontstyle-normal__kHyN3"})
  score_ = [ele.text for ele in score][0]
  lst_score += [score_]

d = {'provider' : final_provider, 'provider_site' : site_lst, 'score' : lst_score}
df_provider = pd.DataFrame(d)
