import scrapy


class Top100Spider(scrapy.Spider):
    name = 'top100'
    allowed_domains = ['https://izea.com/']
    start_urls = ['https://izea.com/resources/top-100-linkedin-influencers/']

    def parse(self, response):
        inf_list = response.xpath("//div[@id='fws_65864eb400a94']//h3")
        names = inf_list.css('::text').extract()
        names = map(lambda x: ' '.join(x.strip('\xa0').split(' ')[1:]), names)

        with open('../influencers.txt', 'w+', encoding='utf8') as file:
            for name in names:
                file.write(name + '\n')
