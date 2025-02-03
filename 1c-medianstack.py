from statistics import mean
fluxes = [17.3, 70.1, 22.3, 16.2, 20.7]
m = mean(fluxes)
print(m)

from statistics import median
fluxes = [17.3, 70.1, 22.3, 16.2, 20.7]
m = median(fluxes)
print(m)

# median without the package
#odd number of elements
fluxes = [17.3, 70.1, 22.3, 16.2, 20.7]
fluxes.sort()
mid = len(fluxes)//2
median = fluxes[mid]
print(median)

#even number of elements
fluxes = [17.3, 70.1, 22.3, 16.2, 20.7, 19.3]
fluxes.sort()
mid = len(fluxes)//2
median = (fluxes[mid - 1] + fluxes[mid])/2
print(median)


# Write your list_stats function here.
import numpy as np

def list_stats(values):
    
    N = len(values)
    if N == 0:
       return

    # Mean
    mean = sum(values)/N

    # Median
    values.sort()
    mid = int(N/2)
    if N%2 == 0:
        median = (values[mid] + values[mid - 1])/2
    else:
        median = values[mid]

    return median, mean


# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # Run your function with the first example in the question.
  m = list_stats([1.3, 2.4, 20.6, 0.95, 3.1, 2.7])
  print(m)

  # Run your function with the second example in the question
  m = list_stats([1.5])
  print(m)


# Measuring execution time
import time
start = time.perf_counter()
# potentially slow computation
end = time.perf_counter() - start

import time, numpy as np
n = 10**7
data = np.random.randn(n)

start = time.perf_counter()
mean = sum(data)/len(data)
seconds = time.perf_counter() - start

print('That took {:.2f} seconds.'.format(seconds))

#now with NumPy
import time, numpy as np
n = 10**7
data = np.random.randn(n)

start = time.perf_counter()
mean = np.mean(data)
seconds = time.perf_counter() - start

print('That took {:.2f} seconds.'.format(seconds))

# Now a function to compare
import numpy as np
import statistics
import time

def time_stat(func, size, ntrials):
  total = 0
  for i in range(ntrials):
    data = np.random.rand(size)
    start = time.perf_counter()
    res = func(data)
    total += time.perf_counter() - start
  return total/ntrials

if __name__ == '__main__':
  print('{:.6f}s for statistics.mean'.format(time_stat(statistics.mean, 10**6, 10)))
  print('{:.6f}s for np.mean'.format(time_stat(np.mean, 10**6, 10)))


# Beyond time
import sys

a = 3
b = 3.123
c = [a, b]
d = []
for obj in [a, b, c, d]:
  print(obj, sys.getsizeof(obj))