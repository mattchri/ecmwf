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
#python2.7 -i download_cams_pl.py
#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
import calendar
import os
import datetime as datetime
from dateutil.rrule import rrule, MONTHLY                                         

savepath="/group_workspaces/cems2/nceo_generic/model_data/CAMS/" 
server = ECMWFDataServer()

#Main function to download data
def download_ecmwf(start_date,end_date,vars_pl,target):
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

    #Fetch profile variables
    params = [(vars_pl[i])['param'] for i in range(len(vars_pl))]
    #target="%s%s_%s_%s.nc"%(savepath,datasetName,'pl',datestrMonth)
    print("######### CAMS Near Realtime Download  #########")
    print('get data for', target)
    print("################################")

    #CAMS level list changes to full suite of values after 2016/6/1
    jday1= datetime.datetime(start_date.year,start_date.month,start_date.day)
    jdayRef= datetime.datetime(2016,6,1)
    if (jdayRef-jday1).total_seconds() < 0:
        levl_list = "1/2/3/5/7/10/20/30/50/70/100/150/200/250/300/400/500/600/700/800/850/900/925/950/1000"
    else:
        levl_list = "1/2/3/5/7/10/20/30/50/70/100/150/200/250/300/400/500/700/850/925/1000"
    print(levl_list)
    struct = {"class": "mc",
                     "dataset": "%s"%datasetName,
                     'date'     : "%s/to/%s"%(datestrDayST,datestrDayED),
                     "expver": "0001",
                     "levtype": "pl",
                     "levelist": "%s"%levl_list,
                     'param' : '/'.join(map(str,params)),
                     "step": "3/6/9/12/15/18/21/24",
                     "stream": "oper",
                     "time": "00:00:00",
                     "type": "fc",
                     "grid": "0.4/0.4",
                     "format": "netcdf",
                     "target": "%s"%target,
                     }
    print(struct)
    server.retrieve(struct)
    return struct



# Set time:
#CAMS is available from JUL 5th 2012 - AUG 2018 (1-month prior)

#whole mission
strt_dt = datetime.date(2012,8,1)
today_dt = datetime.date.today()
end_dt = datetime.date(today_dt.year,today_dt.month-1,today_dt.day)

