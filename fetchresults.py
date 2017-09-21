import common
import numpy as np
import logging
import datetime

HOST = 'http://slb-2cgbj32.dir.slb.com:8000'
API = '/devdiff/latest'
ENDPOINT = '/results/?page=1'
FNAME_DATA = 'data_tmp/evaldevdiffserv_data'


def get_all_with_status():
    first_page = HOST + API + ENDPOINT
    results = []

    def for_each_results_page(rdata, results):       
        for result in rdata['results']:
            if result['status']:
                results += [result]   

    common.traverse_linked_pages(first_page, for_each_results_page, callback_args=[results])
    return results


def get_last_24hrs():
    first_page = HOST + API + ENDPOINT
    num_max_pages = 50 #None
    results = []

    def for_each_results_page(rdata, results): 
        now = datetime.datetime.now()
        #logging.debug('Now {}'.format(now.isoformat()))       
        for result in rdata['results']:
            then = datetime.datetime.strptime(result['posted'], "%Y-%m-%dT%H:%M:%S.%fZ")
            #logging.debug('Result: {}'.format(then.isoformat()))
            delta = now - then            
            if delta.total_seconds() < float(24*60*60):
                logging.debug('Delta: {}'.format(str(delta)))
                results += [result]       
   
    common.traverse_linked_pages(first_page, for_each_results_page, num_max_pages=num_max_pages, callback_args=[results])
    return results









