import sys, logging, requests, collections, enum
import common
import pandas as pd
import numpy as np


#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


def is_ecl2ix_with_duration(test):
    tc_test_name = test['name']
    if 'ecl2ix' in tc_test_name and 'duration' in test:
        return int(test['duration']) > 1
    return False


def extract_test_name(tc_test_name):
    #tc_test_name = tc_test_name.replace('RegressionTest: ', '')
    delim = '.'
    idx_first_dot = tc_test_name.find(delim)
    idx_second_dot = tc_test_name.find(delim, idx_first_dot+1)
    test_name = str(tc_test_name)
    if idx_first_dot != -1 and idx_second_dot != 1:
        test_name = tc_test_name[idx_first_dot+1:idx_second_dot]
    elif idx_first_dot != -1:
        test_name = tc_test_name[idx_first_dot+1:]
    return test_name


def is_valid_test_configuration(name_configuration):
    name_configuration = name_configuration.lower()
    if any(hot in name_configuration for hot in ['small', 'daily', 'tests', 'test', 'cvx', 'schedule', 'cases']):
        if any(cold in name_configuration for cold in ['coverage']):
            return False
        return True
    return False
    

########
# main #
########

categories = ['RollingBuilds_Tests', 'ScheduledBuilds', 'MemoryChecks']
test_effort_db = common.load_db()

for category in categories:
    rdata = common.get_tc('/projects/id:IntersectMain_' + category)
    print('Exploring category: {:}.'.format(rdata['name']))
    
    configurations = rdata['buildTypes']['buildType']
    num_max_configuration_builds_pages = 1
    num_max_build_tests_pages = None

    for configuration in configurations: # look for the tests build in question
        name_configuration = configuration['name']

        if not is_valid_test_configuration(name_configuration):
            continue

        test_type_configuration = common.detect_test_type(name_configuration)
        if test_type_configuration == common.TestType.UNIT:
            continue

        build_type = common.detect_build_type(name_configuration)
        if build_type.configuration == common.Configuration.DEBUG:
            continue 
        if build_type.instrumentation is not common.Instrumentation.NAKED:
            continue 

        print('.'*1, 'Found valid configuration: {:}.'.format(name_configuration))
        print('.'*2, 'Build type: {:}'.format(build_type))         


        def for_each_test(data_page):
            for test in data_page['testOccurrence']:
                if is_ecl2ix_with_duration(test):              
                    name_test = extract_test_name(test['name'])
                    if name_test in test_effort_db:
                        test_effort_db[name_test][common.IDX_DB_TIME_ECL2IX] = int(test['duration']/1000)
                    else:
                        print('NOT FOUND', test['name'], name_test)


        def for_each_configuration_builds_page(data_page):
            for ibuild, build in enumerate(data_page['build']):
                num_build = build['number']
                details_build = common.get_tc(build['href'])
                tests = common.get_tc(details_build['testOccurrences']['href'])
                common.traverse_linked_pages_tc(details_build['testOccurrences']['href'], for_each_test, 
                  num_max_pages=num_max_build_tests_pages)
                if ibuild > 4:
                    break # only first build
        

        details_configuration = common.get_tc(configuration['href'])
        common.traverse_linked_pages_tc(details_configuration['builds']['href'], for_each_configuration_builds_page, 
          num_max_pages=num_max_configuration_builds_pages)

        #break # only first build configuration
    
    #break # only first category


common.save_db(test_effort_db)


        

