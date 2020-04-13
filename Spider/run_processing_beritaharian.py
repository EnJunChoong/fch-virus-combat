import time
from processing_beritaharian import updater_processing_beritaharian
from settings import Settings

wait_time = Settings.GENERAL_CRAWL_WAIT_TIME 

while True:
    time.sleep(60)
    try:
        updater_processing_beritaharian()
    except Exception as err:
        print("Error at: updater_processing_beritaharian")
        print(err)
    time.sleep(wait_time+30)