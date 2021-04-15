import scrapy

from scrapy.loader import ItemLoader

from ..items import AttijariwafabankItem
from itemloaders.processors import TakeFirst


class AttijariwafabankSpider(scrapy.Spider):
	name = 'attijariwafabank'
	start_urls = ['https://www.attijariwafabank.com/fr/espace-media/actualites']

	def parse(self, response):
		post_links = response.xpath('//div[@class="article-card__content"]')
		for post in post_links:
			url = post.xpath('.//div[@class="article-card__permalink"]/a/@href').get()
			date = post.xpath('.//div[@class="article-item__date"]/span/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//li[@class="pager-next last"]/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//*[(@id = "page-title")]/text()').get()
		description = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "article-details__body", " " ))]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=AttijariwafabankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
