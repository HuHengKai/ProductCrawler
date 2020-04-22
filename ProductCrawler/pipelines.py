# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from os import mkdir, makedirs
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from ProductCrawler.settings import IMAGES_STORE

class GoodscrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class GoodsUrlPipeline(object):
    """把商品的网址保存为txt文件"""
    def process_item(self, item, spider):
        # 保存路径：
        # images/<brand>/<number>/url.txt
        filepath = file_path(
            item.get('brand'),
            item.get('season'),
            item.get('week'),
            item.get('title'),
            item.get('art_no'),
        )
        filepath = IMAGES_STORE + '/' + filepath
        try:
            makedirs(filepath)
        except OSError:
            pass
        filename =  filepath + '/url.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(item['item_url'])
        return item


class GoodsImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        brand = request.meta['brand']
        title = request.meta['title']
        art_no = request.meta.get('art_no')
        season = request.meta.get('season')
        week = request.meta.get('week')
        file_name = file_path(brand, season, week, title, art_no, request.url.split('/')[-1])
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Download Failed')
        return item

    def get_media_requests(self, item, info):
        image_base_url = item.get('image_base_url', None)
        if image_base_url:
            images_url = [image_base_url + part_url for part_url in item['images']]
        else: # image_base_url is None
            images_url = item['images']
        for image_url in images_url:
            yield Request(image_url,
                          meta={'brand': item.get('brand'),
                                'title': item.get('title'),
                                'art_no': item.get('art_no'),
                                'season': item.get('season'),
                                'week': item.get('week')}
                          )


def file_path(brand=None, season=None, week=None, title=None, art_no=None, filename=None):
    filepath = ''
    if brand:
        filepath += brand + '/'
    if season:
        filepath += season + '/'
    if week:
        filepath += week + '/'
    if art_no:
        filepath += art_no + '/'
    else:  # title is not None.
        filepath += title + '/'
    if filename:
        filepath += filename
    return filepath