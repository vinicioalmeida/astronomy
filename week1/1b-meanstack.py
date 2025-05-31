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

# Working with FITS files - Flexible Image Transport System
from astropy.io import fits

hdulist = fits.open('C:/repo/astronomy/image0.fits')
hdulist.info()

# Access image data
hdulist = fits.open('C:/repo/astronomy/image0.fits')
data = hdulist[0].data
print(data.shape)

# Produce the image
from astropy.io import fits
import matplotlib.pyplot as plt
hdulist = fits.open('C:/repo/astronomy/image0.fits')
data = hdulist[0].data
# Plot the 2D array
plt.imshow(data, cmap=plt.cm.viridis)
plt.xlabel('x-pixels (RA)')
plt.ylabel('y-pixels (Dec)')
plt.colorbar()
plt.show()


# The load_fits function:
from astropy.io import fits
import numpy as np

filename = 'C:/repo/astronomy/image3.fits'

def load_fits(filename):
  hdulist = fits.open(filename)
  data = hdulist[0].data

  arg_max = np.argmax(data)  
  max_pos = np.unravel_index(arg_max, data.shape)
  
  return max_pos

load_fits(filename)

hdulist = fits.open('C:/repo/astronomy/image3.fits')
data = hdulist[0].data

if __name__ == '__main__':
  
  # Test your function with examples from the question
 
  # You can also plot the result:
  import matplotlib.pyplot as plt
  plt.imshow(data.T, cmap=plt.cm.viridis)
  plt.colorbar()
  plt.show()


# Finally, the mean_fits function

from astropy.io import fits
import numpy as np

def mean_fits(files):
  n = len(files)
  if n > 0:
    
    hdulist = fits.open(files[0])
    data = hdulist[0].data
    hdulist.close()
    
    for i in range(1, n):
      hdulist = fits.open(files[i])
      data += hdulist[0].data
      hdulist.close()
    
    mean = data / n
    return mean



if __name__ == '__main__':
  
  # Test your function with examples from the question
  data  = mean_fits(['C:/repo/astronomy/image0.fits', 'C:/repo/astronomy/image1.fits', 'C:/repo/astronomy/image2.fits'])
  print(data[100, 100])

  # You can also plot the result:
  import matplotlib.pyplot as plt
  plt.imshow(data.T, cmap=plt.cm.viridis)
  plt.colorbar()
  plt.show()