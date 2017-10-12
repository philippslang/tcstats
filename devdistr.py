import common
import logging, sys
import datetime
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)



submissions = {}
with open('cl.txt', 'r') as file:
    for line in file: 
        tokens = line.split()        
        user = tokens[6].split('@')[0]
        if user in submissions:
            submissions[user] += 1
        else:
            submissions[user] = 1


users = list(submissions.keys())
count = [submissions[user] for user in users]
d = {'users': users, 'submissions': count}
df = pd.DataFrame(data=d)
df = df.sort_values('submissions')
print(df)


