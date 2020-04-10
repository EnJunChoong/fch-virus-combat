import requests
import pandas as pd

def search(keyword, max_results = 10):
    result = requests.get(f"http://localhost:9200/news/_search?q={keyword}")
    x = result.json().get("hits").get("hits")[0:max_results]
    titles = [j.get("_source").get("title") for j in x]
    urls = [j.get("_source").get("url") for j in x]
    categories = [j.get("_source").get("category") for j in x]
    sources = [j.get("_source").get("news_vendor") for j in x]
    scores = [j.get("_score") for j in x]
    result_dict = dict(title = titles, url = urls, category = categories, source = sources, score = scores)
    return result_dict

def get_top_news(r, category = "FakeNewsAlert", top = 3):
    df = pd.DataFrame(r)
    sdf = df.loc[df["category"] == category].sort_values("score", ascending = False)
    unique_source = sdf["source"].unique()
    num_unique_source = len(unique_source)
    ddf = [{"source": src, "df": sdf.loc[sdf["source"] == src].sort_values("score", ascending = False).head(top)} for src in unique_source]
    max_score = [sdf.loc[sdf["source"] == src]["score"].max() for src in unique_source]
    
    return ddf, num_unique_source, max_score

def predict(n_fna, n_news, mscore_fna, mscore_news):
    if n_news >= 2 and n_fna == 0:
        idx = 0
    elif n_news == 1 and n_fna == 0:
        idx = 1
    elif n_news == 0 and n_fna == 0:
        idx = 2
    elif n_news == 0 and n_fna >= 1:
        idx = 4
    elif n_news >= 1 and n_fna >= 1:
        m_fna = max(mscore_fna)
        m_news = max(mscore_news)
        ratio = m_fna / m_news
        if ratio > 1.5:
            idx = 4
        elif ratio <= 1.5 and ratio >= 0.5:
            idx = 3
        else: 
            idx = 1
    return idx
        
        
    