;CREATE ANIMATION OF AOD TIMESERIES DEMONSTRATING PULSING BEHAVIOR OF
;THE PRODUCT
PRO ANIMATE_CAMS

FNAME = '/group_workspaces/cems2/nceo_generic/model_data/CAMS/cams_nrealtime_sfc_201708.nc'
STAT=READ_NCDF(FNAME,DAT)
caldat,julday(1,1,1900,0,0)+dat.time/24D,mm,dd,yyyy,hh,mn

for i=0,n_elements(dat.time)-1 do begin
lat = REVERSE( FINDGEN(N_ELEMENTS(dat.latitude)+1)*(179./float(N_ELEMENTS(dat.latitude)))-89.5 )
lon = FINDGEN(N_ELEMENTS(dat.longitude)+1)*(359./float(N_ELEMENTS(dat.longitude)))+0.5
lon = (lon lt 180.)*lon + (lon ge 180.)*(lon-360)
data = dat.aod550[*,*,i]


opath = '/group_workspaces/jasmin2/cloud_ecv/public/mchristensen/ecmwf_animation/'
file_mkdir,opath

TIMEstr = STRING(FORMAT='(I02,"/",I02,"/",I04," ",I02,":",I02)',mm[i],dd[i],yyyy[i],hh[i],mn[i])
fname = opath+'aod_img_'+string(format='(i04)',i)
chk=file_search(fname+'.png',count=chkct)
 if chkct eq 0 then begin
  void=plot_map_l3(lon,lat,data,0.,11,0.,.5,[-90,-180,90,180],1,199,20,'aod550',labelStr=TIMEstr,labelLoc=[.51,.3,1],/CONVERTtoPNG,oFile=fname)
 endif


lat = REVERSE( FINDGEN(N_ELEMENTS(dat.latitude)+1)*(179./float(N_ELEMENTS(dat.latitude)))-89.5 )
lon = FINDGEN(N_ELEMENTS(dat.longitude)+1)*(359./float(N_ELEMENTS(dat.longitude)))+0.5
lon = (lon lt 180.)*lon + (lon ge 180.)*(lon-360)
data = dat.t2m[*,*,i]


opath = '/group_workspaces/jasmin2/cloud_ecv/public/mchristensen/ecmwf_animation/'
file_mkdir,opath

TIMEstr = STRING(FORMAT='(I02,"/",I02,"/",I04," ",I02,":",I02)',mm[i],dd[i],yyyy[i],hh[i],mn[i])
fname = opath+'t2m_img_'+string(format='(i04)',i)
chk=file_search(fname+'.png',count=chkct)
 if chkct eq 0 then begin
  void=plot_map_l3(lon,lat,data,0.,11,265.,310.,[-90,-180,90,180],1,199,20,'t2m (K)',labelStr=TIMEstr,labelLoc=[.51,.3,1],/CONVERTtoPNG,oFile=fname)
 endif


endfor
imgs = file_search(opath+'aod_img_*.png')
html_script,imgs,'aod','',outPath=opath

imgs = file_search(opath+'t2m_img_*.png')
html_script,imgs,'t2m','',outPath=opath

STOP
END