#selected range (CLARIFY PERIOD)
#strt_dt = datetime.date(2017,8,1)
#end_dt = datetime.date(2017,9,30)

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
    target="%s%s_%s_%s.nc"%(savepath,datasetName,'pl',datestrMonth)
    if not os.path.isfile(target):
        print('processing: ',mo,'/1/',yr,' - ',mo,'/',ndays,'/',yr)


        #For lower resolution downloads e.g. 1degree use all variables
        #vars_pl = [ {"param":"129.128","name":"z" , "long_name":"geopotential"}, 
        #            {"param":"130.128","name":"t" , "long_name":"temperature"},
        #            {"param":"157.128","name":"r" ,"long_name":"relative humidity"},
        #            {"param":"1.210"  ,"name":"aer01"  ,"long_name":"Sea Salt Aerosol (0.03 - 0.5 um)"},
        #            {"param":"2.210"  ,"name":"aer02"  ,"long_name":"Sea Salt Aerosol (0.50 - 5.0 um)"},
        #            {"param":"3.210"  ,"name":"aer03"  ,"long_name":"Sea Salt Aerosol (5.00 - 20. um)"},
        #            {"param":"4.210"  ,"name":"aer04"  ,"long_name":"Dust Aerosol (0.03 - 0.55 um)"   },
        #            {"param":"5.210"  ,"name":"aer05"  ,"long_name":"Dust Aerosol (0.55 - 0.9 um)"    },
        #            {"param":"6.210"  ,"name":"aer06"  ,"long_name":"Dust Aerosol (0.9 - 20 um)"      },
        #            {"param":"7.210"  ,"name":"aer07"  ,"long_name":"Hydrophilic OM"                  },
        #            {"param":"8.210"  ,"name":"aer08"  ,"long_name":"Hydrophobic OM"                  },
        #            {"param":"9.210"  ,"name":"aer09"  ,"long_name":"Hydrophilic BC"                  },
        #            {"param":"10.210" ,"name":"aer010" ,"long_name":"Hydrophobic BC"                  },
        #            {"param":"11.210" ,"name":"aer011" ,"long_name":"Sulphate"                        }]        
        #tmp = download_ecmwf(start_date,end_date,vars_pl,target)
        

        #Split into 3 groups to keep size under 30 Gb then merge together
        #group 1
        vars_pl = [ {"param":"129.128","name":"z" , "long_name":"geopotential"}, 
                    {"param":"130.128","name":"t" , "long_name":"temperature"},
                    {"param":"157.128","name":"r" ,"long_name":"relative humidity"},
                    {"param":"1.210"  ,"name":"aer01"  ,"long_name":"Sea Salt Aerosol (0.03 - 0.5 um)"}]
        TMPtarget1="%s%s_%s_%s_%s.nc"%(savepath,datasetName,'pl',datestrMonth,'group1')
        if not os.path.isfile(TMPtarget1):
            tmp = download_ecmwf(start_date,end_date,vars_pl,TMPtarget1)

        #group 2
        vars_pl = [ {"param":"2.210"  ,"name":"aer02"  ,"long_name":"Sea Salt Aerosol (0.50 - 5.0 um)"},
                    {"param":"3.210"  ,"name":"aer03"  ,"long_name":"Sea Salt Aerosol (5.00 - 20. um)"},
                    {"param":"4.210"  ,"name":"aer04"  ,"long_name":"Dust Aerosol (0.03 - 0.55 um)"   }]
        TMPtarget2="%s%s_%s_%s_%s.nc"%(savepath,datasetName,'pl',datestrMonth,'group2')
        if not os.path.isfile(TMPtarget2):
            tmp = download_ecmwf(start_date,end_date,vars_pl,TMPtarget2)

        #group 3
        vars_pl = [ {"param":"5.210"  ,"name":"aer05"  ,"long_name":"Dust Aerosol (0.55 - 0.9 um)"    },
                    {"param":"6.210"  ,"name":"aer06"  ,"long_name":"Dust Aerosol (0.9 - 20 um)"      },
                    {"param":"7.210"  ,"name":"aer07"  ,"long_name":"Hydrophilic OM"                  }] 
        TMPtarget3="%s%s_%s_%s_%s.nc"%(savepath,datasetName,'pl',datestrMonth,'group3')
        if not os.path.isfile(TMPtarget3):
            tmp = download_ecmwf(start_date,end_date,vars_pl,TMPtarget3)

        #group 4
        vars_pl = [ {"param":"8.210"  ,"name":"aer08"  ,"long_name":"Hydrophobic OM"                  },
                    {"param":"9.210"  ,"name":"aer09"  ,"long_name":"Hydrophilic BC"                  },
                    {"param":"10.210" ,"name":"aer010" ,"long_name":"Hydrophobic BC"                  },
                    {"param":"11.210" ,"name":"aer011" ,"long_name":"Sulphate"                        }]        
        TMPtarget4="%s%s_%s_%s_%s.nc"%(savepath,datasetName,'pl',datestrMonth,'group4')
        if not os.path.isfile(TMPtarget4):
            tmp = download_ecmwf(start_date,end_date,vars_pl,TMPtarget4)


        os.system("cdo merge "+TMPtarget1+" "+TMPtarget2+" "+TMPtarget3+" "+TMPtarget4+" "+ target)
        os.system("rm "+TMPtarget1)
        os.system("rm "+TMPtarget2)
        os.system("rm "+TMPtarget3)
        os.system("rm "+TMPtarget4)

    else:
        print('skipping: ',mo,'/1/',yr,' - ',mo,'/',ndays,'/',yr)
