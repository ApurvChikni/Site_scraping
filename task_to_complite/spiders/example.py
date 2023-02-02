import pandas as pd
import scrapy
from scrapy.cmdline import execute
import json,re

# from scrapy.http import HtmlResponse
from scrapy.selector import Selector

data_accumulatore_list = []

class ExampleSpider(scrapy.Spider):
    name = "example"
    start_urls = ["https://isd110.org/our-schools/laketown-elementary/staff-directory"]
    
    def parse(self, response):
        try:
            temp_school_name = response.xpath('//title/text()').get()
            if temp_school_name:
                try:
                    school_name = temp_school_name.split('|')[1].strip()
                except:
                    school_name=''
        except:
            school_name = ''
        try:
            temp_add = response.xpath('//*[@class="address"]/text()').getall()
            if temp_add:temp_add=[i.strip() for i in temp_add if i.strip()!=""]
            zip_code = state = city = address = ''
            for i in temp_add:
                if re.findall(r'\d{5,}',i):
                    try:
                        zip_code=re.findall(r'\d{5}',i)[0]
                    except:
                        zip_code=''
                    try:
                        state = re.findall(r'[A-Z]{2}',i)[0]
                    except:
                        state=''
                    try:
                        city = i.split(',')[0]
                    except:
                        city=''
                else:
                    address = i.strip()

        except Exception as e:
            zip_code = state = city = address = ''

        item = {
            'school_name': school_name,
            'zip_code': zip_code,
            'state': state,
            'city': city,
            'address': address
        }



        url = "https://isd110.org/views/ajax?_wrapper_format=drupal_ajax"

        payload = "view_name=staff_teaser&view_display_id=default&view_args=all%2F5&view_path=%2Fnode%2F32&view_base_path=&view_dom_id=b1e9ab5d68f366f7cbabf6ddc3c12567518e962c2e62b5882fa5bf9305076a42&pager_element=0&page=0&_drupal_ajax=1&ajax_page_state%5Btheme%5D=wac&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=aeon%2Fbase%2Cblazy%2Fbio.ajax%2Ccore%2Fhtml5shiv%2Ccore%2Fpicturefill%2Cgoogle_analytics%2Fgoogle_analytics%2Cgtranslate%2Fjquery-slider%2Cmicon%2Fmicon%2Cparagraphs%2Fdrupal.paragraphs.unpublished%2Csystem%2Fbase%2Cux%2Fux.auto_submit%2Cux_form%2Fux_form.input%2Cux_header%2Fux_header%2Cux_offcanvas_menu%2Fux_offcanvas_menu%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module%2Cwac%2Fbase"
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': '_ga=GA1.2.1739906034.1675338201; _gid=GA1.2.1083475475.1675338201',
            'x-requested-with': 'XMLHttpRequest'
        }
        yield scrapy.Request(method="POST",url=url,headers=headers,body=payload,callback=self.parse1,meta={'item_data':item,'page_no':0})

    def parse1(self, response):
        temp_data_dict = response.meta['item_data']
        j_data = json.loads(response.text)
        res_text= j_data[2]['data']
        res = Selector(text=res_text)
        patent_selector = res.xpath('//*[@class="views-row"]')
        for sel_div in patent_selector:
            final_item = temp_data_dict.copy()
            full_name = sel_div.xpath('.//*[@class="title"]/text()').get()
            if ',' in full_name:
                try:
                    final_item['first_name'] = full_name.split(",")[1].strip()
                except:
                    final_item['first_name']=''
                try:
                    final_item['last_name'] = full_name.split(",")[0].strip()
                except:
                    final_item['last_name']=''
            try:
                final_item['title'] = sel_div.xpath('.//*[@class="field job-title"]/text()').get().strip()
            except:
                final_item['title']=''
            try:
                final_item['phone_num'] = sel_div.xpath('.//*[@class="field phone"]/a/text()').get()
            except:
                final_item['phone_num']=''
            try:
                final_item['email'] = sel_div.xpath('.//*[@class="field email"]/a/text()').get()
            except:
                final_item['email']=''

            data_accumulatore_list.append(final_item)


        next_page=res.xpath('//*[@class="item next"]/a/@href').get()
        next_page_no = response.meta['page_no']
        if next_page:
            next_page_no+=1
            print(next_page_no)
            url = "https://isd110.org/views/ajax?_wrapper_format=drupal_ajax"

            payload = f'view_name=staff_teaser&view_display_id=default&view_args=all%2F5&view_path=%2Fnode%2F32&view_base_path=&view_dom_id=b1e9ab5d68f366f7cbabf6ddc3c12567518e962c2e62b5882fa5bf9305076a42&pager_element=0&page={next_page_no}&_drupal_ajax=1&ajax_page_state%5Btheme%5D=wac&ajax_page_state%5Btheme_token%5D=&ajax_page_state%5Blibraries%5D=aeon%2Fbase%2Cblazy%2Fbio.ajax%2Ccore%2Fhtml5shiv%2Ccore%2Fpicturefill%2Cgoogle_analytics%2Fgoogle_analytics%2Cgtranslate%2Fjquery-slider%2Cmicon%2Fmicon%2Cparagraphs%2Fdrupal.paragraphs.unpublished%2Csystem%2Fbase%2Cux%2Fux.auto_submit%2Cux_form%2Fux_form.input%2Cux_header%2Fux_header%2Cux_offcanvas_menu%2Fux_offcanvas_menu%2Cviews%2Fviews.ajax%2Cviews%2Fviews.module%2Cwac%2Fbase'
            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'cookie': '_ga=GA1.2.1739906034.1675338201; _gid=GA1.2.1083475475.1675338201',
                'x-requested-with': 'XMLHttpRequest'
            }
            yield scrapy.Request(method="POST", url=url, headers=headers, body=payload, callback=self.parse1,
                                 meta={'item_data': response.meta['item_data'],'page_no':next_page_no})

    def close(spider, reason):
        df = pd.DataFrame(data_accumulatore_list)
        df.insert(0,'Id',[i for i in range(1,len(df)+1)])
        df.to_csv("final_data.csv",index=False)




if __name__ == '__main__':
    execute("scrapy crawl example".split())