from ftplib import FTP
import os
#import time

ftpUrl='ladsweb.nascom.nasa.gov' # ftp site URL
outBase= 'F:\\MARCH2013RUN\\TO SORT\\' # filepath to folder to write downloaded data
usr='anonymous' # username for
pswd='BDHudson@gmail.com' # email address  used for your orders
#orders=[500836772]

#orders = [500836773,500836774,500836775,500836776,500836777,500836778,
#          500836779,500836780,500836781,500836782,500836783,500836784,
#          500836785,500836786,500836787,500836788,500836789,500836790,
#          500836791,500836793,500836794,500836795,500836796,500836797,
#          500836800,500836798,500836762,500836792]
#Narwal 2013    '500850364', '500850365', '500850366', '500850367', '500850368'    
# Narwal 2012 '500850394', '500850395', '500850396', '500850397', '500850398' 
# '500850422', '500850423', '500850424', '500850425', '500850426' 
orders = [500850422,500850423,500850424,500850425,500850426]
          
for order in orders:
    out = outBase + str(order) + '\\'

    downloadPath = '/orders/' + str(order) + '/'
    #print out
    

    if not os.path.exists(out):
    	print "out path did not exists, created directory"
    	os.makedirs(out)
    
    
    
        
    # open FTP client			
    ftp = FTP(ftpUrl)   # connect to host, default port

    # FTP client settings and login
    ftp.login(user=usr, passwd=pswd)
    ftp.set_pasv(True)

    # set the correct directory on the FTP site
    ftp.cwd(downloadPath)
    ftpStatus='open!'

    # get list of all files in FTP directory
    fileList=ftp.nlst()
    print "this order has ", str(len(fileList)), 'files'

    for file in fileList:
        outPath=out+file
        cmnd='RETR '+file
        
        #print file
        
        # This actually does the downloaind  
        #ftp.retrbinary(cmnd, open(downloadPath+file, 'wb').write) 
        ftp.retrbinary(cmnd, open(out+file, 'wb').write) 
        #time.sleep(15)
        
    ftp.quit()	