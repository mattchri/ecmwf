#This routine downloads CAMS reanalysis products from ECMWF
#Standard setup: monthly increment output data at 1x1 degree resolution
#                every 3 hours using analysis step 00:00 with forecast steps 3/6/9/12/15/18/21/24
#
#The data for MACC is only provided for the 00:00 analysis time-step. CAMS has 0 & 12
#but there is a problem with the AOD fields pulsating when MODIS data is assimilated.
#Therefore to create a consistent record we update daily using forecast data.
#
#Note, if full data output is desired the following should be selected:
#analysis times: 0/6/12/18 with timestep 0 combined with analysis times 00:00 & 12:00 and forecast steps 3/9
#
#The netcdf files can be merged using the following command:
#os.system("cdo -b F64 mergetime outputAN.nc outputFC.nc outputFULL.nc")
#see example script below
#------------------------------------------------------------------------------------------

#python2.7 -i download_cams_sfc.py
#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
import calendar
import os
import datetime as datetime
from dateutil.rrule import rrule, MONTHLY                                         
                                            
savepath="/group_workspaces/cems2/nceo_generic/model_data/CAMS/" 
server = ECMWFDataServer()


def download_ecmwf(start_date,end_date):
    dateST=start_date
    dateED=end_date
    datestrMonth=dateST.strftime("%Y%m") 
    datestrDayST=dateST.strftime("%Y%m%d") 
    datestrDayED=dateED.strftime("%Y%m%d") 

    # Restrict area

    global_data=True;    

    # Boundaries (not necessary when global=True)
    boundary_west=-180 # West boundary in degrees -180 to 180
    boundary_east=-180 # East boundary in degrees -180 to 180
    boundary_south=-90 # South boundary in degrees -180 to 180
    boundary_north=90  # North boundary in degrees -180 to 180

    if global_data:
        boundarystring= "-90/-180/90/180"
    else:
        boundarystring= "%s/%s/%s/%s"%(boundary_south,boundary_west,boundary_north,boundary_east)

    #data set
    datasetName = 'cams_nrealtime'

    #parameters:

    vars_sfc = [ {"param":"207.210","name":"aod550", "long_name":"total AOD at 550 nm"},
                 {"param":"208.210","name":"ssaod" , "long_name":"sea salt AOD at 550 nm"},
                 {"param":"209.210","name":"duaod" , "long_name":"dust AOD at 550 nm"},
                 {"param":"210.210","name":"omaod" , "long_name":"organic matter AOD at 550 nm"},
                 {"param":"211.210","name":"bcaod" , "long_name":"black carbon AOD at 550 nm"},
                 {"param":"212.210","name":"suaod" , "long_name":"sulphate AOD at 550 nm"},
                 {"param":"215.210","name":"aod865", "long_name":"total AOD at 865 nm"}]


    #Fetch surface variables
    params = [(vars_sfc[i])['param'] for i in range(len(vars_sfc))]
    target="%s%s_%s_%s.nc"%(savepath,datasetName,'sfc',datestrMonth)
    print("######### CAMS Near Realtime Download  #########")
    print('get data for', target)
    print("################################")
    struct = {"class": "mc",
                 "dataset": "%s"%datasetName,
                 'date'     : "%s/to/%s"%(datestrDayST,datestrDayED),
                 "expver": "0001",
                 "levtype": "sfc",
                 'param' : '/'.join(map(str,params)),
                 "step": "3/6/9/12/15/18/21/24",
                 "stream": "oper",
                 "time": "00:00:00",
                 "type": "fc",
                 "grid": "0.4/0.4",
                 "format": "netcdf",
                 "target": "%s"%target,
                 }
    server.retrieve(struct)
    return struct

# Set time:
strt_dt = datetime.date(2012,8,1)
today_dt = datetime.date.today()
end_dt = datetime.date(today_dt.year,today_dt.month-1,today_dt.day)
month_dates = [dt for dt in rrule(MONTHLY, dtstart=strt_dt, until=end_dt)]
for i in range(len(month_dates)):
    yr = month_dates[i].year
    mo = month_dates[i].month
    start_date=datetime.date(yr,mo,1)
    ndays = (calendar.monthrange(yr,mo))[1]
    end_date=datetime.date(yr,mo,ndays)

    #Check if the data was already downloaded
    datestrMonth=month_dates[i].strftime("%Y%m") 
    datasetName = 'cams_nrealtime'
    target="%s%s_%s_%s.nc"%(savepath,datasetName,'sfc',datestrMonth)
    if not os.path.isfile(target):
        print('processing: ',mo,'/1/',yr,' - ',mo,'/',ndays,'/',yr)
        tmp = download_ecmwf(start_date,end_date)
    else:
        print('skipping: ',mo,'/1/',yr,' - ',mo,'/',ndays,'/',yr)

