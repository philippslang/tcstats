import common

test_effort_db = common.load_db()
num_max_processes = 0

for name_deck in test_effort_db:
    num_max_processes  = max(test_effort_db[name_deck][common.IDX_DB_NUM_PROC], num_max_processes)

print(num_max_processes)