
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