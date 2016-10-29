# process_MODIS_pySOAP+subset_v12_clean.py
# increased expected relationship tolerance 
# from .025 to .03, also relaxed B2 max threshold to .17 from .13
 
import os
import pylab as plt
import scipy.ndimage
import numpy as np
import glob
import pickle
from scipy.interpolate import griddata
from pyhdf.SD import SD, SDC
import gdal
from gdalconst import *
import gdalnumeric

import mpl_toolkits.basemap.pyproj as pyproj

# projection information 

wgs84 = pyproj.Proj("+init=EPSG:4326")
utm22n = pyproj.Proj("+init=EPSG:32622")



# --------------------------------------------------

# NEED TO ALERT PROCESSOR IF MOD35 Version 006 is used 
# instead of Version 005 because of the cloud detection 
# and bit flags extracted... . This should be easy to 
# do by reading the part of the hdf that says .005. 

# --------------------------------------------------
# --------------------------------------------------
# ALL USER INPUTS HERE 

# tell it where the master directory is 
master_directory = 'F:\\MARCH2013RUN\\'

# tell it what FJORD
# K, N or P
fjord = 'K' 

# or tell it a list of strings for multiple years 
year_list = ['2012','2011','2010','2009','2008','2007'] 

# 2012 - 2000 for Kanger [157,155,159,144,154,
#                          143,156,148,155,152,153,159,160,159]
day_start_list = [155,159,144,154,143,156]

# 2012 - 2000 for Pak 
# day_start_list = [155,166] 
# [174,155,166,144,156,149,165,152,155,151,144,157,165,162]

#2005-2012 for Pak 
#day_start_list = [155,151,144,157,165,162]

# For NUUK 
#day_start_list = [135,135,135] 
#,135,135,135,135,135,135,135,135,135,135,135,135]


# first time running this directory?  1 is yes, 0 is no - as an interger
first_time = 0

# tell it what scene to start on THIS DOES NOT CORRESPOND TO DAY OF THE YEAR
# LEAVE THIS ZERO ! IT IS SUPERCEDED BY day_start_list
scene_start = 0

# pak - 2011 start on 137 
# Kang- 2012 start on 6 - THIS IS MISSING A LOT OF IMAGERY
# Nuuk 2012 start at zero

# save an ArcGIS raster every
dump_raster = 50

# Tell it the maximum solar zenith angle you allow.
# SZA is measured from the Zentih (strait up) down to the horizon
# ie the horizon is SZA of 90 degrees 
# in degreees 
max_allowed_SZA = 60. 



# --------------------------------------------------
# --------------------------------------------------

