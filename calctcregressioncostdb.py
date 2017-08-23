import common
import cost
import logging, csv, math

HOST = 'http://slb-2cgbj32.dir.slb.com:8000'
API = '/devdiff/latest'
ENDPOINT = '/results/?page=1'
FNAME_DATA = 'data_tmp/evaldevdiffserv_data'
COST_PROC_SEC = 0.119/(60*60*2)

logging.basicConfig(level=logging.INFO)

first_page = HOST + API + ENDPOINT
num_max_pages = 1

test_effort_db = common.load_db()




def calc_test_effort(tests):
    num_max_processes = 0
    process_seconds = 0
    num_tests_missing = 0
    total_seconds = 0
    for test in tests:
        if test in test_effort_db:
            test_data = test_effort_db[test]
            num_max_processes = max(num_max_processes, test_data[common.IDX_DB_NUM_PROC])
            process_seconds += test_data[common.IDX_DB_TIME_IX] * test_data[common.IDX_DB_NUM_PROC]
            process_seconds += test_data[common.IDX_DB_TIME_ECL2IX]
            total_seconds += test_data[common.IDX_DB_TIME_IX] + test_data[common.IDX_DB_TIME_ECL2IX]
        elif test: # guard against empty
            num_tests_missing += 1
    
    cost_lower, cost_upper, msg = cost.google_compute(total_seconds, process_seconds, num_max_processes)
    print(msg, '{0:d} tests, {1:d} missing, between {2:.2f}-{3:.2f} USD.'.format(len(tests), num_tests_missing, cost_lower, cost_upper))


def for_each_results_page(rdata):
    for result in rdata['results']:
        tests = result['passed'].split(',')
        tests += result['failed'].split(',')
        tests += result['gold_diff'].split(',')
        calc_test_effort(tests)        
        #break # only last posted       

common.traverse_linked_pages(first_page, for_each_results_page, num_max_pages=num_max_pages)








