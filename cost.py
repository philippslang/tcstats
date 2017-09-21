import math
import numpy as np

OVERHEAD_MIN_LO = 5
OVERHEAD_MIN_HI = 15

def google_compute(total_seconds, process_seconds, num_max_processes, platform):
    """
    TODO use googles json data
    https://cloudpricingcalculator.appspot.com/static/data/pricelist.json
    """
    num_max_processes += 2 # OS
    cost_per_hour = 0.0912
    if num_max_processes > 2:
        cost_per_hour = 0.1824
    if num_max_processes > 4:
        cost_per_hour = 0.3648
    if num_max_processes > 8:
        cost_per_hour = 0.7296
    if num_max_processes > 16:
        cost_per_hour = 1.4592
    if num_max_processes > 32:
        cost_per_hour = 2.9184
    cost_per_minute = cost_per_hour/60
    # ten min minimum, assume linear scaling etc...
    minutes_lower = math.ceil(process_seconds/(60. * num_max_processes))    
    minutes_upper = math.ceil(total_seconds/60.)    
    minutes_overtime_lower = max(0, minutes_lower - 10) 
    minutes_overtime_upper = max(0, minutes_upper - 10) 
    cost_basis_lower = 0. # image
    cost_basis_upper = 0. # image
    if 'rh' in platform:
        # RH premium
        if num_max_processes > 4:
            img_per_hr = 0.13
        else:
            img_per_hr = 0.06
        hours_lower = 1 + max(0, np.ceil((minutes_lower-60)/60))
        hours_upper = 1 + max(0, np.ceil((minutes_upper-60)/60))
        cost_basis_lower = img_per_hr * hours_lower
        cost_basis_upper = img_per_hr * hours_upper
    else:
        # windows server premium
        img_cost_per_min = 0.04*num_max_processes/60.
        cost_basis_lower = img_cost_per_min * (10 + minutes_overtime_lower)
        cost_basis_upper = img_cost_per_min * (10 + minutes_overtime_upper)
    cost_lower = cost_basis_lower + cost_per_minute * (10 + minutes_overtime_lower)
    cost_upper = cost_basis_upper + cost_per_minute * (10 + minutes_overtime_upper) 
    cost_lower_incl_one_run_overhead = cost_lower + cost_per_minute * OVERHEAD_MIN_LO
    cost_uppper_incl_one_run_overhead = cost_upper + cost_per_minute * OVERHEAD_MIN_HI
    # some pseudo currency math, rounding up to two decimals  
    cost = np.array([cost_lower, cost_upper, cost_lower_incl_one_run_overhead, cost_uppper_incl_one_run_overhead]) * 100.
    cost = np.floor(cost) / 100. + 0.01
    return cost
