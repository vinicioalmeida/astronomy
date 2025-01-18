def calculate_mean(data):
  mean = sum(data)/len(data)
  return mean

# Mean with a function
from statistics import mean
fluxes = [23.3, 42.1, 2.0, -3.2, 55.6]
m = mean(fluxes)
print(m)

# Mean calculated manually
fluxes = [23.3, 42.1, 2.0, -3.2, 55.6]
m = sum(fluxes)/len(fluxes)
print(m)

# Numpy makes mean calculation in arrays, faster than in lists
import numpy as np
fluxes = np.array([23.3, 42.1, 2.0, -3.2, 55.6])
m = np.mean(fluxes)
print(m)

# Numpy offers other features
fluxes = np.array([23.3, 42.1, 2.0, -3.2, 55.6])
print(np.size(fluxes)) # length of array
print(np.std(fluxes))  # standard deviation

# Reading data stored as comma-separated values (CSV) in a file

data = []
for line in open('C:/repo/astronomy/data.csv'):
  data.append(line.strip().split(','))

print(data)

# Store the data in lists

data = []
for line in open('C:/repo/astronomy/data.csv'):
  row = []
  for col in line.strip().split(','):
    row.append(float(col))
  data.append(row)

print(data)

# Store in lists, converting to float with NumPy

import numpy as np

data = []
for line in open('C:/repo/astronomy/data.csv'):
  data.append(line.strip().split(','))

data = np.asarray(data, float)
print(data)

# With NumPy function loadtxt

import numpy as np
data = np.loadtxt('C:/repo/astronomy/data.csv', delimiter=',')
print(data)

# A solution to calculate mean and median

import numpy as np

def calc_stats(filename):
  data = np.loadtxt(filename, delimiter=',')
 
  mean = np.mean(data)
  median = np.median(data)

  return np.round(mean, 1), np.round(median, 1)

calc_stats('C:/repo/astronomy/data2.csv')