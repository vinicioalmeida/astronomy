print('Hello, World!')

# Write your greet function definition below:

def greet(name):
  return 'Hello, '+name+'!'

# Any code inside the if statement will be ignored by the automarker.
# Put your test code in here, since it will be run by clicking Run or Terminal.
if __name__ == '__main__':
  print(greet('World'))
  print(greet('Grok'))
  print(greet('123'))


def calculate_mean(data):
  mean = sum(data)/len(data)
  return mean


from statistics import mean
fluxes = [23.3, 42.1, 2.0, -3.2, 55.6]
m = mean(fluxes)
print(m)


import numpy as np
def calc_stats(filename):
  data = np.loadtxt(filename, delimiter=',')
 
  mean = np.mean(data)
  median = np.median(data)

  return np.round(mean, 1), np.round(median, 1)


data = []
for line in open('data.csv'):
  row = []
  for col in line.strip().split(','):
    row.append(float(col))
  data.append(row)

print(data)


import numpy as np
data = []
for line in open('data.csv'):
  data.append(line.strip().split(','))

data = np.asarray(data, float)
print(data)

import numpy as np
data = np.loadtxt('data.csv', delimiter=',')
print(data)

#The NumPy loadtxt function is simpler, faster, and less error-prone than our previous solution. Use it!

calc_stats('data2.csv')
(11.4, 10.4)


# Write your mean_datasets function here
import numpy as np

def mean_datasets(filenames):
  n = len(filenames)
  if n > 0:
    data = np.loadtxt(filenames[0], delimiter=',')
    for i in range(1,n):
      data += np.loadtxt(filenames[i], delimiter=',')
    
    # Mean across all files:
    data_mean = data/n
     
    return np.round(data_mean, 1)


# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # Run your function with the first example from the question:
  print(mean_datasets(['data1.csv', 'data2.csv', 'data3.csv']))

  # Run your function with the second example from the question:
  print(mean_datasets(['data4.csv', 'data5.csv', 'data6.csv']))