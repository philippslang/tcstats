import common, sys
test_effort_db = common.load_db()
num_max_processes = 0

for name_deck in test_effort_db:
    num_max_processes  = max(test_effort_db[name_deck][common.IDX_DB_NUM_PROC], num_max_processes)

print('Num max processes', num_max_processes)

tests_to_query = sys.argv

if len(tests_to_query) > 1:
    for test_to_query in tests_to_query[1:]:
        if test_to_query in test_effort_db:
            print(test_to_query, test_effort_db[test_to_query])
        else:
            print('{} not in DB'.format(test_to_query))
