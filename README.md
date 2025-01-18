# Data-Driven Astronomy
Professor Tara Murphy

## Additional resources

### Links to Advanced Crossmatching Papers
Here's a couple of really cool papers on probabilistic cross-matching that Tara mentioned at the end of Module 2:
Budavati & Szalay (2008) - https://arxiv.org/abs/0707.1611

Line et al. (2017) - https://arxiv.org/abs/1611.05534
 and his
 source code - https://github.com/JLBLine/PUMA
 for the the cross-matcher.

### Larger datasets for stacking
Contained in this resource are additional datasets to perform stacking with. Running the code on a large number of FITS files illustrates the difference in results between the different methods of stacking, like mean, median, and binapprox median.

pulsar_example_fits_1000 has 1000 example images centred on faint pulsars not able to be seen in individual images. This dataset should be sufficient to illustrate all the differences between the three methods of stacking, but is small enough (164 MB) to hold in memory on most modern computers.

pulsar_example_fits_7330 is similar to pulsar_example_fits_1000, but has 7330 images centred on faint pulsars. This dataset is >1GB in size, so only perform mean or median stacking with this dataset if your computer has sufficient RAM specifications.

rand_pos_example_fits contains a large number (~9500) of images centred at random locations, so you can see the effect of stacking when not centred on any real emission. Similar to pulsar_example_fits_7330, this dataset is > 1GB in size so please be wary when running your mean or median stacking code on this dataset. If you want a less compute-intensive illustration, perhaps selecting the first 500 or 1000 examples would be sufficient to illustrate the effect.


### Useful links for magnitudes/SDSS filters
The following links are give useful explanations relevant to the SDSS systems, including the camera system, the photometric filters, and the way visual magnitudes are calculated for each object.

http://voyages.sdss.org/preflight/light/filters/

http://www.sdss.org/instruments/camera/

http://voyages.sdss.org/preflight/light/magnitude/

http://voyages.sdss.org/preflight/light/magnitude-calculation/


Introduction to Pulsars 
https://www.atnf.csiro.au/projects/science/pulsars/
https://www.cv.nrao.edu/~sransom/web/Ch6.html

MWA
https://www.mwatelescope.org/

Images
https://sites.google.com/cfa.harvard.edu/saoimageds9/home
https://aladin.cds.unistra.fr/


MODULE 1 READING
All of these readings are completely optional. They are provided in case you are interested in reading further on the topics covered in this module.

1 Introductory pulsar material

Introduction to Pulsars (from CSIRO, beginner) Hobbs, M. (n.d.). An introduction to pulsars. Retrieved February 14, 2017, from 
http://www.atnf.csiro.au/outreach/education/everyone/pulsars/index.html
 

Access options: open access

 Pulsar Properties (from NRAO, advanced) National Radio Astronomy Observatory. (2010).  Pulsar Properties. Retrieved February 14, 2017, from 
http://www.cv.nrao.edu/course/astr534/Pulsars.html

Access options: open access

2 Introductory programming and statistics material

There are plenty of resources online for learning programming, but if you’d like a “textbook”, on option we recommend is:

Introduction to Python (O’Reilly)                                                                                                                                           McKellar, J. (2014). Introduction to Python. Retrieved from 
http://shop.oreilly.com/product/110000448.do

Access options: 10- day free access through Safari. $79.99 to purchase complete resource

Practical statistics for astronomers                                                                                                                                                 (An excellent book that covers a wide range of statistical techniques for astronomers)                                                     Wall, J. V., & Jenkins, C. R. (2012).
Practical statistics for astronomers
 (Second ed.). Cambridge: Cambridge University Press. 

Access options: £35.99. 

Additional material located here: Department of Physics and Astronomy, University of British Columbia. (n.d.). Practical Statistics for Astronomers. Retrieved from 
http://www.astro.ubc.ca/people/jvw/ASTROSTATS/
 

3 Research papers

This is advanced (graduate-level) astronomy material for people who want to read more about the use of image stacking in astronomy research.

Image stacking to detect quasars                                                                                                                                               White, R. L., Helfand, D. J., Becker, R. H., Glikman, E., & de Vries, W. (2007). Signals from the noise: Image stacking for quasars in the FIRST survey. The Astrophysical Journal, 654(1), 99-114. 
doi:10.1086/507700

Access options: open access

Stacking of radio images to study faint, high-redshift galaxies

Lindroos, L., Knudsen, K., Vlemmings, W., Conway, J., Marti-Vidal, I. (2015). Stacking of large interferometric data sets in the image- and uv-domain - a comparative study. Monthly Notices of the Royal Astronomical Society, 446(4), 3502-3515. doi:
10.1093/mnras/stu2344

Access options: open access

Radio visibility stacking to search for Type 1a supernova                                                                                                 Hancock, P. P., Gaensler, B. M., & Murphy, T. (2011). Visibility stacking in the quest for type ia supernova radio emission. Astrophysical Journal Letters, 735(2) doi:
10.1088/2041-8205/735/2/L35

Access options: open access



