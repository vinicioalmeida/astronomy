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


# Write your function median_FITS here:
import time, numpy as np
from astropy.io import fits

def median_fits(filenames):

  start = time.time()   # Start timer
  # Read in all the FITS files and store in list
  FITS_list = []
  for filename in filenames: 
    hdulist = fits.open(filename)
    FITS_list.append(hdulist[0].data)
    hdulist.close()

  # Stack image arrays in 3D array for median calculation
  FITS_stack = np.dstack(FITS_list)

  median = np.median(FITS_stack, axis=2)

  # Calculate the memory consumed by the data
  memory = FITS_stack.nbytes
  # or, equivalently:
  #memory = 200 * 200 * len(filenames) * FITS_stack.itemsize

  # convert to kB:
  memory /= 1024
  
  stop = time.time() - start   # stop timer
  return median, stop, memory



# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # Run your function with first example in the question.
  result = median_fits(['image0.fits', 'image1.fits'])
  print(result[0][100, 100], result[1], result[2])
  
  # Run your function with second example in the question.
  result = median_fits(['image{}.fits'.format(str(i)) for i in range(11)])
  print(result[0][100, 100], result[1], result[2])


# Write your median_bins and median_approx functions here.
import numpy as np

def median_bins(values, B):
  mean = np.mean(values)
  std = np.std(values)
    
  # Initialise bins
  left_bin = 0
  bins = np.zeros(B)
  bin_width = 2*std/B
    
  # Bin values
  for value in values:
    if value < mean - std:
      left_bin += 1
    elif value < mean + std:
      bin = int((value - (mean - std))/bin_width)
      bins[bin] += 1
    # Ignore values above mean + std

  return mean, std, left_bin, bins


def median_approx(values, B):
  # Call median_bins to calculate the mean, std,
  # and bins for the input values
  mean, std, left_bin, bins = median_bins(values, B)
    	
  # Position of the middle element
  N = len(values)
  mid = (N + 1)/2

  count = left_bin
  for b, bincount in enumerate(bins):
    count += bincount
    if count >= mid:
      # Stop when the cumulative count exceeds the midpoint
      break

  width = 2*std/B
  median = mean - std + width*(b + 0.5)
  return median



# You can use this to test your functions.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # Run your functions with the first example in the question.
  print(median_bins([1, 1, 3, 2, 2, 6], 3))
  print(median_approx([1, 1, 3, 2, 2, 6], 3))

  # Run your functions with the second example in the question.
  print(median_bins([1, 5, 7, 7, 3, 6, 1, 1], 4))
  print(median_approx([1, 5, 7, 7, 3, 6, 1, 1], 4))


  # Import the running_stats function
from helper import running_stats
# Write your median_bins_fits and median_approx_fits here:
import time, numpy as np
from astropy.io import fits
from helper import running_stats


def median_bins_fits(filenames, B):
  # Calculate the mean and standard dev
  mean, std = running_stats(filenames)
    
  dim = mean.shape # Dimension of the FITS file arrays
    
  # Initialise bins
  left_bin = np.zeros(dim)
  bins = np.zeros((dim[0], dim[1], B))
  bin_width = 2 * std / B 

  # Loop over all FITS files
  for filename in filenames:
      hdulist = fits.open(filename)
      data = hdulist[0].data

      # Loop over every point in the 2D array
      for i in range(dim[0]):
        for j in range(dim[1]):
          value = data[i, j]
          mean_ = mean[i, j]
          std_ = std[i, j]

          if value < mean_ - std_:
            left_bin[i, j] += 1
                
          elif value >= mean_ - std_ and value < mean_ + std_:
            bin = int((value - (mean_ - std_))/bin_width[i, j])
            bins[i, j, bin] += 1

  return mean, std, left_bin, bins


def median_approx_fits(filenames, B):
  mean, std, left_bin, bins = median_bins_fits(filenames, B)
    
  dim = mean.shape # Dimension of the FITS file arrays
    
  # Position of the middle element over all files
  N = len(filenames)
  mid = (N + 1)/2
	
  bin_width = 2*std / B
  # Calculate the approximated median for each array element
  median = np.zeros(dim)   
  for i in range(dim[0]):
    for j in range(dim[1]):    
      count = left_bin[i, j]
      for b, bincount in enumerate(bins[i, j]):
        count += bincount
        if count >= mid:
          # Stop when the cumulative count exceeds the midpoint
          break
      median[i, j] = mean[i, j] - std[i, j] + bin_width[i, j]*(b + 0.5)
      
  return median



# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # Run your function with examples from the question.
  mean, std, left_bin, bins = median_bins_fits(['image0.fits', 'image1.fits', 'image2.fits'], 5)
  median = median_approx_fits(['image0.fits', 'image1.fits', 'image2.fits'], 5)
