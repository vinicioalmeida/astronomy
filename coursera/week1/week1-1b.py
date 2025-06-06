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



# Write your mean_fits function here:
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
  data  = mean_fits(['image0.fits', 'image1.fits', 'image2.fits'])
  print(data[100, 100])

  # You can also plot the result:
  import matplotlib.pyplot as plt
  plt.imshow(data.T, cmap=plt.cm.viridis)
  plt.colorbar()
  plt.show()