import requests


def get(epoint):
    resp = requests.get(epoint)
    return resp.json()


def traverse_linked_pages(href_page, call_me_whith_rdata, num_max_pages=None, ipage=0, verbose=0,
  next_key='next'):
    ipage += 1
    if verbose > 0:
        num_max_pages_put = 'all'
        if num_max_pages is not None:
            num_max_pages_put = str(num_max_pages)
        print('Loading page {0:d} of {1} from {2}'.format(ipage, num_max_pages_put, href_page))

    rdata = get(href_page)
    call_me_whith_rdata(rdata)
    
    if num_max_pages is None or ipage < num_max_pages: 
        if next_key in rdata and rdata[next_key] is not None:
            traverse_linked_pages(rdata[next_key], call_me_whith_rdata, num_max_pages=num_max_pages, 
              ipage=ipage, verbose=verbose)