for year in year_list:

    #This saves a .mat file that both python and matlab can access 
    # Python automatically combines two strings when in succession
    saveAs = "Z:\\Documents\\WRITE UPS\\PEER REVIEWED PAPERS\\SSC\\satelliteRuns\\"+fjord+"_"+year+"_StS_swath_cube_OCT_30_2013"

    fileDirectory = master_directory+fjord+'\\'+year+'\\'
    
    # Terra 
    MOD02_fileCount = 0 
    MOD03_fileCount = 0 
    MOD35_fileCount = 0 
    
    MOD02_fileList = [] 
    MOD03_fileList = [] 
    MOD35_fileList = [] 
    
    # Aqua 
    MYD02_fileCount = 0 
    MYD03_fileCount = 0 
    MYD35_fileCount = 0 
    
    MYD02_fileList = [] 
    MYD03_fileList = [] 
    MYD35_fileList = [] 
    
    ticker = 1 
    
    duplicateFound = 0 
    
    # run the two controlling loops (Reflectance)
    
    # --------------------------------------------------
    # Set above inpts to 1 if THIS IF YOU ARE RUNNING FILES FOR THE FIRST TIME!!! 
    # --------------------------------------------------
    if first_time == 1:
        for files in os.listdir(fileDirectory):
            
            if files.endswith('.hdf'):
                
                # MOD02     
                if files.startswith('MOD02'):
                    print "looking at MYD02 file"    
                    #basically if we can find the corret day/time 
                    #in all three, they get appended to the list... 
                    yr_day_time_version = files[9:23]  
                    
                    # now restrict the list to only mid-day hours 
                    #( fom 1300 UTC to 1700 UTC)                    
                    
                    utc_time = int(files[18:22])
                    
                    # ANd start on day of year it is told to start on 
                    
                    day_of_year_check = int(files[14:17])
                    
                    if day_of_year_check >= day_start_list[ticker-1]:
                
                        if utc_time >= 1300 and utc_time <=1700:
                        
                            #now check for duplicaties 
                            if any(files[0:40] in fl for fl in MOD02_fileList):                
                                print "duplicate found"
                                duplicateFound = 1
                            
                            if duplicateFound == 0:
                                print "no duplicate was found"
                                
                                # look for a mod03 match
                                mod03match = glob.glob(fileDirectory+"MOD03*"+
                                                yr_day_time_version+"*"+".hdf")
                    
                                if len(mod03match) > 0:
                                    
                                    print "found MOD03 Match"
                                    # look for a mod03 match          
                                    mod35match = glob.glob(fileDirectory+
                                    "MOD35_L2*"+yr_day_time_version+"*"+".hdf")
                    
                                    if len(mod35match) > 0:
                                        print "found MOD35 match," 
                                        "adding files to file list"
                                        
                                        MOD02_fileList.append(files)
                                        MOD02_fileCount += 1
                                        
                                        MOD03_fileList.append(mod03match)
                                        MOD03_fileCount += 1
                                        
                                        MOD35_fileList.append(mod35match)
                                        MOD35_fileCount += 1
                            # set duplicate found back to zero 
                            duplicateFound = 0 
        
        # now save what you just did as as pickle 
        #so that you don't have to wait 10 minutes 
        #for the above code to run each time.! 
        
        pMOD02 = open( fileDirectory+fjord+"_pMOD02_"+year+"_fileList.p", "wb" )
        pMOD03 = open( fileDirectory+fjord+"_pMOD03_"+year+"_fileList.p", "wb" )
        pMOD35 = open( fileDirectory+fjord+"_pMOD35_"+year+"_fileList.p", "wb" )
        
        pickle.dump(MOD02_fileList,pMOD02)
        pickle.dump(MOD03_fileList,pMOD03)
        pickle.dump(MOD35_fileList,pMOD35)
        
        pMOD02.close()
        pMOD03.close()
        pMOD35.close()
        
        print MOD02_fileCount, "Files were correctly matched and will be run"
        
    # --------------------------------------------------
    # open the file pickle if you have one! 
    # --------------------------------------------------
    elif first_time == 0:
        
        pMOD02 = open( fileDirectory+fjord+"_pMOD02_"+year+"_fileList.p")
        pMOD03 = open( fileDirectory+fjord+"_pMOD03_"+year+"_fileList.p")
        pMOD35 = open( fileDirectory+fjord+"_pMOD35_"+year+"_fileList.p")
        
        MOD02_fileList = pickle.load(pMOD02)
        MOD03_fileList = pickle.load(pMOD03)
        MOD35_fileList = pickle.load(pMOD35)
        
        MOD02_fileCount = len(MOD02_fileList)
        MOD03_fileCount = len(MOD03_fileList)
        MOD35_fileCount = len(MOD35_fileList)
        
    # --------------------------------------------------
    # --------------------------------------------------
    # fjord specfic stuff handled here 
    
    if fjord  == 'N':
        print "Working on Nuuk data"
        # You need to manually change data array length 
        #if you change teh centerline text file.     
        data_array_length = 86
        
        
        # ROI info - used down around line 680
        n=64.5
        s=63.9
        e=-49.7
        w=-52.8
    
        # To get a transect's lat and long coordinates:
        #   1) open ENVI 
        #   2) open a subsetted HDF that is correctly projected  
        #   3) Click Tools > profile > arbitrary profile
        #   4) in the spatial profile box (not the plot of the 
        #      transect you drew), click file > save transect points to ASCII    
        #   5 save the file to somewhere it can be read by this scripts 
        
        # --------------------------------------------------
        # Read lat and lon from ASCII you made in ENVI 
        # --------------------------------------------------
        # Point	     
        # X	     
        # Y	
        # EuclidianDist (Meters)	
        # CumulativeDist (Meters)	          
        # Map X	          
        # Map Y	  
        # Latitude	 
        # Longitude	
        # Band1
         # You need to manually change the data array length 
         #if you change the centerline text file.     
        
        transect = "F:\\TRANSECTS\\Nuuk\\nuuk_tran_20121123.txt"    
        mask_path ="F:\\MARCH2013RUN\\landMask\\N_MASK.tif"
        allowable_b2_map_path = "F:\\MARCH2013RUN\\landMask\\N_allow.tif"
        
    elif fjord == 'K':
        print "Working on Kangerlussuaq data"
        # this is the number of pixels in the centerline 
        data_array_length = 194
        
        
        # ROI info - used down around line 680
        n=67.1
        s=66.3
        e=-50.0
        w=-54.0
        
        transect = "F:\\TRANSECTS\\Kanger\\K_transect_10_31_12.txt"  
        mask_path = "F:\\MARCH2013RUN\\landMask\\K_MASK.tif"
        allowable_b2_map_path = "F:\\MARCH2013RUN\\landMask\\K_allow.tif"
        
    elif fjord == 'P':
        print "Working on Paakitsoq data"
        # this is the number of pixels in the centerline 
        data_array_length = 33
        #ROI_dimensions = [134,468]
        
        # ROI info - used down around line 680    
        n=69.7
        s=69.3
        e=-50.0
        w=-51.4
    
        transect = "F:\\TRANSECTS\\pak\\pak_tran_done_20121123.txt" 
        mask_path = "F:\\MARCH2013RUN\\landMask\\P_MASK.tif"
        allowable_b2_map_path = "F:\\MARCH2013RUN\\landMask\\P_allow.tif"
       
    
    # --------------------------------------------------
    # --------------------------------------------------
    
    # import mask just to get it out of the way
    print "import mask"
    import arcpy
    fjord_mask = arcpy.RasterToNumPyArray(mask_path)
    allowable_b2_map = arcpy.RasterToNumPyArray(allowable_b2_map_path)
    del arcpy 

    ## regional X and y to get it out of the way
    #
    #regional_x = np.round(((e-w)/.003),0)+1.0
    #regional_y = np.round(((n-s)/.003),0)+1.0 
    #    
    #ROI_dimensions = [regional_y,regional_x]    
    
    utm_e, utm_s = utm22n(e,s)
    utm_w, utm_n  = utm22n(w,n)
    
    regional_x = np.round(((utm_e-utm_w)/250.),0)
    
    regional_y = np.round(((utm_n-utm_s)/250.),0)
        
    ROI_dimensions = [regional_y,regional_x]    
    
   
    
    xi = np.linspace(utm_w,utm_e,regional_x)
    yi = np.linspace(utm_n,utm_s,regional_y)

     
    # --------------------------------------------------
    # for now only opening one day/ swath scene 
    print "opening one day/swath scene"
    
    dataMatlab = {}  
    
    # kanger was 194 long
    
    data_b1 = np.zeros([len(MOD02_fileList),data_array_length])
    data_b2 = np.zeros([len(MOD02_fileList),data_array_length])
    data_sum_b1 = np.zeros([len(MOD02_fileList),data_array_length])
    data_sum_b2 = np.zeros([len(MOD02_fileList),data_array_length])
    
    B1_min = np.zeros([len(MOD02_fileList),data_array_length])
    B2_min = np.zeros([len(MOD02_fileList),data_array_length])
    B1_max = np.zeros([len(MOD02_fileList),data_array_length])
    B2_max = np.zeros([len(MOD02_fileList),data_array_length])
    
    YEARLY_SSC_extract = np.zeros([len(MOD02_fileList),data_array_length])    
    
    
    xx = 0
    data_header = []
    # --------------------------------------------------
    # --------------------------------------------------
    # pre-allocating the NON- daily arrays 
    # this is going to be the total number of scenes 
    #that went into informing the yearly information 
    # it is done pixel by pixel 
    print "pre allocating the NON- daily Arrays"
    
    scenes_considered = np.zeros(ROI_dimensions)
    
    YEARLY_B1 = np.zeros(ROI_dimensions)
    YEARLY_B2 = np.zeros(ROI_dimensions)
    YEARLY_SSC = np.zeros(ROI_dimensions)
    # --------------------------------------------------
    # --------------------------------------------------
    # pre-allocating the scene-to-scene arrays  
    
    
    
    
    # about time/date
    StS_year = np.zeros(len(MOD02_fileList),dtype=int)
    StS_day = np.zeros(len(MOD02_fileList),dtype=int)
    StS_time = np.zeros(len(MOD02_fileList),dtype=int)
    StS_day_time = np.zeros(len(MOD02_fileList))
    
    # about statistics from the scene
    StS_b1_sum = np.zeros(len(MOD02_fileList))
    StS_b2_sum = np.zeros(len(MOD02_fileList))
    StS_SSC_sum = np.zeros(len(MOD02_fileList))
    
    StS_b1_mean = np.zeros(len(MOD02_fileList))
    StS_b2_mean = np.zeros(len(MOD02_fileList))
    StS_SSC_mean = np.zeros(len(MOD02_fileList))
    
    StS_b1_stDev = np.zeros(len(MOD02_fileList))
    StS_b2_stDev = np.zeros(len(MOD02_fileList))
    StS_SSC_stDev = np.zeros(len(MOD02_fileList))
    
    
    StS_pixels_used_in_scene = np.zeros(len(MOD02_fileList))

    Pak_North_SSC_data_cube = np.zeros([88-71,185-169,len(MOD02_fileList)])
    Pak_South_SSC_data_cube= np.zeros([121-103,148-127,len(MOD02_fileList)])
    
    Watson_SSC_data_cube = np.zeros([100-69,545-489,len(MOD02_fileList)])
    Umivit_SSC_data_cube = np.zeros([133-99,553-504,len(MOD02_fileList)])
    Sarfartoq_SSC_data_cube = np.zeros([310-253,355-274,len(MOD02_fileList)])
    
    NK_SSC_data_cube = np.zeros([175-109,510-374,len(MOD02_fileList)])
    
    # --------------------------------------------------
    # --------------------------------------------------
    # STARTING THE LOOP 
    # --------------------------------------------------
    # --------------------------------------------------
    
    for swath_scene in xrange(scene_start,len(MOD02_fileList)):
        
        print MOD02_fileList[swath_scene] 
        
        # Pull out info from the file name that will be useful later
        
        swath_scene_year = int(MOD02_fileList[swath_scene][10:14])
        swath_scene_day = int(MOD02_fileList[swath_scene][14:17])
        swath_scene_time = int(MOD02_fileList[swath_scene][18:22])
        
        swath_scene_day_time = int(MOD02_fileList[swath_scene][14:17]
        )+(int(MOD02_fileList[swath_scene][18:22])/2400.)  
        
        fid = fileDirectory+str(MOD02_fileList[swath_scene]).strip('[]')
    
        fid2 = MOD03_fileList[swath_scene][0]
        fid3 = MOD35_fileList[swath_scene][0]
        

        # --------------------------------------------------
        #  OPEN SUBSETTED DATASET(S) 
        
        # borrowing liberally from this tutorial
        # http://www2.geog.ucl.ac.uk/~plewis/geogg122/readhdf.html
        # --------------------------------------------------
    
        # open MOD02    
        dataset = SD(fid,SDC.READ)
        
        # read the Scaled Iinterger data     
        MOD02_scaled_interger = dataset.select('EV_250_RefSB')
        
        # you need to drill into the metadata to get details 
        #like this to correct the scaled intergers into correct reflectance
        #(and radiance) values. From here you will be able to calc things 
        #like Remote Sensing Reflectance.... 
        
        #These are by band     
        reflectance_offsets = MOD02_scaled_interger.reflectance_offsets
        reflectance_scales = MOD02_scaled_interger.reflectance_scales
        
        refl = MOD02_scaled_interger[:,:,:]
        
        # these are band 1 and 2 SCALED INTERGERS- NOT REFLECTANCE... 
        b1SI =  refl[0,:,:]
        b2SI =  refl[1,:,:]    
        
        # calculating cos theta * reflectance 
        b1 = MOD02_scaled_interger.reflectance_scales[0] * (b1SI -
        MOD02_scaled_interger.reflectance_offsets[0])
        
        b2 = MOD02_scaled_interger.reflectance_scales[1] * (b2SI - 
        MOD02_scaled_interger.reflectance_offsets[1])
    
        # grab the scientific data set meta data 
    #    sds_md = dataset.GetMetadata('SUBDATASETS')
    #    
    #    print 'Reflectance Keys'
    #    for i in sds_md.iterkeys():
    #        print i,sds_md[i]
    #        
    #    datakeys = {}
    #    
    #    # --------------------------------------------------
    #    # THIS IS ALSO USER DEFINED, 
    #    # BUT NEEDS TO BE DONE AFTER YOU KNOW WHAT SUBDATASETS ARE IN THE HDF
    #    
    #    datasets = ['SUBDATASET_1']
    #    datanames = ['EV_250_RefSB']
    #    for (j,i) in enumerate(datasets):
    #        this = {}
    #        this['name'] = sds_md[i + '_NAME']
    #        this['description'] = sds_md[i + '_DESC']
    #        this['data'] = gdalnumeric.LoadFile(this['name'])
    #        datakeys[datanames[j]] = this.copy()
    #    
    #    #this is both bands
    #    refl = datakeys['EV_250_RefSB']['data']
        
        # --------------------------------------------------
        # NOW DO THE SAME THING FOR THE GEOLOCATION DATASET 
        # --------------------------------------------------
        
        geo_dataset = gdal.Open( fid2, GA_ReadOnly )
        
        # grab the scientific data set meta data 
        geo_sds_md = geo_dataset.GetMetadata('SUBDATASETS')
        
    #    print 'Geolocation (MOD/MYD 03) Keys'
    #    for i in geo_sds_md.iterkeys():
    #        print i,geo_sds_md[i]
            
        geo_datakeys = {}
        geo_datasets = ['SUBDATASET_9','SUBDATASET_10','SUBDATASET_15']
        geo_datanames = ['Latitude','Longitude','SolarZenith']
        for (j,i) in enumerate(geo_datasets):
            this = {}
            this['name'] = geo_sds_md[i + '_NAME']
            this['description'] = geo_sds_md[i + '_DESC']
            this['data'] = gdalnumeric.LoadFile(this['name'])
            geo_datakeys[geo_datanames[j]] = this.copy()
        
        
        # --------------------------------------------------
        # NOW DO THE SAME THING FOR THE CLOUD DATASET 
        # SUBDATASET_15_DESC [6x150x160] Cloud_Mask (8-bit integer)
        # SUBDATASET_6_DESC [6x150x160] Cloud_Mask mod35 (8-bit integer)
        
        # --------------------------------------------------
        
        cloud_dataset = gdal.Open( fid3, GA_ReadOnly )
        
        # grab the scientific data set meta data 
        cloud_sds_md = cloud_dataset.GetMetadata('SUBDATASETS')
    
          
        cloud_datakeys = {}
        cloud_datasets = ['SUBDATASET_6',
                          'SUBDATASET_15',
                          'SUBDATASET_7',
                          'SUBDATASET_8', 
                          'SUBDATASET_9']
                          
        cloud_datanames = ['Cloud_Mask mod35',
                           'Cloud_Mask', 
                           'Quality_Assurance mod35',
                           'cloud mask latitude',
                           'cloud mask longitude']
                           
        for (j,i) in enumerate(cloud_datasets):
            this = {}
            this['name'] = cloud_sds_md[i + '_NAME']
            this['description'] = cloud_sds_md[i + '_DESC']
            this['data'] = gdalnumeric.LoadFile(this['name'])
            cloud_datakeys[cloud_datanames[j]] = this.copy()
        
        # --------------------------------------------------
        # Open cloud mask and interpret
        # --------------------------------------------------
        
        #there appears to be no difference between these datasets.... 
        clouds = cloud_datakeys['Cloud_Mask']['data']
        clouds35 = cloud_datakeys['Cloud_Mask mod35']['data']
        cloudsQA = cloud_datakeys['Quality_Assurance mod35']['data']
        cloudLat = cloud_datakeys['cloud mask latitude']['data']
        cloudLon =  cloud_datakeys['cloud mask longitude']['data']   
        
        cloudLat_zoom = scipy.ndimage.interpolation.zoom(cloudLat, 5)
        cloudLon_zoom = scipy.ndimage.interpolation.zoom(cloudLon, 5)
        
        #get the dimensions of the 2d array  
        layers = clouds35.shape[0]
        x = clouds35.shape[1]
        y = clouds35.shape[2] 
        
        # --------------------------------------------------
        # MAKE EMPTY MAPS FOR PRODUCTS FROM CLOUD MASK 
        #makes a empty zeros array that will be filled in by the below loop. 
        # --------------------------------------------------
        
        mask_determined_map = np.zeros([x,y],dtype=int)
        
        FOV_map = np.zeros([x,y],dtype=int)
        
        lw_map = np.zeros([x,y],dtype=int)
        
        vis_refl_test_map = np.zeros([x,y],dtype=int) 
        
        aerosol_map = np.zeros([x,y],dtype=int)  
        
        thin_cirrus_map = np.zeros([x,y],dtype=int)     
        
        shadow_map = np.zeros([x,y],dtype=int) 
        
        thin_cirrus_IR_map = np.zeros([x,y],dtype=int) 
        
        vis_refl_ratio_test_map = np.zeros([x,y],dtype=int) 
        
        vis_nearIR_tests = np.zeros([x,y],dtype=int)
        
        high_cloud_CO2_map = np.zeros([x,y],dtype=int)
        
        high_cloud_67_map = np.zeros([x,y],dtype=int)
        
        high_cloud_138_map = np.zeros([x,y],dtype=int)
        
        IR_temp_diff_map = np.zeros([x,y],dtype=int)
        
        test_39_11_map = np.zeros([x,y],dtype=int)
        
        
    #    # --------------------------------------------------
    #    # MAKE EMPTY MAPS FOR PRODUCTS FROM CLOUD MASK QA 
    #    # --------------------------------------------------
    #    #get the dimensions of the 2d array  
    #    QAlayers = cloudsQA.shape[2]
    #    QAx = cloudsQA.shape[0]
    #    QAy = cloudsQA.shape[1] 
    #    
    #    QAuseful_map = 0
        
        #this loop reads each pixel 
        for i in xrange(0,x):    
            for j in xrange(0,y):
                
                # here I read the specific pixel value 
                # Note there are 6 LAYERS cloud mask
                #- so value will be updated as needed to move to a new layer... 
                cloud_byte0 = clouds35[0,i,j]
                cloud_byte1 = clouds35[1,i,j]
                cloud_byte2 = clouds35[2,i,j]
                cloud_byte3 = clouds35[3,i,j]
                cloud_byte4 = clouds35[4,i,j]
                cloud_byte5 = clouds35[5,i,j]
                
                # take that value and convert it to a binary string  
                # it will come out looking like this
                #        '10111001'
                # the value on the far right is bit number
                #ZERO in MODIS Cloud Mask User's Guide by Kathleen Strabala        
                cloud_byte0 = "{0:08b}".format(cloud_byte0)
                cloud_byte1 = "{0:08b}".format(cloud_byte1)
                cloud_byte2 = "{0:08b}".format(cloud_byte2)
                cloud_byte3 = "{0:08b}".format(cloud_byte3)
                cloud_byte4 = "{0:08b}".format(cloud_byte4)
                cloud_byte5 = "{0:08b}".format(cloud_byte5)
                
                # HOWEVER, IN THE NEXT LINE I AM GOING TO FLIP
                #THIS STRING SO THAT I DON'T 
                #GO CROSS EYED THINKING ABOUT WHAT IS CORRECT...         
                cloud_byte0 = cloud_byte0[::-1]        
                cloud_byte1 = cloud_byte1[::-1] 
                cloud_byte2 = cloud_byte2[::-1] 
                cloud_byte3 = cloud_byte3[::-1] 
                cloud_byte4 = cloud_byte4[::-1] 
                cloud_byte5 = cloud_byte5[::-1] 
                
                #cloudMask = binaryValu[5] 
                # location 5 is for internal MOD09GA cloud mask
                
                # --------------------------------------------------
                # Was the mask determined    
                # --------------------------------------------------        
         
                mdFlag = cloud_byte0[0]
        
                if mdFlag == '1': # determined,0 = not determined 
                    mask_determined_map[i,j] = 1        
                
    #            # --------------------------------------------------
    #            # Was the mask useful? 
    #            # --------------------------------------------------  
    #            
    #            QAvalu = cloudsQA[i,j,0]
    #            QAbinaryValu = "{0:08b}".format(QAvalu)
    #            QAbinaryValu = QAbinaryValu[::-1] 
    #            
    #            QAuseful_flag = QAbinaryValu[0]
    #            if QAuseful_flag == '1': # determined,0 = not determined 
    #                 QAuseful_map = 1 
                
                # --------------------------------------------------
                # Unobstructed FOV Quality Flag 
                # as is this test qualifies some of the core plume 
                #as uncertain clear, and some of it as probably clear 
                #(when it should be confident clear)
                # Right now I am assuming this is beacuse one 
                #of the tests probably assumes that water shold
                #be dark in the near IR when in fact the turbid waters of
                # the fjord are not dark.
                # --------------------------------------------------         
                
                FOV_Flag = cloud_byte0[1:3]        
                
                if FOV_Flag == '00': # cloudy
                    FOV_map[i,j] = 0
                
                if FOV_Flag == '01': # uncertain clear 
                     FOV_map[i,j] = 1
                
                if FOV_Flag == '10': # probaly clear 
                     FOV_map[i,j] = 1
                     
                if FOV_Flag == '11': # confident clear
                     FOV_map[i,j] = 1        
                
                # --------------------------------------------------
                # Water - Coastal - Desert - Land flagging         
                # --------------------------------------------------
                land_waterFlag = cloud_byte0[6:8] 
                # 00 (clear), 01 (cloudy), 10 (mixed) are all possible. 
                
        
                if land_waterFlag == '00': # water
                    lw_map[i,j] = 1
                
                if land_waterFlag == '10': 
                    # coastal - THIS MAKES SENSE WHEN YOU DISPLAY AN IMAGE 
                    # - BUT IS IS OPPOSITE OF WHAT DOCUMENTATION SAYS
                     lw_map[i,j] = 1
                
                if land_waterFlag == '01': 
                    # Desert - THIS MAKES SENSE WHEN YOU DISPLAY AN IMAGE 
                    #- BUT IS IS OPPOSITE OF WHAT DOCUMENTATION SAYS
                     lw_map[i,j] = 0
                     
                if land_waterFlag == '11': # Land
                     lw_map[i,j] = 0
                
                # --------------------------------------------------
                # Non- Cloud Obstruction Test        
                # --------------------------------------------------
                                    
                aerosol_flag = cloud_byte1[0]
                
                if aerosol_flag == '1': # determined,0 = not determined 
                    aerosol_map[i,j] = 1   
                
                # --------------------------------------------------
                # Thin Cirrus Test        
                # --------------------------------------------------
                thin_cirrus_flag = cloud_byte1[1]
                
                if thin_cirrus_flag == '1': # determined,0 = not determined 
                    thin_cirrus_map[i,j] = 1   
    
                # --------------------------------------------------
                # shadow Test        
                # --------------------------------------------------
                shadow_flag = cloud_byte1[2]
                
                if shadow_flag == '1': # determined,0 = not determined 
                    shadow_map[i,j] = 1               
    
                # --------------------------------------------------
                # Thin Cirrus IR Test        
                # --------------------------------------------------
                thin_cirrus_IR_flag = cloud_byte1[3]
                
                if thin_cirrus_IR_flag == '1': # determined,0 = not determined 
                    thin_cirrus_IR_map[i,j] = 1                           
                
                # --------------------------------------------------
                # GROUP I 
                # Bits 14 and 15
                # --------------------------------------------------           
                # Bit 14            
                high_cloud_CO2_flag = cloud_byte1[6]
                
                if high_cloud_CO2_flag == '1': # determined,0 = not determined 
                    high_cloud_CO2_map[i,j] = 1               
                
                # bit 15 
                high_cloud_67_flag = cloud_byte1[7]
                
                if high_cloud_67_flag == '1': # determined,0 = not determined 
                    high_cloud_67_map[i,j] = 1               
                
                # --------------------------------------------------
                # GROUP IV 
                # Bits 16
                # --------------------------------------------------           
                # Bit 16            
                high_cloud_138_flag = cloud_byte2[0]
                
                if high_cloud_138_flag == '1': # determined,0 = not determined 
                    high_cloud_138_map[i,j] = 1               
                
                # --------------------------------------------------
                # GROUP II 
                # Bits 18 and 19
                # --------------------------------------------------           
                # Bit 18            
                IR_temp_diff_flag = cloud_byte2[2]
                
                if IR_temp_diff_flag == '1': # determined,0 = not determined 
                    IR_temp_diff_map[i,j] = 1               
                
                # bit 19 
                test_39_11_flag = cloud_byte2[3]
                
                if test_39_11_flag == '1': # determined,0 = not determined 
                    test_39_11_map[i,j] = 1               
                
                # --------------------------------------------------
                # Group  III
                # Visual reflectance Testing - Bit 20 
                # this cloud test assumes a dark water surface 
                # in bands 1 and 2 (red/n. ir) This is absolutely not 
                # the case for turbid river plumes in coastal greenland
                # use this flag to correct erroneous cloud classifications
                # BUT NEED SOME TEST B/C THIS COULD overcorrect.  
                # --------------------------------------------------        
             
                vis_refl_test_flag = cloud_byte2[4]
                
                if vis_refl_test_flag == '0': # determined,0 = not determined 
                    vis_refl_test_map[i,j] = 1       
                
                # --------------------------------------------------
                #  Visual reflectance Testing - Bit 21 
                
                vis_refl_ratio_test_flag = cloud_byte2[5]
                
                if vis_refl_ratio_test_flag == '0': 
                    # determined,0 = not determined 
                   vis_refl_ratio_test_map[i,j] = 1                   
     
        # --------------------------------------------------
        # Re-size geolocation dataset to match the reflectance bands... 
        # --------------------------------------------------
        
        lat = geo_datakeys['Latitude']['data']
        #this resizes the file 4x and using a cubic spline through
        #the data to interpolate 
        
        lat_zoom = scipy.ndimage.interpolation.zoom(lat, 4)
        
        lon = geo_datakeys['Longitude']['data']
        lon_zoom = scipy.ndimage.interpolation.zoom(lon, 4)
    
        SZA = geo_datakeys['SolarZenith']['data']    
        SZA_zoom = scipy.ndimage.interpolation.zoom(SZA, 4)    
        
        
        # --------------------------------------------------
        # PULL TOGETHER ALL THE CLOUD MASK INFO from MOD35
        
        # --------------------------------------------------
        
        # the master cloud mask asks:
        # if the mask was detrmined - THIS IS STRICT - 
        #it it wasn't determinted it gets rid of the good
        #Reflectance data BUT ensures that there isn't reflectance data
        #that has been contaminted by clouds that 
        # was allowed in because the mask wasn't run.. 
        # FOV Map - this is the top level cloud mask that 
        #is either confident clear, probably clear, uncertain clear, cloudy.
        #only confident clear is let through right now even though it 
        #classifys some sediment cores as clouds erroneously 
        
        # Build Mask 
    
        MASTER_CLOUD_MASK =  (aerosol_map 
                                * thin_cirrus_map 
                                * shadow_map 
                                * thin_cirrus_IR_map 
                                * high_cloud_67_map 
                                * IR_temp_diff_map 
                                * test_39_11_map) 
                                #* FOV_map # * lw_map   # FOV_map 
                                #* high_cloud_CO2_map * high_cloud_138_map 
        
        # NOW to be conservative we are going to dialate the 
        #cloud mask because it isn't doing as good of a job 
        #masking out cloud edges. 
        MASTER_CLOUD_MASK = MASTER_CLOUD_MASK.astype('float64')
    
    
        MASTER_CLOUD_MASK_old = MASTER_CLOUD_MASK
      
      
        # --------------------------------------------------
        # Now quality contol for bad reflectance data bad meaning
        #   1) cloud contaminated
        #   2) land contaminated? this isn'at a big deal with the transect...
        #   3) DO dark area subtraction... 
        # --------------------------------------------------
        
       
        
        # --------------------------------------------------
        # DARK OBJECT SUBTRACT - for each band 
        b1 = b1 - b1.min()
        b2 = b2 - b2.min()
        
        # --------------------------------------------------
        # COS THETA CORRECT     
    
        print "Solar Zentih Angle MIN for this scene:", SZA_zoom.min()/100    
        print "Solar Zentih Angle MAX for this scene:", SZA_zoom.max()/100    
        
        print "b1 is shaped,", np.shape(b1)
    
        SZA_radian_cos_corr = np.cos(np.deg2rad(SZA_zoom/100))
    
        print "SZA_radians_cos_corr is shaped,", np.shape(SZA_radian_cos_corr) 
        
        if np.shape(b1) == np.shape(SZA_radian_cos_corr):
            
            print "MOD02 and MOD03 files are same shape," 
            "continuing with processing"
            
            b1 = np.multiply(b1,(1.0/SZA_radian_cos_corr))
            b2 = np.multiply(b2,(1.0/SZA_radian_cos_corr))
            
            # throw out all pixels that are above a speficed solar zenith angle 
            
            b1[np.where((SZA_zoom/100) > max_allowed_SZA)] = 0
            b2[np.where((SZA_zoom/100) > max_allowed_SZA)] = 0
            
            # --------------------------------------------------
            # Band 1 (Y) expected from band 2 (X)     
            # expected_Y = .0428*log(X)+.2487;
            # --------------------------------------------------
        
            expected_b1 = .0428*np.log(b2)+.2487
            
            # difference the expected from actual values, and take the absolute
            #value to make subsequent logical statements easier. 
            diff_b1 = np.abs(expected_b1-b1)     
            
            #make empty mask array that will be filled in next line. 
            diff_b1_mask = np.zeros(np.shape(diff_b1))
            
            # fine where diff b1 is within a certain tolerance, and allow it 
            #to be assigned 1 (as in these pixels will pass the test) 
            # moved from .025 to .02 as of 6-5-2013, 
            #back from .03 to .25 for 6-20-13
            # changed from .020 to .030 on 10-30-2013
            
            diff_b1_mask[np.where(diff_b1 < .040)] = 1
             
            # --------------------------------------------------
            # GRID EVERYTHING SO THAT IT CAN TALK TO EACH OTHER. 
            # --------------------------------------------------

            
            #CONVERT FROM LAT LONG INTO UTM 
            
            lon_subset_utm, lat_subset_utm = pyproj.transform(wgs84, 
                                                              utm22n, 
                                                              lon_zoom.flatten(),
                                                              lat_zoom.flatten())
            
            # --------------------------------------------------
            
            b1_grid = griddata((lon_subset_utm,lat_subset_utm),
                               b1.flatten(),
                               (xi[None,:],
                                yi[:,None]), 
                               method='nearest')
                               
            b2_grid = griddata((lon_subset_utm,
                                lat_subset_utm),
                               b2.flatten(),
                               (xi[None,:], yi[:,None]), 
                               method='nearest')
                               
            lat_grid = griddata((lon_subset_utm,
                                 lat_subset_utm),
                                lat_subset_utm,
                                (xi[None,:], yi[:,None]), 
                                method='nearest')
            lon_grid = griddata((lon_subset_utm,
                                 lat_subset_utm),
                                lon_subset_utm,
                                (xi[None,:], yi[:,None]),
                                method='nearest')
            #b1_grid = griddata((lat_zoom.flatten(),lon_zoom.flatten()), b1.flatten(), (xi[None,:], yi[:,None]), method='nearest')
            #b2_grid = griddata((lat_zoom.flatten(),lon_zoom.flatten()), b2.flatten(), (xi[None,:], yi[:,None]), method='nearest')
        
            cloud_lon_subset_utm, cloud_lat_subset_utm = pyproj.transform(wgs84,
                                                                          utm22n,
                                                                          cloudLon_zoom.flatten(),
                                                                          cloudLat_zoom.flatten())    
            
            # MOD35
            cloud_mask_grid = griddata((cloud_lon_subset_utm,
                                        cloud_lat_subset_utm),
                                        MASTER_CLOUD_MASK.flatten(),
                                       (xi[None,:], 
                                        yi[:,None]), 
                                        method='nearest')
                                        
            diff_b1_mask_grid = griddata((lon_subset_utm,
                                          lat_subset_utm),
                                          diff_b1_mask.flatten(),
                                          (xi[None,:],
                                          yi[:,None]),
                                          method='nearest')
            
            #cloud_mask_grid = griddata((cloudLat_zoom.flatten(),cloudLon_zoom.flatten()), MASTER_CLOUD_MASK.flatten(), (xi[None,:], yi[:,None]), method='nearest')
        
            # --------------------------------------------------
            # This is a land/water mask, it also backstops the 'expected' 
            # relationship tubidity mask 
            # --------------------------------------------------

            # testing/revising this section as of 6-19-2013
            # --------------------------------------------------
            # CHANGEABLE  - The entire map can be changed with 
            # Open_Allow_mask_and_save.py           
            core_plume_b2_criteria = .17
            rest_of_fjord_b2_criteria = .17
            # -------------------------------------------------- 
            
            allowable_b2_map = np.where(allowable_b2_map == 1,
                                        rest_of_fjord_b2_criteria,
                                        allowable_b2_map)
            allowable_b2_map = np.where(allowable_b2_map == 2,
                                        core_plume_b2_criteria,
                                        allowable_b2_map)
                    
            b2_mask = np.ones(b2_grid.shape)            
            b2_mask[np.where(b2_grid > allowable_b2_map)] = 0            
            
         
            
