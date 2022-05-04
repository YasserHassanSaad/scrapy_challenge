import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from property import Property


class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url, callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url, callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        properties = response.xpath('//*[@class="test-inline"]')

        for prop in properties:
            l = ItemLoader(item=Property(), selector=prop)

            l.add_value('title', response.xpath('//*[@class="bottom-ic"]/p/text()').extract_first())
            l.add_value('price', prop.xpath('.//*[@class="bottom-ic"]/h5/text()').extract_first().split()[1])

            url = prop.xpath('.//*[@class="h4-space"]/h4/a/@href').extract_first()
            l.add_value('url', response.urljoin(url))

            yield l.load_item()

        if '&pageset=2' not in response.url:
            second_page = response.url + '&pageset=2'
            yield Request(second_page, callback=self.parse_area_pages)  