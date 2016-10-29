#######################################################################################
#######################################################################################
############### User Defined Settings #################################################

# This code was adapted from code Katy Barnhart wrote

#address='BDHudson@gmail.com' # your email address
#address='Benjamin.Hudson@colorado.edu'
address='HudsonMODIS@gmail.com' # your email address

# search for Files Parameters:
ps=['MOD03','MOD02QKM', 'MOD35_L2'] # ,'MOD02QKM', 'MOD35_L2','MOD03','MYD02QKM','MYD35_L2','MYD03'] modis dataproducts that are supported
#ps=['MYD03','MYD02QKM', 'MYD35_L2'] #

#dnbs=['D', 'N','B', 'DN', 'DB', 'NB','DNB'] # day and night settings
dnbs=['D']
c=5 # collection number

# bounding box for both search and spatial subsetting (units are in degrees: (N-S: 90:-90
# E-W: -180:180)
#n=72.0
#s=68.0
#e=-142.0
#w=-162.0

fjord = ['narwal'] #'Kanger','Pak','Ameralik''Andrews','qa'

for f in range(len(fjord)):

	fjords = fjord[f]
	
	if fjords == 'Kanger':
		n=67.1
		s=66.3
		e=-50.0
		w=-54.0

	elif fjords == 'Pak':
		n=69.7
		s=69.3
		e=-50.0
		w=-51.4

	elif fjords == 'Ameralik':
		n=64.5
		s=63.9
		e=-49.7
		w=-52.8

	elif fjords =='Elwha':
		n=48.29
		s=48.05
		e=-123.30
		w=-123.75

	elif fjords =='Andrews':
		n=75.15
		s=71.45
		e=-17.30
		w=-28.30

	elif fjords =='qa':
		n=68.85
		s=68.6
		e=-50.2
		w=-51.5

#75.25 to 76.25 deg. N to 73.25 to 76.5
	elif fjords =='narwal':
		n=76.5
		s=73.25
		e=-55.0
		w=-62.0
		

	# Time Period in 'YYYY-MM-DD HH:MM:SS' format, can be given as a list of start and end times. 
	#starts=['2000-05-15 00:00:00','2001-05-15 00:00:00','2002-05-15 00:00:00','2003-05-15 00:00:00','2004-05-15 00:00:00','2005-05-15 00:00:00','2006-05-15 00:00:00','2007-05-15 00:00:00','2008-05-15 00:00:00','2009-05-15 00:00:00','2010-05-15 00:00:00','2011-05-15 00:00:00','2012-05-15 00:00:00']
	#ends=['2000-10-25 00:00:00','2001-10-25 00:00:00','2002-10-25 00:00:00','2003-10-25 00:00:00','2004-10-25 00:00:00','2005-10-25 00:00:00','2006-10-25 00:00:00','2007-10-25 00:00:00','2008-10-25 00:00:00','2009-10-25 00:00:00','2010-10-25 00:00:00','2011-10-25 00:00:00','2012-10-25 00:00:00']
	#starts=['2000-05-15 00:00:00']
	#ends=['2000-10-25 00:00:00']
	starts=['2011-05-15 00:00:00']
	ends=['2011-10-31 00:00:00']
	# number of files per order
	fLim=1800

	# This higher Flim is to check 
	#fLim=12000

	# name of output pickle file with order number
	saveOut='qa_2000.p'

	############### End User Defined Settings #############################################
	#######################################################################################
	#######################################################################################
	clientUrl='http://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices' # MODAPS URL

	print "importing SOAPProxy"
	from SOAPpy import SOAPProxy
	import time
	import os
	import cPickle as pickle
		
	print "creating client"
	client = SOAPProxy(clientUrl)

	savedOIDS=[]
	files=[]


	for i in range(len(starts)): # for each time period
		st=starts[i]
		et=ends[i]
		print "time interval ", st, '<---->', et
		for p in ps: # for each product
			for dnb in dnbs: # for each Day/Night/Both Setting
				print "searching for: ", p, dnb
				try:
					# search for files
					fIDs=client.searchForFiles(product=p,
								   collection=c, 
								   startTime=st, 
								   endTime=et, 
								   north=n, 
								   south=s, 
								   east=e, 
								   west=w, 
								   coordsOrTiles='coords', 
								   dayNightBoth=dnb)
				except:
					print "exception raised, tring client again." 
					
					client = SOAPProxy(clientUrl);
					time.sleep(10)
					fIDs=client.searchForFiles(product=p,
								   collection=c, 
								   startTime=st, 
								   endTime=et, 
								   north=n, 
								   south=s, 
								   east=e, 
								   west=w, 
								   coordsOrTiles='coords', 
								   dayNightBoth=dnb)

					print "looks like we re-established contact."
					
				if isinstance(fIDs,list):
				# append files to file list if any where found
					print str(len(fIDs)), " files found"	
					for id in fIDs:
						files.append(id)
		
	# get only the unique granule ID numbers								
	print "checking for unique values"
	print "There are", len(files), "found files"
	files=list(set(files))	
	print "of which", len(files), "are unique"
		
	print "concatenating file names into one CS string, 5500 files long"
	totalItter=0
	orderItter=0

	saveOrderDict={}
	# -------------------------
	# THIS IS A MANUAL STEP!
	# -------------------------
	# -------------------------
	# remove files that have been temporarilt removed from processing
	
##	list_remove_files = [5599888,33329429,5582032,5587371,5599002,33320852,33326938,33327922,33328321,33331420,33338730,5579072,5583837,5587233,5589475,5598895,5599444,5599745,5599936,5600287,33319808,33320860,33324201,33324282,33325463,33327871,33327875,33328665,33330232,33331416,6219718,33324058,33328799] 
##	for ff in list_remove_files:
##		print "removing", ff
##		files.remove(str(ff))

	
	# -------------------------
	# -------------------------
	# -------------------------
	# -------------------------

	# create comma delimited strings of the file names, maximum length of order given by fLim
	while totalItter<len(files):
		if orderItter==0:
			fileString=files[totalItter]
			saveFiles=[files[totalItter]]
		else:
			fileString=fileString+','+files[totalItter]
			saveFiles.append(files[totalItter])
		orderItter+=1
		totalItter+=1

		if (orderItter==fLim)+(totalItter==len(files)):
		# if desired order length OR end of the file list is reached, place an order
			print fLim, 	" files or end of file list reached, ordering files"	
			try:
				# place order. This is where subsetting and projection can occur.
				oID=client.orderFiles(email=address, 
						      fileIds=fileString, 
						      geoSubsetNorth=n, 
						      geoSubsetSouth=s, 
						      geoSubsetWest=w, 
						      geoSubsetEast=e) 
			except:
				print "exception raised, tring client again." 
				
				client = SOAPProxy(clientUrl)
				time.sleep(10)
				
				print "looks like we re-established contact."
				
				oID=client.orderFiles(email=address, 
						      fileIds=fileString, 
						      geoSubsetNorth=n, 
						      geoSubsetSouth=s, 
						      geoSubsetWest=w, 
						      geoSubsetEast=e) 

			print "ordering complete. Order Numbers:"	
			savedOIDS.append(oID)
			print oID	
			orderItter=0
			saveOrderDict[str(oID)]=saveFiles

	print "ordering complete. Order Numbers:"	
	print savedOIDS
	output=open(saveOut, 'wb')
	pickle.dump(saveOrderDict, output)
	output.close()
	 
	print "Order Completed with no Errors"