#            plt.subplot(211)
#            plt.imshow(b2_grid)
#            plt.subplot(212)
#            plt.imshow(b2_mask)
#            print "max for this scene is:", np.max(b2_grid*b2_mask)
#            
#            plt.show()
            
            # --------------------------------------------------
            # FINAL B1 and B2 CALCULATED
            # --------------------------------------------------
        
            # diff_b1_mask_grid applies to both bands 
            final_b1 = (b1_grid * cloud_mask_grid 
                        * diff_b1_mask_grid * fjord_mask * b2_mask)
            final_b2 = (b2_grid * cloud_mask_grid 
                        * diff_b1_mask_grid * fjord_mask * b2_mask)
            
                  
            
            # add the two bands
            sum_b1_b2 = final_b1 + final_b2
            
            print " Max b1 is:", final_b1.max()    
            print " Max b2 is:", final_b2.max()    
            print " Max sum b1 b2 is:", sum_b1_b2.max()    
            
            # if the two bands are greater than .3     
           
            SSC_CONCENTRATION = 1.8038 * np.exp(19.108*sum_b1_b2)    
            print " Max SSC [mg/l] is:", SSC_CONCENTRATION.max() 
            
            # FORCE SSC of 1.8038 to go back to zero 
            
            SSC_CONCENTRATION[np.where(SSC_CONCENTRATION == 1.8038)] = 0.0
            
            # THIS IS THE CORRECT PLOTTING ROUTINE FOR AS OF 10-28-2013
            plt.subplot(3,3,1)
            
            plot1 = plt.imshow(final_b1)
            plt.title('Band 1')
            plot1.set_clim(0.0,.5)
            plt.set_cmap('spectral')

            plt.subplot(3,3,2)
            plot2 = plt.imshow(final_b2)
            plt.title('Band 2')
            plot2.set_clim(0.0,.5)
            plt.set_cmap('spectral')
            
            plt.subplot(3,3,3)
            plot3 = plt.imshow(SSC_CONCENTRATION)
            plt.title('SSC')
            plot3.set_clim(0.0,1500.0)
            plt.set_cmap('spectral')
             
            plt.subplot(3,3,4)
            plot4 = plt.imshow(b1_grid)
            plt.title('B1 NO Mask')
            plot4.set_clim(0.0,1.0)
            plt.set_cmap('spectral')
            
            plt.subplot(3,3,5)
            plot5 = plt.imshow(b2_grid)
            plt.title('B2 NO Mask')
            plot5.set_clim(0.0,1.0)
            plt.set_cmap('spectral')
            
            plt.subplot(3,3,6)
            plot6 = plt.imshow(diff_b1_mask_grid)
            plt.title('Expected Relationship Mask')
            plot6.set_clim(0.0,1.0)
            plt.set_cmap('spectral')
            
            plt.subplot(3,3,7)
            plot7 = plt.imshow(b2_mask)
            plt.title('b2 Mask')
            plot7.set_clim(0.0,1.0)
            plt.set_cmap('spectral')
            
            plt.subplot(3,3,8)
            plot8 = plt.imshow(diff_b1_mask_grid - b2_mask)
            plt.title('diff_b1_mask_grid - b2_mask')
            plot8.set_clim(-1.0,1.0)
            plt.set_cmap('spectral')
            
            AAA = SSC_CONCENTRATION[69:100,489:545]
            
