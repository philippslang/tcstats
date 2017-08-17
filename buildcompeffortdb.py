import sys, logging, requests, collections, enum
import common
import pandas as pd
import numpy as np


#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)


UNDEF = 'NA'


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


def detect_test_type(in_this_string):
    in_this_lc_string = in_this_string.lower()
    if common.contains_any_of(in_this_lc_string, ['unit']):
        return TestType.UNIT
    return TestType.REGRESSION


def detect_operating_system(in_this_lc_string):
    if common.contains_any_of(in_this_lc_string, ['pc', 'vs']):
        return System.WINDOWS
    return System.LINUX   


def detect_configuration(in_this_lc_string):
    if common.contains_any_of(in_this_lc_string, ['debug']):
        return Configuration.DEBUG
    return Configuration.RELEASE


def detect_instrumentation(in_this_lc_string):
    if common.contains_any_of(in_this_lc_string, ['valgrind']):
        return Instrumentation.VALGRIND
    if common.contains_any_of(in_this_lc_string, ['threadsanitizer']):
        return Instrumentation.TSAN
    if common.contains_any_of(in_this_lc_string, ['addresssanitizer']):
        return Instrumentation.ASAN
    if common.contains_any_of(in_this_lc_string, ['noge', 'without ge']):
        return Instrumentation.NOGE
    return Instrumentation.NAKED


def detect_build_type(in_this_string):
    in_this_lc_string = in_this_string.lower()
    osys = detect_operating_system(in_this_lc_string)
    config = detect_configuration(in_this_lc_string)
    instrument = detect_instrumentation(in_this_lc_string)
    return BuildType(osys, config, instrument)


class TCTestData:
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

categories = ['RollingBuilds_Builds', 'RollingBuilds_Tests', 'ScheduledBuilds', 'MemoryChecks']

for category in categories:
    rdata = common.get_tc('/projects/id:IntersectMain_' + category)
    print('Exploring category: {:}.'.format(rdata['name']))
    
    configurations = rdata['buildTypes']['buildType']
    num_max_configuration_builds_pages = 1

    for configuration in configurations: # look for the tests build in question
        name_configuration = configuration['name']

        if not is_valid_test_configuration(name_configuration):
            continue

        test_type_configuration = detect_test_type(name_configuration)
        if test_type_configuration == TestType.UNIT:
            continue

        print('.'*1, 'Found valid configuration: {:}.'.format(name_configuration))
        print('.'*2, 'Build type: {:}'.format(detect_build_type(name_configuration)))        

        def for_each_configuration_builds_page(data_page):
            for build in data_page['build']:
                num_build = build['number']
                details_build = common.get_tc(build['href'])
                # TC youtrack bug TW-51221
                href_build_artifcats = details_build['artifacts']['href'].replace('latest/latest', 'latest')
                artifacts = common.get_tc(href_build_artifcats)   
                if artifacts['count'] > 0:
                    for iartifact in range(artifacts['count']):
                        name_artifact = artifacts['file'][iartifact]['name']
                        print('.'*2, 'Found artifact {0:} @ {1:}'.format(name_artifact, num_build))
                        # TODO check if meaningful artiface and analyse, if not check duration
                else:
                    print('.'*2, 'Found no artifacts @ {0:}'.format(num_build))    
                    # TODO loop over tests, see if meaningful, use NA for run type
                break # only first build
        
        details_configuration = common.get_tc(configuration['href'])
        common.traverse_linked_pages_tc(details_configuration['builds']['href'], for_each_configuration_builds_page, 
          num_max_pages=num_max_configuration_builds_pages)

        break # only first build configuration





        

