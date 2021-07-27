import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager



def check_exists_by_xpath(xpath, driver):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def information_panel(video_id):
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        web = 'https://www.youtube.com/watch?v='+video_id
        driver.get(web)
        time.sleep(5)

        exist = check_exists_by_xpath('//*[@id="clarify-box"]',driver)
        if (exist ==True):
             content = driver.find_element_by_xpath('//*[@id="clarify-box"]').text
        else:
            content =''
        driver.close()
        return content
    except:
        return 'Error'


if __name__ == "__main__":
    print(information_panel(sys.argv[1]))