#            plt.subplot(3,3,9)
#            plot3 = plt.imshow(SSC_CONCENTRATION[69:100,489:545])
#            plt.title('SSC Watson Subset')
#            plot3.set_clim(0.0,1500.0)
#            plt.set_cmap('spectral')
            
            plt.show() 
        
           
                
                    # --------------------------------------------------
                    #MASK OUT DA CLOUDS     
        #            b1 = b1 * MASTER_CLOUD_MASK    
        #            b2 = b2 * MASTER_CLOUD_MASK
                    
                    # --------------------------------------------------
                    # Now calculate suspended sediment concentration (intead of reflectance)
                    #   1) cloud contaminated
                    #   2) land contaminated? this isn'at a big deal with the transect...
                    #   3) what else? 
                    # --------------------------------------------------
                    # --------------------------------------------------
                    # I now have the  relevant 2-d arrays. 
                    # now figure out some way to etract the pixel values I want
                    #   1) plume centerline
                    #   2) The entire fjord
                    # 
                    # possible options are to grid the whole thing, 
                    # --------------------------------------------------
                    
                    # To get a transect's lat and long coordinates:
                    #   1) open ENVI 
                    #   2) open a subsetted HDF that is correctly projected  
                    #   3) Click Tools > profile > arbitrary profile
                    #   4) in the spatial profile box (not the plot of the transect you drew), click file > save transect points to ASCII    
                    #   5 save the file to somewhere it can be read by this scripts 
                    
                    # --------------------------------------------------
                    # Read lat and lon from ASCII you made in ENVI 
                    # --------------------------------------------------
                    # Point	     X	     Y	EuclidianDist (Meters)	CumulativeDist (Meters)	          Map X	          Map Y	  Latitude	 Longitude	Band1
        
            fo = open(transect,"r")
            
            # Skipping over header lines... there must be a more elegant way to do this.... 
            fo.readline()
            fo.readline()
            fo.readline()
            fo.readline()
            fo.readline()
            fo.readline()
            fo.readline()
            
            #extract_lat = [67.70835876]
            #extract_lon = [-53.19508743]
            
            extract_lat = []
            extract_lon = []
            
            extract_x = []
            extract_y = []
            for line in fo:
                
                # gets rid of white spaces 
                line = line.strip()
                pt, tran_x, tran_y, Eclid_dist, Cum_dist, mapX, mapY, tran_lat, tran_lon, v9 = line.split("\t")
                extract_lat.append(float(tran_lat))
                extract_lon.append(float(tran_lon))
                extract_x.append(float(mapX))
                extract_y.append(float(mapY))
                
            fo.close()
            
            # convert from lat to UTM
            extract_lon, extract_lat = pyproj.transform(wgs84, utm22n,extract_lon,extract_lat)
            
            #extract_lat = [67.70835876]
            #extract_lon = [-53.19508743]
            
            # --------------------------------------------------
            # extract values
            # --------------------------------------------------
            
            extract_b1 = []
            extract_b2 = []
            sum_b1 = []
            sum_b2 = []
            b1Min = []
            b1Max = []
            b2Min = []
            b2Max = []
            b2b1ratio = []
            numelPts=[]
            
            # Adding to the code as of 10-28-2013
            extract_SSC = [] 
            
            if len(extract_lat) != len(extract_lon):
                print "Not the same number lat and long points"
              
            else:
                
                for i in xrange(0,len(extract_lat)):
                    # select the area around the point by latitude 
