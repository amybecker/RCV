import csv
import operator
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import stv
import scipy.stats as stats
import seaborn as sns




data_file_name = 'small_2014_mayoral_oakland.csv'

data = [[105 for x in range(21)] for y in range(21)]
with open(data_file_name) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        data[int(row[0])][int(row[1])] = float(row[17])

csv_file.close()


print(data)

ax = sns.heatmap(data, linewidth=0)
plt.show()