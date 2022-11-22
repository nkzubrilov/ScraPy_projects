import scrapy


class AlpexSpider(scrapy.Spider):
    name = 'alpex'

    start_urls = [
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/linear_01',
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/stevolution_01',
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/tripler_01',
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/sentinel',
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/grilleset_01',
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/lightbar_01',
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/utilityseries_01',
        'https://www.alpex4x4.com/brand_01/lazer_lamps_01/lazer_acc',
        'https://www.alpex4x4.com/groups/bars/front_bar',
        'https://www.alpex4x4.com/groups/bars/side_bar',
        'https://www.alpex4x4.com/groups/bars/styling_bar',
        'https://www.alpex4x4.com/groups/ubody_guard'
    ]

    def parse(self, response):
        product_links = response.xpath('//div[@class="card-body product-card-body"]/h2/a/@href')
        yield from response.follow_all(product_links, self.parse_product)

        page_link = response.xpath('//div[@class="sortbar sortbar-bottom"]//a[@class="page-link page-next"]/@href')
        if page_link:
            yield from response.follow_all(page_link, self.parse)

    def parse_product(self, response):
        yield {
            'name': response.css('span.product-page-product-name::text').get(),
            'price': response.css('span.product-page-price::text').get() + response.css('span.postfix::text').get(),
            'availability': response.css('td.param-value.productstock-param > span::text').getall()[-1].strip(),
            'manufacturer': response.css('td.param-value.manufacturer-param img::attr(alt)').get(),
            'model': response.css('td.param-value.productsku-param > span::text').get(),
            'parameters': response.css('td.param-value.product-short-description strong::text').re(r'[\w\d]{1}.*'),
            'video_url': response.css('div.embed-responsive.embed-responsive-4by3 iframe::attr(src)').re(r'www[\.\w\d/-]+')
        }

