import requests
import localdata
import logging 
import enum
import string
import collections
import pickle
import numpy as np

TC_HEADER = {'Content-type': 'application/json', 'Accept': 'application/json'}
TC_AUTH = (localdata.USER, localdata.PW)
TC_ENDPOINT_API = '/app/rest/latest'
TC_ENDPOINT = localdata.TC
FNAME_DB = 'data_tmp/test_effort_db'

UNDEF = 'NA'


IDX_DB_TIME_IX = 0
IDX_DB_TIME_ECL2IX = 1
IDX_DB_NUM_PROC = 2


def make_int_array(string_csv):
    string_csv = string_csv.replace(UNDEF, '0')
    string_list = string_csv.split(',')
    return np.array([int(val) for val in string_list], dtype=np.int16)


def make_db_entry(run_time_ix_seconds, run_time_ecl2ix_seconds, num_processes):
    """
    Linked to indices above.
    """
    return [run_time_ix_seconds, run_time_ecl2ix_seconds, num_processes]


class System(enum.Enum):
    LINUX = 1
    WINDOWS = 2


class Configuration(enum.Enum):
    DEBUG = 1
    RELEASE = 2


class Instrumentation(enum.Enum):
    NAKED = 1
    VALGRIND = 2
    TSAN = 3
    ASAN = 4
    NOGE = 5


class TestType(enum.Enum):
    UNIT = 1
    REGRESSION = 2


BuildType = collections.namedtuple('BuildType', 'system configuration instrumentation')


RunType = collections.namedtuple('RunType', 'num_processes num_threads')


TestEffort = collections.namedtuple('TestEffort', 'run_time_ix run_time_ecl2ix num_processes')


def save_db(test_effort_db):
    pickle.dump(test_effort_db, open(FNAME_DB, 'wb'))


def load_db():
    return pickle.load(open(FNAME_DB, 'rb'))


def contains_any_of(inhere, oneofthese):
    if any(hot in inhere for hot in oneofthese):
        return True
    return False


def detect_test_type(in_this_string):
    in_this_lc_string = in_this_string.lower()
    if contains_any_of(in_this_lc_string, ['unit']):
        return TestType.UNIT
    return TestType.REGRESSION


def detect_operating_system(in_this_lc_string):
    if contains_any_of(in_this_lc_string, ['pc', 'vs']):
        return System.WINDOWS
    return System.LINUX   


def detect_configuration(in_this_lc_string):
    if contains_any_of(in_this_lc_string, ['debug']):
        return Configuration.DEBUG
    return Configuration.RELEASE


def detect_instrumentation(in_this_lc_string):
    if contains_any_of(in_this_lc_string, ['valgrind']):
        return Instrumentation.VALGRIND
    if contains_any_of(in_this_lc_string, ['threadsanitizer']):
        return Instrumentation.TSAN
    if contains_any_of(in_this_lc_string, ['addresssanitizer']):
        return Instrumentation.ASAN
    if contains_any_of(in_this_lc_string, ['noge', 'without ge']):
        return Instrumentation.NOGE
    return Instrumentation.NAKED


def detect_build_type(in_this_string):
    in_this_lc_string = in_this_string.lower()
    osys = detect_operating_system(in_this_lc_string)
    config = detect_configuration(in_this_lc_string)
    instrument = detect_instrumentation(in_this_lc_string)
    return BuildType(osys, config, instrument)


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
  auth=None, headers=None, getter=get, callback_args=[]):
    ipage += 1
    num_max_pages_put = 'all'
    if num_max_pages is not None:
        num_max_pages_put = str(num_max_pages)
    logging.info('Loading page {0:d} of {1} from {2}.'.format(ipage, num_max_pages_put, href_page))

    rdata = getter(href_page)
    if not callback_args:
        call_me_whith_rdata(rdata)
    else:
        call_me_whith_rdata(rdata, *callback_args)        

    if num_max_pages is None or ipage < num_max_pages: 
        if next_key in rdata and rdata[next_key] is not None:
            traverse_linked_pages(rdata[next_key], call_me_whith_rdata, num_max_pages=num_max_pages, 
              ipage=ipage, auth=None, headers=None, getter=getter, next_key=next_key, callback_args=callback_args)


def traverse_linked_pages_tc(href_page, call_me_whith_rdata, num_max_pages=None, ipage=0):
    return traverse_linked_pages(href_page, call_me_whith_rdata, num_max_pages=num_max_pages, ipage=ipage, 
      next_key='nextHref', auth=TC_AUTH, headers=TC_HEADER, getter=get_tc)