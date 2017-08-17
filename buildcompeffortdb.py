import sys, logging, requests, collections
import common
import pandas as pd
import numpy as np


UNDEFINED = 'NA'

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


Configuration = collections.namedtuple('Configuration', 'platform num_processes num_threads')


class TCRegressionTestData:
    def __init__(self):
        # Test name as key, dicts as value with Configuration
        # as key and list of durations as value
        # e.g. _data['aim']['rh6_x86_64_gcc'].append(60)
        self._data = {}


def extract_test_name(tc_test_name):
    delim = '.'
    idx_first_dot = tc_test_name.find(delim)
    idx_second_dot = tc_test_name.find(delim, idx_first_dot+1)
    test_name = str(tc_test_name)
    if idx_first_dot != -1 and idx_second_dot != 1:
        test_name = tc_test_name[idx_first_dot+1:idx_second_dot]
    elif idx_first_dot != -1:
        test_name = tc_test_name[idx_first_dot+1:]
    return test_name
    

rdata = common.get_tc('/projects/id:IntersectMain_RollingBuilds_Tests')
name_tests_build = 'Rolling Run DAILY Tests RH6'
name_tests_build = 'Daily Run Small and Daily Tests without ge option PC'
name_tests_build = 'Rolling Run SMALL Tests PC'
name_tests_build = 'Rolling Run SMALL Tests RH6'
tests_builds = rdata['buildTypes']['buildType']
for tests_build in tests_builds: # look for the tests build in question
    if name_tests_build in tests_build['name']:
        logging.info('Found test build: {:}.'.format(tests_build['name']))
        break # we'll look into this
href_tests_build = tests_build['href']
tests_build = common.get_tc(href_tests_build)

num_max_build_pages = 1
num_max_test_pages = 1

def for_each_build_tests_page(pagedata):
    for test in pagedata['testOccurrence']:
        test_summary = common.get_tc(test['href'])
        test_name = extract_test_name(test_summary['name'])
        if 'ignored' in test_summary and test_summary['ignored']:
            continue
        print(test_summary['status'], test_name) 
        print(test_summary['test']['href'])
        test_details = common.get_tc(test_summary['test']['href'])
        print(test_details)
        break


def for_each_tests_build_builds_page(pagedata):
    for build in pagedata['build']:
        tests_overview = common.get_tc(build['href'])        
        tests_summary = common.get_tc(tests_overview['href'])        
        tests = common.get_tc(tests_summary['testOccurrences']['href'])
        common.traverse_linked_pages_tc(tests_summary['testOccurrences']['href'], 
          for_each_build_tests_page, num_max_pages=num_max_test_pages)        
        break # only first build

common.traverse_linked_pages_tc(tests_build['builds']['href'], for_each_tests_build_builds_page, 
  num_max_pages=num_max_build_pages)

