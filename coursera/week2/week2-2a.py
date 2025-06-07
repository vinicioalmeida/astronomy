
'''
When investigating astronomical objects, like active galactic nuclei (AGN), astronomers compare 
data about those objects from different telescopes at different wavelengths. This requires positional 
cross-matching to find the closest counterpart within a given radius on the sky. In this activity you'll 
cross-match two catalogues: one from a radio survey, the AT20G Bright Source Sample (BSS) catalogue and 
one from an optical survey, the SuperCOSMOS all-sky galaxy catalogue. The BSS catalogue lists the 
brightest sources from the AT20G radio survey while the SuperCOSMOS catalogue lists galaxies observed by 
visible light surveys. If we can find an optical match for our radio source, we are one step closer to 
working out what kind of object it is, e.g. a galaxy in the local Universe or a distant quasar. We've 
chosen one small catalogue (BSS has only 320 objects) and one large one (SuperCOSMOS has about 240 million) 
to demonstrate the issues you can encounter when implementing cross-matching algorithms.

'''
# Write your hms2dec and dms2dec functions here
def hms2dec(h, m, s):
  return 15*(h + m/60 + s/3600)

def dms2dec(d, m, s):
  if d < 0:
    sign = -1
  else:
    sign = 1
  return sign*(abs(d) + m/60 + s/3600)


# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # The first example from the question
  print(hms2dec(23, 12, 6))

  # The second example from the question
  print(dms2dec(22, 57, 18))

  # The third example from the question
  print(dms2dec(-66, 5, 5.1))


# Write your angular_dist function here.

import numpy as np

def angular_dist(RA1, dec1, RA2, dec2):
  # Convert to radians
  r1 = np.radians(RA1)
  d1 = np.radians(dec1)
  r2 = np.radians(RA2)
  d2 = np.radians(dec2)

  a = np.sin(np.abs(d1 - d2)/2)**2
  b = np.cos(d1)*np.cos(d2)*np.sin(np.abs(r1 - r2)/2)**2

  angle = 2*np.arcsin(np.sqrt(a + b))
    
  # Convert back to degrees
  return np.degrees(angle)
  
# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # Run your function with the first example in the question.
  print(angular_dist(21.07, 0.1, 21.15, 8.2))

  # Run your function with the second example in the question
  print(angular_dist(10.3, -3, 24.3, -29))

###
# Write your import_bss function here.
import numpy as np

def hms2dec(hr, m, s):
  dec = hr + m/60 + s/3600
  return dec*15

def dms2dec(d, m, s):
  sign = d/abs(d)
  dec = abs(d) + m/60 + s/3600
  return sign*dec

def import_bss():
  res = []
  data = np.loadtxt('C:/repo/astronomy/coursera/week2/bss.dat', usecols=range(1, 7))
  for i, row in enumerate(data, 1):
    res.append((i, hms2dec(row[0], row[1], row[2]), dms2dec(row[3], row[4], row[5])))
  return res

def import_super():
  data = np.loadtxt('C:/repo/astronomy/coursera/week2/super.csv', delimiter=',', skiprows=1, usecols=(0, 1))
  res = []
  for i, row in enumerate(data, 1):
    res.append((i, row[0], row[1]))
  return res



# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  # Output of the import_bss and import_super functions
  bss_cat = import_bss()
  super_cat = import_super()
  print(bss_cat)
  print(super_cat)


##
## Look around
# Write your find_closest function here
import numpy as np

def hms2dec(hr, m, s):
  dec = hr + m/60 + s/3600
  return dec*15

def dms2dec(d, m, s):
  sign = d/abs(d)
  dec = abs(d) + m/60 + s/3600
  return sign*dec

def import_bss():
  res = []
  data = np.loadtxt('C:/repo/astronomy/coursera/week2/bss2.dat', usecols=range(1, 7))
  for i, row in enumerate(data, 1):
    res.append((i, hms2dec(row[0], row[1], row[2]), dms2dec(row[3], row[4], row[5])))
  return res

def import_super():
  data = np.loadtxt('C:/repo/astronomy/coursera/week2/super.csv', delimiter=',', skiprows=1, usecols=[0, 1])
  res = []
  for i, row in enumerate(data, 1):
    res.append((i, row[0], row[1]))
  return res