#                    a = np.logical_and(lat_grid < extract_lat[i]+.003,lat_grid > extract_lat[i]-.003)
                    a = np.logical_and(lat_grid < extract_lat[i]+125,lat_grid > extract_lat[i]-125)
                    
                    # select the area around the point by longitude
                    #b = np.logical_and(lon_grid < extract_lon[i]+.025,lon_grid > extract_lon[i]-.025)
#                    b = np.logical_and(lon_grid < extract_lon[i]+.003,lon_grid > extract_lon[i]-.003)
                    b = np.logical_and(lon_grid < extract_lon[i]+125,lon_grid > extract_lon[i]-125)
                    #the find where both are true
                    c = np.logical_and(a == True, b == True)
                    
                    # and then apply it to band 1 reflectance to extract the value we want.
                    
                    b1_values = np.mean(final_b1[c])
                    b2_values = np.mean(final_b2[c])            

                    # SSC values - added as of 10-28-2013
                    SSC_values = np.mean(SSC_CONCENTRATION[c])


                    b2b1_value = b2_values/b1_values            
                    
                    
                    
                    b1_sum = np.sum(final_b1[c])
                    b2_sum = np.sum(final_b2[c])
                
                    b1Min_step1 = 0 
                    b1Max_step1 = 0
                    
                    if final_b1[c].size != 0:
                        
                        b1Min_step1 = np.min(final_b1[c])
                        b1Max_step1 = np.max(final_b1[c])
                        
                    b2Min_step1 = 0 
                    b2Max_step1 = 0 
                    
                    if final_b2[c].size != 0:
                        
                        b2Min_step1 = np.min(final_b2[c])
                        b2Max_step1 = np.min(final_b2[c])            
                    
                    #values = list(b1[c])
                    #numelPts.append(len(values))
                    extract_b1.append(b1_values) 
                    extract_b2.append(b2_values)
                    
                    
                    #extract_SSC.append(SSC_values)

                    # YEARLY_SSC_extract = np.zeros([len(MOD02_fileList),data_array_length])   
                    YEARLY_SSC_extract[swath_scene,i] = SSC_values
                    
                    b2b1ratio.append(b2b1_value)
        
                    sum_b1.append(b1_sum)
                    sum_b2.append(b2_sum)
                    
                    b1Min.append(b1Min_step1)
                    b1Max.append(b1Max_step1)
                    b2Min.append(b2Min_step1)
                    b2Max.append(b2Max_step1)
   
            
            # Kanger_critera
        #    nan_count = np.isnan(extract_b1).sum()
        #    refl_sum = np.nansum(extract_b1[0:75])
        #    refl_check1 = np.nanmax(extract_b1[0:25]) - np.nanmax(extract_b1[25:50])
        #    refl_check2 = np.nanmax(extract_b1[25:50]) - np.nanmax(extract_b1[50:75])
        
            # test nuuk criteria
            nan_count = np.isnan(extract_b1).sum()
            refl_sum = np.nansum(extract_b1[0:50])
            refl_check1 = np.nanmax(extract_b1[0:10]) - np.nanmax(extract_b1[10:20])
            refl_check2 = np.nanmax(extract_b1[20:30]) - np.nanmax(extract_b1[30:40])
            
            print " NAN count is:", nan_count
            print "refl sum for this day is : ", refl_sum
            print "refl check1 for this day is;", refl_check1    
            print "refl check2 for this day is;", refl_check2   
            
            # for Kanger nan_count was < 20
            # refl_sum > .75 
        
            # Lowered for Nuuk and Pak becase transects are not as long    
            
        #    if nan_count < 20:
        #        if  refl_sum > .3:
        #            
        #            if refl_check1 > 0 and refl_check2 > 0:
        
            
