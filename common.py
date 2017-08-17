import requests
import localdata
import logging 

TC_HEADER = {'Content-type': 'application/json', 'Accept': 'application/json'}
TC_AUTH = (localdata.USER, localdata.PW)
TC_ENDPOINT_API = '/app/rest/latest'
TC_ENDPOINT = localdata.TC


def get(epoint, auth=None, headers=None):
    logging.debug('Calling {:}.'.format(epoint))
    resp = requests.get(epoint, auth=auth, headers=headers)
    return resp.json()


def prepend_if_not_in(text, prefix):
    if prefix not in text:
        return prefix + text
    return text


def get_tc(epoint):
    '''
    Can be absolute or relative endpoint.
    '''
    epoint = prepend_if_not_in(epoint, TC_ENDPOINT_API)
    epoint = prepend_if_not_in(epoint, TC_ENDPOINT)
    return get(epoint, auth=TC_AUTH, headers=TC_HEADER)


def traverse_linked_pages(href_page, call_me_whith_rdata, num_max_pages=None, ipage=0, next_key='next', 
  auth=None, headers=None, getter=get):
    ipage += 1
    num_max_pages_put = 'all'
    if num_max_pages is not None:
        num_max_pages_put = str(num_max_pages)
    logging.info('Loading page {0:d} of {1} from {2}.'.format(ipage, num_max_pages_put, href_page))

    rdata = getter(href_page)
    call_me_whith_rdata(rdata)
    logging.debug(rdata.keys())

    if num_max_pages is None or ipage < num_max_pages: 
        if next_key in rdata and rdata[next_key] is not None:
            traverse_linked_pages(rdata[next_key], call_me_whith_rdata, num_max_pages=num_max_pages, 
              ipage=ipage, auth=None, headers=None, getter=getter, next_key=next_key)


def traverse_linked_pages_tc(href_page, call_me_whith_rdata, num_max_pages=None, ipage=0):
    return traverse_linked_pages(href_page, call_me_whith_rdata, num_max_pages=num_max_pages, ipage=ipage, 
      next_key='nextHref', auth=TC_AUTH, headers=TC_HEADER, getter=get_tc)