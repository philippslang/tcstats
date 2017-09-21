import common, cost, fetchresults
import logging, sys
import numpy as np
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':

    
    test_names_to_query = sys.argv
    if len(sys.argv) < 2:
        print('provide test names as args')
        sys.exit()

    if 1:
        results = fetchresults.get_all_with_status()
        pickle.dump(results, open(r'data_tmp\resultsstatusinfo', 'wb'))
    else:
        results = pickle.load(open(r'data_tmp\resultsstatusinfo', 'rb'))


    for result in results:
        status = common.make_int_array(result['status'])
        duration_ix = common.make_int_array(result['duration_ix'])
        duration_ecl2ix = common.make_int_array(result['duration_ecl2ix'])
        num_processes_ix = common.make_int_array(result['num_processes_ix'])
        num_threads_ix = common.make_int_array(result['num_threads_ix'])
        vcpu_seconds_tests = num_threads_ix*num_processes_ix*duration_ix + duration_ecl2ix
        tests = result['tests'].split(',')
        cl = int(result['cl'])
        platform = result['platform']
        posted = result['posted']
        for i, test in enumerate(tests):
            if test in test_names_to_query:
                status = 'passed' if status[i] == 0 else 'failed'
                print('{0}: {7} @ {1:d} on {2}, {3:d} processes, {4:d} threads, duration ix {5:d}s, {6}'.format(test,
                  cl, platform, num_processes_ix[i], num_threads_ix[i], duration_ix[i], posted, status))
           