#            # THIS IS THE CORRECT PLOTTING ROUTINE FOR AS OF 10-28-2013
#            plt.subplot(3,3,1)
#            
#            plot1 = plt.imshow(final_b1)
#            plt.title('Band 1')
#            plot1.set_clim(0.0,.5)
#            plt.set_cmap('spectral')
#
#            plt.subplot(3,3,2)
#            plot2 = plt.imshow(final_b2)
#            plt.title('Band 2')
#            plot2.set_clim(0.0,.5)
#            plt.set_cmap('spectral')
#            
#            plt.subplot(3,3,3)
#            plot3 = plt.imshow(SSC_CONCENTRATION)
#            plt.title('SSC')
#            plot3.set_clim(0.0,1500.0)
#            plt.set_cmap('spectral')
#             
#            plt.subplot(3,3,4)
#            plot4 = plt.imshow(b1_grid)
#            plt.title('B1 NO Mask')
#            plot4.set_clim(0.0,1.0)
#            plt.set_cmap('spectral')
#            
#            plt.subplot(3,3,5)
#            plot5 = plt.imshow(b2_grid)
#            plt.title('B2 NO Mask')
#            plot5.set_clim(0.0,1.0)
#            plt.set_cmap('spectral')
#            
#            plt.subplot(3,3,6)
#            plot6 = plt.imshow(diff_b1_mask_grid)
#            plt.title('Expected Relationship Mask')
#            plot6.set_clim(0.0,1.0)
#            plt.set_cmap('spectral')
#            
#            plt.subplot(3,3,7)
#            plot7 = plt.imshow(cloud_mask_grid)
#            plt.title('cloud_mask_grid')
#            plot7.set_clim(0.0,1.0)
#            plt.set_cmap('spectral')
#            
#            plt.subplot(3,3,8)
#            plot8 = plt.imshow(diff_b1_mask_grid - cloud_mask_grid)
#            plt.title('diff_b1_mask_grid - cloud_mask_grid')
#            plot8.set_clim(-1.0,1.0)
#            plt.set_cmap('spectral')
#            
#            #AA = SSC_CONCENTRATION[69:100,489:545]
#            plt.subplot(3,3,9)
#            plot9 = plt.plot( YEARLY_SSC_extract[swath_scene,:],'o')
#            plt.title('SSC Curve')
##            plt.subplot(3,3,9)
##            plot3 = plt.imshow(SSC_CONCENTRATION[69:100,489:545])
##            plt.title('SSC Watson Subset')
##            plot3.set_clim(0.0,1500.0)
##            plt.set_cmap('spectral')
#            
#            plt.show()          

            # --------------------------
            # BUILD YEARLY DATA 
            # --------------------------
        

            # scenes considered 
            # for this scene, make a array of zeros 
            used_in_scene = np.zeros(np.shape(final_b1))
            
            
            # set it to 1 if it was used in the scene     
            used_in_scene[np.where(final_b1 != 0)] = 1
            
            pixels_used_in_scene = np.sum(used_in_scene)
            
            # CONTROL FOR CLOUDY SCENES-
            #IF THIS WORKS MAY EXTEND TO ANALYSIS FURTHER..

            sum_fjord_pixels = np.sum(fjord_mask)
            
            # if at least 0 percent of the fjord 
            #is cloud free save it as an output png 
            if pixels_used_in_scene >= (sum_fjord_pixels * 0.0):
            
                # --------------------------
                # BUILD SCENE TO SCENE DATA (StS)
                # --------------------------
                # about time/date
                StS_year[swath_scene] = swath_scene_year
                StS_day[swath_scene] = swath_scene_day
                StS_time[swath_scene] = swath_scene_time
                StS_day_time[swath_scene] = swath_scene_day_time
            
                # about statistics from the scene
                
                StS_b1_sum[swath_scene] = np.sum(final_b1)
                StS_b2_sum[swath_scene] = np.sum(final_b2)
                
                daily_SSC_sum = np.sum(SSC_CONCENTRATION[np.where(SSC_CONCENTRATION > 1.8038)]) 
                print " the SUM OF ALL SSC for this day is [mg/l]:", daily_SSC_sum    
                StS_SSC_sum[swath_scene] = daily_SSC_sum    
                
                StS_b1_mean[swath_scene] = np.mean(final_b1)
                StS_b2_mean[swath_scene] = np.mean(final_b2)
                
                daily_SSC_mean = np.mean(SSC_CONCENTRATION[np.where(SSC_CONCENTRATION > 1.8038)]) 
                StS_SSC_mean[swath_scene] = daily_SSC_mean
                
                StS_b1_stDev[swath_scene] = np.std(final_b1)
                StS_b2_stDev[swath_scene] = np.std(final_b2)
                
                daily_SSC_std = np.std(SSC_CONCENTRATION[np.where(SSC_CONCENTRATION > 1.8038)]) 
                StS_SSC_stDev[swath_scene] = daily_SSC_std 
                
                if fjord =='P':
                    #pak n and s 
                    Pak_North_SSC_data_cube[:,:,swath_scene] = SSC_CONCENTRATION[71:88,169:185]
                    Pak_South_SSC_data_cube[:,:,swath_scene] = SSC_CONCENTRATION[103:121,127:148]

                if fjord == 'K':
                    #watson, umivit and sarfartoq
                    Watson_SSC_data_cube[:,:,swath_scene] = SSC_CONCENTRATION[69:100,489:545]
                    Umivit_SSC_data_cube[:,:,swath_scene] = SSC_CONCENTRATION[99:133,504:553]
                    Sarfartoq_SSC_data_cube[:,:,swath_scene] = SSC_CONCENTRATION[253:310,274:355]
                
                elif fjord == 'N':
                    # naukat kuat only
                    NK_SSC_data_cube[:,:,swath_scene] = SSC_CONCENTRATION[109:175,374:510]                
                
                # --------------------------
                # BUILD YEARLY DATA - OLD SPOT
                # --------------------------
                
                pixels_used_in_scene = np.sum(used_in_scene)
                print "for this scene there were:", pixels_used_in_scene, "Pixels used"
                StS_pixels_used_in_scene[swath_scene] = pixels_used_in_scene
                      
                scenes_considered = scenes_considered + used_in_scene
                
                # SUM of reflectivity values 
                YEARLY_B1 = YEARLY_B1 + final_b1 
                YEARLY_B2 = YEARLY_B2 + final_b2 
                YEARLY_SSC = YEARLY_SSC + SSC_CONCENTRATION
        
