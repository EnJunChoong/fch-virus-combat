# Forkwell Coronavirus Hack: Virus Combat

## Team Name: UniJagung

## Team Members:
1. Choong En Jun  
    - Github: <https://github.com/EnJunChoong/>
2. Cheah Jun Yitt
    - Github: <https://github.com/junyitt/>

## Presentation Slides, Pitch and Web App
1. [Slides](https://docs.google.com/presentation/d/1-SKUOr6jdPtzyyujNData0-Gf4s8PiTCxJgpfb3bCuc)
2. [Pitch](https://youtu.be/TXFyflu78lY )
3. [FFA web app](<http://facts4all.ml>)

  
![Facts for All (FFA)](FFA_App/app/static/images/full_logo.png)



### A fact check app to combat COVID-19 related fake news
The trend is rising for fake news creation. With the rise of DeepFake (Generative AI) etc., anyone can create increasingly realistic fake content and spread them.  

[Example of Fake News: 1](https://sebenarnya.my/tiada-kenyataan-bahawa-kelab-golf-dibenarkan-dibuka-semasa-pkp/)  
For example, someone spreading misinformation that certain area is no longer under Movement Control Order (MCO) may inhibit the effectiveness to contain the spread of the virus.

[Example of Fake News: 2](https://sebenarnya.my/stok-beras-negara-hanya-mampu-bertahan-selama-2-5-bulan-adalah-tidak-benar/)  
Misinformation about diminishing food supplies in the country may cause widespread panic buying.

The current situation to do fact checking is:
1. Non-existent: Users simply do not know how to fact check.
2. Rather manual and tedious: Depends on the user to manually google and check through various verified news sources. 

Due to such reasons, users tend to share information without thinking of the consequences that such information turns out to be rumour or misinformation later on.

Hence, there is a need to create a one-stop platform to allow users to quickly verify any sources of information that they have encountered, and advise the users whether it is okay to share them or not. 
 
## Crude Idea on the Development of FFA
1. Scrap news from various sources, and label them as Verified News or Fake News Alert (depending on where they originated).
2. Labelling of the news can be inferred from a manually curated list of credible sources and official sources like sebenarnya.my (Fake News Alert), Harian Metro (Verified News) and Berita Harian (Verified News).
3. Store the news and labels on a MongoDB database (raw html data).
4. Ingest the processed news data to ElasticSearch.
5. Create a search-engine-like web app for fact checking COVID-19 related news.  
~~6. Create an API to allow developers to query the database. Use case include development of web/mobile apps to tackle fake news, model training for fake news detection, and bots to help detect fake news.~~ (cancelled for now because of grey area of sharing scraped data)

## Start Small, Think Big, Scale Fast
1. Start Small: Work on Malaysia COVID-19-related news sources, create a database and a simple web app.
2. Think Big: Aim to create a platform to automatically detect potential fake news, enlighten any potential readers with credible sources. Bring in various parties like government and companies to quickly verify any recent fake news ASAP.
3. Scale Fast: Scale to other countries, scrape news from various countries and beyond COVID-19 related news, and make the platform an international one.

## Dependencies Installation for Ubuntu 18.04
#### Create conda environment
```
conda env create -f environment.yml
conda activate covid
```

#### Install MongoDB
```
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

#### Install ElasticSearch
```
curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.2-amd64.deb
sudo dpkg -i elasticsearch-7.6.2-amd64.deb
sudo /etc/init.d/elasticsearch start
```

#### Install Kibana
```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
sudo apt-get update && sudo apt-get install kibana
```

## Pipelines
1. Scrape news from news websites -> raw MongoDB collection
2. Processing pipeline -> ingest processed data to ElasticSearch index
    - Commands in /Spider/run.sh will do the following:
        - Crawl the news from the news websites (Berita Harian, Harian Metro, Sebenarnya, and The Star)
        - Store the raw data into MongoDB (for backup and debugging)
        - Clean and process the raw html 
        - Ingest the processed data to ElasticSearch index
    - Data Schema (in Json)
        - News: Fields
        ```
            1. scrape_date
            2. news_date
            3. title
            4. category (News, or FakeNewsAlert)
            5. topic (COVID-19)
            6. content_text
            7. image: list:{src, caption}
            8. audio: list:{src, caption}
            9. fact_src (NA if not fake news alert category)
            10. label (4 for actual reported news)
            11. confidence (4 for actual report news)
            12. url
            13. news_vendor
            14. processed_date
            15. content_html (raw only)
            16. meta_full_html (raw only)
        ```
3. Query news  -> Output results to FFA Web App (Developed using Flask)
    - Commands in /FFA_App/run.sh will launch the FFA fact checking web app.
    - The web app is currently hosted on our DigitalOcean remote server:
        - <http://128.199.71.7:5000/>


## FFA Web App
#### Prediction/Categorization
Currently, there is a simple algorithm to categorize whether any keywords entered into the search tool in the FFA Web App belongs to any of the following categories:
1. Fact - Feel free to share! - Verified news from at least 2 sources, did not appear as FakeNewsAlert. 
    - (>=2, 0)
2. Latest news - Not advisable to share immediately! - Verified news from 1 source only, did not appear as FakeNewsAlert.
    - (==1, 0)
3. No search results - Avoid sharing unverified news or rumours! - No search results.
    - (==0, 0)
4. Conflicting results - Please take precautions and manually check the news authenticity from at least 2 verified news sources before sharing! - 
    - (>=1, >=1)
5. Suspected fake news - Avoid sharing unverified news or rumours! - 
    - (0, >=1)
    
As the current categorization is very simple, it acts as a heads up for users to look into the top search results quickly, and check whether what they are searching was reported by verified news sources. If what the users are searching did not appear in the verified news sources, the app will advise users to avoid sharing. There is definitely a big room for improvement on inaccuracies and uncertainties of the categorization algorithm (See Further Improvements).

### Further Improvements
1. [x] Create apps to monitor pipelines (Kibana)
2. [ ] Better logging (Future)
3. [x] Use elasticsearch 
4. [ ] Translation (Future) 
5. [x] Visualization of Rate of fake news on sebenarnya (Done using Kibana)
6. [x] Mapping news source (TheStar to The Star) on web app
7. [x] Font sizing and formatting
8. [x] Search correctness - color intensity -red to green, red as likely incorrect search result, green as likely correct
9. [ ] API for developers (Future)
10. [ ] Improvement on search beyond traditional keyword matching (use of AI word embeddings for language understanding)
11. [ ] Extend search functionalities to Audio/Image/Video/Contents in URL
