# Forkwell Coronavirus Hack: Virus Combat

## Team Name: UniJagung

## Team Members:
1. Choong En Jun
2. Cheah Jun Yitt

### Crude Idea
1. Scrap news from various sources, and label their authenticity as True (authentic news) or False (fake news).
2. Labelling of the news authenticity can be inferred from a manually curated list of credible sources and official sources like sebenar.my.
3. Store the news and labels on a database.
4. Create an API to allow developers to query the database. Use case include development of web/mobile apps to tackle fake news, model training for fake news detection, and bots to help detect fake news.

### Start Small, Think Big, Scale Fast
1. Start Small: Work on Malaysia news sources, create a database and API only.
2. Think Big: Aim to create a bot to automatically detect potential fake news, enlighten any potential readers with an automated reply to the news (on Twitter for now). E.g. someone posted a fake news on Twitter, a bot will detect it and reply to the tweet, suggesting that it is a fake news, and cite at least one credible source to enlighten any potential reader.
3. Scale Fast: Scale to other countries, scrap news from various countries, and make the bot an international one.

### Pipelines
1. Scrape from source -> raw_collection
2. Processing pipeline -> processed_collection
3. Combiner -> Combine all sources to one collection -> combined_collection
4. Serve combined_collection -> Search Engine Web App

### News: Fields
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
15. meta_full_html (raw only)

### Further Improvements:
1. Create apps to monitor pipelines.
2. Better logging 
3. Use elasticsearch 
4. Translation


### Search Engine Web App:
#### Categorization
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

*add weights based on scoring - show color gradient for less confidence search results*