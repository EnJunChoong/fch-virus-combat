import time
from processing_harianmetro import updater_processing_harianmetro
from settings import Settings

wait_time = Settings.GENERAL_CRAWL_WAIT_TIME 

while True:
    time.sleep(5)
    try:
        updater_processing_harianmetro()
    except Exception as err:
        print("Error at: updater_processing_harianmetro")
        print(err)
    time.sleep(wait_time+30)