#                plt.figure(1)
#                plt.plot(extract_b1)
#                plt.plot(extract_b2,'r')
#                plt.plot(extract_SSC,'k')
#                plt.show()    
        
#                E_SSC = np.array(extract_SSC)                
#                
#                YEARLY_SSC_extract = np.concatenate(YEARLY_SSC_extract,E_SSC
                
        
                ticker = ticker + 1
        
    
    # USE THIS CODE TO DUMP A RASTER THAT 
    #IS USEFUL IN ARCGIS TO MAKE CUSTOM LAND MASKS TO BE USED IN ABOVE PROCESSING. 
    #import arcpy
    #
    #corner = arcpy.Point(utm_w,utm_s)
    ## units are in meters
    #outRaster = arcpy.NumPyArrayToRaster(YEARLY_B2,corner,250.0,250.0)
    #outRaster.save(fileDirectory+fjord+year+"AR_mayWmsk")
    
   
    

    
    from scipy import io
    
    if fjord == 'P':
        
        scipy.io.savemat(saveAs, 
                         mdict={'YEARLY_B1':YEARLY_B1,
                                'YEARLY_B2':YEARLY_B2,
                                'YEARLY_SSC':YEARLY_SSC,
                                'scenes_considered':scenes_considered,
                                'MOD02_fileList':MOD02_fileList,
                                'StS_year':StS_year,
                                'StS_day':StS_day,
                                'StS_time':StS_time,
                                'StS_day_time':StS_day_time,
                                'StS_b1_sum':StS_b1_sum,
                                'StS_b2_sum':StS_b2_sum,
                                'StS_SSC_sum':StS_SSC_sum,
                                'StS_b1_mean':StS_b1_mean,
                                'StS_b2_mean':StS_b2_mean,
                                'StS_SSC_mean':StS_SSC_mean,
                                'StS_b1_stDev':StS_b1_stDev,
                                'StS_b2_stDev':StS_b2_stDev,
                                'StS_SSC_stDev':StS_SSC_stDev,
                                'StS_pixels_used_in_scene':StS_pixels_used_in_scene,
                                'Pak_North_SSC_data_cube':Pak_North_SSC_data_cube,
                                'Pak_South_SSC_data_cube':Pak_South_SSC_data_cube,
                                'YEARLY_SSC_extract':YEARLY_SSC_extract})
     
    elif fjord == 'K':
        scipy.io.savemat(saveAs,
                         mdict={'YEARLY_B1':YEARLY_B1,
                                'YEARLY_B2':YEARLY_B2,
                                'YEARLY_SSC':YEARLY_SSC,
                                'scenes_considered':scenes_considered,
                                'MOD02_fileList':MOD02_fileList,
                                'StS_year':StS_year,'StS_day':StS_day,
                                'StS_time':StS_time,
                                'StS_day_time':StS_day_time,
                                'StS_b1_sum':StS_b1_sum,
                                'StS_b2_sum':StS_b2_sum,
                                'StS_SSC_sum':StS_SSC_sum,
                                'StS_b1_mean':StS_b1_mean,
                                'StS_b2_mean':StS_b2_mean,
                                'StS_SSC_mean':StS_SSC_mean,
                                'StS_b1_stDev':StS_b1_stDev,
                                'StS_b2_stDev':StS_b2_stDev,
                                'StS_SSC_stDev':StS_SSC_stDev,
                                'StS_pixels_used_in_scene':StS_pixels_used_in_scene,
                                'Watson_SSC_data_cube':Watson_SSC_data_cube,
                                'Umivit_SSC_data_cube':Umivit_SSC_data_cube,
                                'Sarfartoq_SSC_data_cube':Sarfartoq_SSC_data_cube,
                                'YEARLY_SSC_extract':YEARLY_SSC_extract})

    elif fjord == 'N':
        scipy.io.savemat(saveAs, 
                         mdict={'YEARLY_B1':YEARLY_B1,
                                'YEARLY_B2':YEARLY_B2,
                                'YEARLY_SSC':YEARLY_SSC,
                                'scenes_considered':scenes_considered,
                                'MOD02_fileList':MOD02_fileList,
                                'StS_year':StS_year,
                                'StS_day':StS_day,
                                'StS_time':StS_time,
                                'StS_day_time':StS_day_time,
                                'StS_b1_sum':StS_b1_sum,
                                'StS_b2_sum':StS_b2_sum,
                                'StS_SSC_sum':StS_SSC_sum,
                                'StS_b1_mean':StS_b1_mean,
                                'StS_b2_mean':StS_b2_mean,
                                'StS_SSC_mean':StS_SSC_mean,
                                'StS_b1_stDev':StS_b1_stDev,
                                'StS_b2_stDev':StS_b2_stDev,
                                'StS_SSC_stDev':StS_SSC_stDev,
                                'StS_pixels_used_in_scene':StS_pixels_used_in_scene,
                                'NK_SSC_data_cube':NK_SSC_data_cube,
                                'YEARLY_SSC_extract':YEARLY_SSC_extract})
