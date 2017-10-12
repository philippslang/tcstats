import datetime
import json
import sys
import requests
import logging


TC_HEADER = {'Content-type': 'application/json', 'Accept': 'application/json'}
TC_ENDPOINT = 'http://gb0921app02.dir.slb.com'
TC_ENDPOINT_API = '/app/rest/latest'


def get(epoint, auth=None, headers=None):
    resp = requests.get(epoint, auth=auth, headers=headers)
    return resp.json()


def prepend_if_not_in(text, prefix):
    if prefix not in text:
        return prefix + text
    return text


def get_tc(epoint, tc_auth):
    '''
    Can be absolute or relative endpoint.
    '''
    epoint = prepend_if_not_in(epoint, TC_ENDPOINT_API)
    epoint = prepend_if_not_in(epoint, TC_ENDPOINT)
    return get(epoint, auth=tc_auth, headers=TC_HEADER)


def traverse_pages(epoint, tc_auth, callback):
    logging.debug('Calling {:}.'.format(epoint))
    data = get_tc(epoint, tc_auth)
    callback(data)
    if 'nextHref' in data:
        traverse_pages(data['nextHref'], tc_auth, callback)


def smalls_failures(tc_auth):
    data = get_tc('/app/rest/latest/buildTypes/id:bt205', tc_auth)

    stats = {'passed': 0, 'failed': 0, 'failures': []}
    def record_stats(data):
        for build in data['build']:            
            if build['status'] == 'SUCCESS':
                stats['passed'] += 1
            else:
                stats['failed'] += 1
                stats['failures'] += [build['number']]

    traverse_pages(data['builds']['href'], tc_auth, record_stats)
    return stats


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) is not 3:
        raise IOError('Needs TC username and password as arguments')
    tc_auth = (sys.argv[1], sys.argv[2])
    stats = smalls_failures(tc_auth)
    with open('smalls.json', 'w') as f:
        f.write(json.dumps(stats, indent=4))
    pass