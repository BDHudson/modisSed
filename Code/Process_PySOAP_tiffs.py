# -*- coding: utf-8 -*-
"""
Created on Thu Aug 07 14:38:43 2014

@author: Ben Hudson
"""

# open TIFFS made by process_MODIS_pySOAP

#version 6/4/2013
# increased expected relationship tolerance from .025 to .03, also relaxed B2 max threshold to .17 from .13
 
import os
#import gdal
#from gdalconst import *
#import gdalnumeric
import pylab as plt
import scipy.ndimage
from scipy import stats
from scipy.interpolate import griddata
import numpy as np
import glob
import pickle

from pyhdf.SD import SD, SDC
import gdal
from gdalconst import *
import gdalnumeric
import arcpy
arcpy.env.overwriteOutput = True

#from osgeo import gdal
drv = gdal.GetDriverByName('GTiff')

import mpl_toolkits.basemap.pyproj as pyproj

# projection information 
wgs84 = pyproj.Proj("+init=EPSG:4326")
# this is correct for greenland 
#outputProjection = pyproj.Proj("+init=EPSG:32622")

# THIS IS REALLY UTM 10 NORTH (ELWAH) was "+init=EPSG:32610"
# THIS IS NOW EAST GREENLAND 
#outputProjection = pyproj.Proj("+init=EPSG:32626")
outputProjection = pyproj.Proj("+init=EPSG:3413")

# arc needs this. EPSG 3413 is WGS_1984_NSIDC_Sea_Ice_Polar_Stereographic_North
# can check that it worked by typing in sr.name
 
sr = arcpy.SpatialReference(3413)

def imshowwithZ(X):

    import matplotlib.cm as cm
    
    fig, ax = plt.subplots()
    ax.imshow(X, cmap=cm.spectral, interpolation='nearest')
    
    numrows, numcols = X.shape
    def format_coord(x, y):
        col = int(x+0.5)
        row = int(y+0.5)
        if col>=0 and col<numcols and row>=0 and row<numrows:
            z = X[row,col]
            return 'x=%1.4f, y=%1.4f, z=%1.4f'%(x, y, z)
        else:
            return 'x=%1.4f, y=%1.4f'%(x, y)
    
    ax.format_coord = format_coord
    #ax.set_cmap('spectral')
    
    
    plt.show()

# --------------------------------------------------

# NEED TO ALERT PROCESSOR IF MOD35 Version 006 is used instead of Version 005 because of the cloud detection and bit flags extracted... . This should be easy to do by reading the part of the hdf that says .005. 

# --------------------------------------------------
# --------------------------------------------------
# ALL USER INPUTS HERE 

fileDirectoryOUTPUT_Tiff = "F:\\NARWAL\\OUTPUT_TIFF\\"
fileList = []
fileCount = 0 

#LIST FILES IN FOLDER 
for files in os.listdir(fileDirectoryOUTPUT_Tiff):
            
            if files.endswith('.tif'):
                                  
                fileList.append(files)
                fileCount += 1

ticker = 0
                      
for f in fileList:           
    
    keep = 0
    
    # from http://geoinformaticstutorial.blogspot.com/2012/09/reading-raster-data-with-python-and-gdal.html
    dataset = gdal.Open( fileDirectoryOUTPUT_Tiff+f, GA_ReadOnly )                                
    
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    bands = dataset.RasterCount
    driver = dataset.GetDriver().LongName
    
    geotransform = dataset.GetGeoTransform() 
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    
    #
    band = dataset.GetRasterBand(1)

    data = band.ReadAsArray(0, 0, dataset.RasterXSize, dataset.RasterYSize).astype(np.float)

    # First time through the stack only has one layer
    
    plt.imshow(data)
    plt.show()
    
    keep = raw_input('keep?')
    
    if keep == '1':
        
        if ticker == 0:        
            dataStack = data
            ticker += 1 
        
        dataStack = np.dstack((dataStack,data))
    
    
    # close the dataset
    del dataset

# check shape of data stack         
print np.shape(dataStack)



# PLOTTING

dataMedian = stats.nanmedian(dataStack,axis=2)


plt.imshow(dataMedian)
dataMean = stats.nanmean(dataStack,axis=2)

dataMax = stats.nanmax(dataStack,axis=2)


# ROI info - used down around line 680  
n=76.5
s=73.25
e=-55.0
w=-62.0

outputProjection = pyproj.Proj("+init=EPSG:3413")
utm_e, utm_s = outputProjection(e,s)
utm_w, utm_n  = outputProjection(w,n)



sr = arcpy.SpatialReference(3413)
LL_corner_subset = arcpy.Point(utm_w,utm_s)
pixel_size = 250 # meters
        
outRaster = arcpy.NumPyArrayToRaster(dataMax,LL_corner_subset,pixel_size,pixel_size)
outASCII = fileDirectoryOUTPUT_Tiff+"max.txt"
outGEOTIFF = fileDirectoryOUTPUT_Tiff+"max.tif"                
arcpy.RasterToASCII_conversion(outRaster, outASCII)

# using GDAL TO TURN INTO GEOTIFF 
ds_in = gdal.Open(outASCII)
ds_out = drv.CreateCopy(outGEOTIFF, ds_in)
ds_in = None
ds_out = None    
# define the projection
arcpy.DefineProjection_management(outGEOTIFF,sr)  
