import requests
import pandas as pd
from colour import Color

source_mapping = {"TheStar": "The Star", "sebenarnya": "SEBENARNYA.MY", "HarianMetro": "Harian Metro"}

def get_colors_red_green(val = 0):
    max_idx = 20
    red = Color("red")
    colors = [j.get_hex_l() for j in list(red.range_to(Color("green"), max_idx))]
    idx = int(val*(max_idx - 1))
    return colors[idx]
    
def convert_color(score, maxx = 20):
    flat_score = min(score/maxx,1)
    style = str("color:") + get_colors_red_green(flat_score)
    return style
    
def search(keyword, max_results = 10, index = "my_index"):
    result = requests.get(f"http://localhost:9200/{index}/_search?q={keyword}")
    x = result.json().get("hits").get("hits")[0:max_results]
    titles = [j.get("_source").get("title") for j in x]
    urls = [j.get("_source").get("url") for j in x]
    categories = [j.get("_source").get("category") for j in x]
    sources = [j.get("_source").get("news_vendor") for j in x]
    
    #     news_dates = [j.get("_source").get("news_date") for j in x]
    scores = [j.get("_score") for j in x]
    result_dict = dict(title = titles, url = urls, category = categories, source = sources, score = scores)
    return result_dict

def get_top_news(r, category = "FakeNewsAlert", top = 3):
    df = pd.DataFrame(r)
    df["source"] = df["source"].replace(source_mapping)
    df["color"] = df["score"].apply(lambda x: convert_color(x))
    sdf = df.loc[df["category"] == category].sort_values("score", ascending = False)
    unique_source = sdf["source"].unique()
    num_unique_source = len(unique_source)
    ddf = [{"source": src, "df": sdf.loc[sdf["source"] == src].sort_values("score", ascending = False).drop_duplicates().head(top)} for src in unique_source]
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
        
        
    