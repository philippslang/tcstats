import sys
import requests
import localdata
import pandas as pd
import numpy as np

headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
auth = (localdata.USER, localdata.PW)
ENDPOINT_API = '/app/rest/latest'


def endpoint(relepoint):
    endpoint_api = ENDPOINT_API
    if endpoint_api in relepoint:
        endpoint_api = ''
    return localdata.TC + endpoint_api + relepoint  


def get(relepoint):
    ept = endpoint(relepoint)
    resp = requests.get(ept, auth=auth, headers=headers)
    return resp.json()


def traverse_linked_pages(href_page, call_me_whith_rdata, num_max_pages=None, ipage=0, verbose=0):
    ipage += 1
    if verbose > 0:
        num_max_pages_put = 'all'
        if num_max_pages is not None:
            num_max_pages_put = str(num_max_pages)
        print('Loading page {0:d} of {1}'.format(ipage, num_max_pages_put))
    rdata = get(href_page)
    call_me_whith_rdata(rdata)
    
    if num_max_pages is None or ipage < num_max_pages: 
        if 'nextHref' in rdata:
            traverse_linked_pages(rdata['nextHref'], call_me_whith_rdata, num_max_pages=num_max_pages, 
              ipage=ipage, verbose=verbose)


if 0:
    rdata = get('/projects/id:IntersectMain')
    print(rdata.keys())
    print(rdata['projects']['project'])


if 0:
    rdata = get('/projects/id:IntersectMain_RollingBuilds_Builds')
    #print(rdata.keys())
    print(rdata['buildTypes'])


if 0:
    rdata = get('/buildTypes/id:IntersectMain_P1b01RollingBuildPc')
    #print(rdata)
    print(rdata.keys())
    print(rdata['builds'])


if 0:
    rdata = get('/buildTypes/id:IntersectMain_P1b01RollingBuildPc/builds/')
    #print(rdata)
    #print(rdata.keys())
    print(rdata['build'][0])


if 0:
    rdata = get('/projects/id:IntersectMain_RollingBuilds_Tests')
    #print(rdata.keys())
    print(rdata['buildTypes']['buildType'][0])


if 0:
    rdata = get('/buildTypes/id:bt201')
    print(rdata.keys())
    print(rdata['builds'])


if 0:
    rdata = get('/buildTypes/id:bt201/builds')
    print(rdata.keys())
    print(rdata['build'][0])


if 0:
    rdata = get('/app/rest/latest/builds/id:4112100')
    print(rdata.keys())
    print(rdata['statistics'])


if 0:
    rdata = get('/app/rest/latest/builds/id:4112100/statistics')
    print(rdata.keys())
    #print(rdata['statistics'])


if 1:
    rdata = get('/projects/id:IntersectMain_RollingBuilds_Tests')
    name_test_build = 'Daily Run Small and Daily Tests without ge option PC'
    builds = rdata['buildTypes']['buildType']
    for build in builds: # look for the test build in question
        if name_test_build in build['name']:
            break # we'll look into this
    href_test_build = build['href']
    rdata = get(href_test_build)        
    href_test_build_builds = rdata['builds']['href']    

    num_max_test_build_builds_pages = 20#None
    num_max_test_build_tests_pages = None
    num_max_failures = 750

    test_failures = {'test': [], 'cl': [], 'duration': []}
    build_failures = {'cl': [], 'failures': []}
    build_count = [0, 0, 0]

    def traverse_test_build_build_tests(rdata):
        for test in rdata['testOccurrence']:
            if 'FAILURE' in test['status']:
                #print(test.keys())
                test_rdata = get(test['href'])
                #print(test_rdata.keys())  
                duration = 1 # default for diff
                if 'duration' in test:
                    duration = test['duration']
                test_failures['test'] += [test['name']]
                test_failures['cl'] += [test_rdata['build']['number']]
                test_failures['duration'] += [duration]
                #print(test['name'], test_rdata['build']['number'], duration)      

    def traverse_test_build_builds_pages(rdata):
        test_build_builds = rdata['build']        
        for test_build_build in test_build_builds:
            build_count[0] += 1
            if 'FAILURE' in test_build_build['status']:  
                build_count[1] += 1              
                test_build_build_rdata = get(test_build_build['href'])
                if 'testOccurrences' in test_build_build_rdata:
                    if 'failed' in test_build_build_rdata['testOccurrences']:
                        cl = test_build_build['number']
                        num_failed = test_build_build_rdata['testOccurrences']['failed']
                        build_failures['cl'] += [cl]
                        build_failures['failures'] += [num_failed]
                        build_count[2] += 1
                        if num_failed <= num_max_failures:
                            print('CL', cl, 'failed', num_failed)
                            traverse_linked_pages(test_build_build_rdata['testOccurrences']['href'], 
                                traverse_test_build_build_tests, num_max_pages=num_max_test_build_tests_pages)

    traverse_linked_pages(href_test_build_builds, traverse_test_build_builds_pages, 
      num_max_pages=num_max_test_build_builds_pages, verbose=1)

    print('{0:d} total builds, {1:d} failed, {2:d} used.'.format(*build_count))
    df = pd.DataFrame(data=test_failures)
    df.to_csv('data_tmp/test_failures.csv')
    df = pd.DataFrame(data=build_failures)
    df.to_csv('data_tmp/build_failures.csv')
        
    

