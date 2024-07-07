import scrapy
from pytube import YouTube
from http.client import IncompleteRead
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class EduSpider(scrapy.Spider):
    name = "edu"
    allowed_domains = ["edulance.ru", "youtube.com"]
    start_url = '' # url with token

    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(self.start_url)
        WebDriverWait(self.driver, 10).until(EC.url_changes(self.start_url))

    def start_requests(self):
        yield scrapy.Request(self.start_url,
                             callback=self.to_courses_list)

    def to_courses_list(self, response):
        main_page = response.css("a.navbar-header::attr(href)").get()
        yield response.follow(main_page, callback=self.parse_courses)

    def parse_courses(self, response):
        courses_list = response.css("a.link::attr(href)").getall()
        next_page = response.css('li.next>a ::attr(href)').get()
        yield from response.follow_all(courses_list, callback=self.parse)

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_courses)

    def parse(self, response):
        lessons_links = map(lambda x: 'https://edulance.ru' + x, response.css("div.flex>a::attr(href)").getall())
        for link in lessons_links:
            self.driver.get(link)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe#player')))
            iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe#player')
            for iframe in iframes:
                self.driver.switch_to.frame(iframe)
                video_link = self.driver.find_element(By.CSS_SELECTOR, 'a.ytp-title-link').get_attribute('href')
                self.driver.switch_to.default_content()

                yield {'video url': video_link}
                self.download_video(video_link)

    def download_video(self, url):
        while True:
            try:
                stream = YouTube(url).streams.get_highest_resolution()
                stream.download(r'F:\Видео для Вики')
                self.logger.warning('Video downloaded successfully!')
                break
            except IncompleteRead:
                self.logger.warning('IncompleteRead exception! Try again in 3 sec.')
                sleep(3)
                continue

    def closed(self, reason):
        self.driver.quit()