def angular_dist(ra1, dec1, ra2, dec2):
  # Convert to radians
  r1 = np.radians(ra1)
  d1 = np.radians(dec1)
  r2 = np.radians(ra2)
  d2 = np.radians(dec2)

  a = np.sin(np.abs(d1 - d2)/2)**2
  b = np.cos(d1)*np.cos(d2)*np.sin(np.abs(r1 - r2)/2)**2

  angle = 2*np.arcsin(np.sqrt(a + b))
    
  # Convert back to degrees
  return np.degrees(angle)

def find_closest(cat, ra, dec):
  min_dist = np.inf
  min_id = None
  for id1, ra1, dec1 in cat:
    dist = angular_dist(ra1, dec1, ra, dec)
    if dist < min_dist:
      min_id = id1
      min_dist = dist
    
  return min_id, min_dist



# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  cat = import_bss()
  
  # First example from the question
  print(find_closest(cat, 175.3, -32.5))

  # Second example in the question
  print(find_closest(cat, 32.2, 40.7))


#Now find more!

# Write your crossmatch function here.
import numpy as np

def hms2dec(hr, m, s):
  dec = hr + m/60 + s/3600
  return dec*15

def dms2dec(d, m, s):
  sign = d/abs(d)
  dec = abs(d) + m/60 + s/3600
  return sign*dec

def import_bss():
  res = []
  data = np.loadtxt('C:/repo/astronomy/coursera/week2/bss2.dat', usecols=range(1, 7))
  for i, row in enumerate(data, 1):
    res.append((i, hms2dec(row[0], row[1], row[2]), dms2dec(row[3], row[4], row[5])))
  return res

def import_super():
  data = np.loadtxt('C:/repo/astronomy/coursera/week2/super2.csv', delimiter=',', skiprows=1, usecols=[0, 1])
  res = []
  for i, row in enumerate(data, 1):
    res.append((i, row[0], row[1]))
  return res

def find_closest(cat, ra, dec):
  min_dist = np.inf
  min_id = None
  for id1, ra1, dec1 in cat:
    dist = angular_dist(ra1, dec1, ra, dec)
    if dist < min_dist:
      min_id = id1
      min_dist = dist
    
  return min_id, min_dist


####

def angular_dist(RA1, dec1, RA2, dec2):
    # Convert to radians
    r1 = np.radians(RA1)
    d1 = np.radians(dec1)
    r2 = np.radians(RA2)
    d2 = np.radians(dec2)
    
    deltar = np.abs(r1 - r2)
    deltad = np.abs(d1 - d2)
    angle = 2*np.arcsin(np.sqrt(np.sin(deltad/2)**2 
                        + np.cos(d1)*np.cos(d2)*np.sin(deltar/2)**2))
    
    # Convert back to degrees
    return np.degrees(angle)

def crossmatch(cat1, cat2, max_radius):
    matches = []
    no_matches = []
    for id1, ra1, dec1 in cat1:
        closest_dist = np.inf
        closest_id2 = None
        for id2, ra2, dec2 in cat2:
            dist = angular_dist(ra1, dec1, ra2, dec2)
            if dist < closest_dist:
                closest_id2 = id2
                closest_dist = dist
        
        # Ignore match if it's outside the maximum radius
        if closest_dist > max_radius:
            no_matches.append(id1)
        else:
            matches.append((id1, closest_id2, closest_dist))

    return matches, no_matches


# You can use this to test your function.
# Any code inside this `if` statement will be ignored by the automarker.
if __name__ == '__main__':
  bss_cat = import_bss()
  super_cat = import_super()

  # First example in the question
  max_dist = 40/3600
  matches, no_matches = crossmatch(bss_cat, super_cat, max_dist)
  print(matches[:3])
  print(no_matches[:3])
  print(len(no_matches))

  # Second example in the question
  max_dist = 5/3600
  matches, no_matches = crossmatch(bss_cat, super_cat, max_dist)
  print(matches[:3])
  print(no_matches[:3])
  print(len(no_matches))


