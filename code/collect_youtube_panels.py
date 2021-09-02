import csv
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


def get_information_panel_content(video_id):

    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get('https://www.youtube.com/watch?v=' + video_id)
    time.sleep(10)

    try:
        information_panel_content = browser.find_element_by_xpath('//*[@id="clarify-box"]').text
    except NoSuchElementException:
        information_panel_content = ''

    browser.quit()
    
    return information_panel_content


if __name__ == "__main__":

    df = pd.read_csv('./data/youtube_flags.csv')

    with open('./data/youtube_flags_new.csv', "w") as csv_file:
        
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(['video_id', 'information_panel_content'])

        for video_id in df.video_id.values:
            writer.writerow([video_id, get_information_panel_content(video_id)])
