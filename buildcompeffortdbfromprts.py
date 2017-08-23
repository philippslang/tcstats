import sys, logging, requests, collections, enum, glob, re
import recompiled
import common
import pandas as pd
import numpy as np


def l():
    sys.exit()

#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)

debug = 0
if debug:
    path_prts = []
    path_prts.append(r'E:\perforce\workspaces\plang_regtests\IX\Branch\Main\RegressionTest\small\aim\Gold\aim.prt')
    path_prts.append(r'E:\perforce\workspaces\plang_regtests\IX\Branch\Main\RegressionTest\weekly\ZADCO-HM\Gold\ZADCO-HM.PRT')
    path_prts.append(r'E:\perforce\workspaces\plang_regtests\IX\Branch\Main\RegressionTest\weekly\WHEATSTONE\Gold\WHEATSTONE.PRT')
    path_prts.append(r'E:\perforce\workspaces\plang_regtests\IX\Branch\Main\RegressionTest\weekly\TengizDP\Gold\TengizDP.PRT')
    path_prts.append(r'E:\perforce\workspaces\plang_regtests\IX\Branch\Main\RegressionTest\small\wm_ix_comp\Gold\wm_ix_comp.PRT')
    path_prts.append(r'E:\perforce\workspaces\plang_regtests\IX\Branch\Main\RegressionTest\scal\SCAL_VERBOSITY_JFUNCTION\Gold\SCAL_VERBOSITY_JFUNCTION.PRT')
    for path_prt in path_prts:
        with open(path_prt, 'r') as file_prt:
                string_prt = file_prt.read()
                run_time_seconds = recompiled.parse_run_time(string_prt)
                name_deck = recompiled.parse_deck_name(string_prt)
                num_processes = recompiled.parse_num_processes(string_prt)
                print(name_deck, num_processes, run_time_seconds)
            
    l()

test_effort = {}

path_base_dir = 'E:/perforce/workspaces/plang_regtests/IX/Branch/Main/RegressionTest'

def skip(path_sub_prt):
    print('|====== SKIPPING ======>{}'.format(path_sub_prt))

for fname_prt in glob.iglob(path_base_dir + '/**/*.prt', recursive=True):

    path_sub_prt = fname_prt.replace(path_base_dir, '')

    if 'Gold' not in fname_prt or 'ECL2IX' in path_sub_prt:
        #skip(path_sub_prt)
        continue
            
    with open(fname_prt, 'r') as file_prt:
        string_prt = file_prt.read()        
        try:
            name_deck = recompiled.parse_deck_name(string_prt)
            run_time_seconds = recompiled.parse_run_time(string_prt)
            num_processes = recompiled.parse_num_processes(string_prt)
            i_start_test_name = path_sub_prt.find('\\', 1) + 1
            i_end_test_name = path_sub_prt.find('\\', i_start_test_name)
            name_test = path_sub_prt[i_start_test_name:i_end_test_name]

        except:
            skip(path_sub_prt)
            continue    

        if 1:
            print('\'{0}\' ({1})'.format(name_test, path_sub_prt))
            print('.'*1, 'Runtime: {:d} (s)'.format(run_time_seconds))
            print('.'*1, 'Processes: {:d}'.format(num_processes)) 
            print('.'*1, 'PRT deck: \'{}\''.format(name_deck)) 

        test_effort[name_test] = common.make_db_entry(run_time_seconds, 0, num_processes)

common.save_db(test_effort)

