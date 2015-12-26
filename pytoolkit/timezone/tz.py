from datetime import datetime, timedelta
from pytz import timezone
import pytz

utc = pytz.utc
fmt = '%Y-%m-%d %H:%M:%S %Z%z'

#The preferred way of dealing with times is to always work in UTC, converting to localtime only when generating output to be read by humans.
#utc_dt = datetime(2002, 10, 27, 6, 0, 0, tzinfo=utc)
utc_dt = datetime.now(utc)
print utc_dt.strftime(fmt)
eastern = timezone('US/Eastern')
loc_dt = utc_dt.astimezone(eastern)
print loc_dt.strftime(fmt)
#before = loc_dt - timedelta(minutes=10)
#print before.strftime(fmt)
#print eastern.normalize(before).strftime(fmt)

london = timezone('Europe/London')
loc_dt2 = london.normalize(loc_dt.astimezone(london))
print loc_dt2.strftime(fmt)
loc_dt3 =  utc.normalize(loc_dt2.astimezone(utc))
print loc_dt3.strftime(fmt)

shai = timezone('Asia/Shanghai')
loc_dt4 =  shai.normalize(loc_dt3.astimezone(shai))
print loc_dt4.strftime(fmt)

#ln_dt = london.normalize(utc_dt.astimezone(london))
#print ln_dt.strftime(fmt)
#
#utc_dt2 = utc.normalize(ln_dt.astimezone(utc))
#print utc_dt2.strftime(fmt)
#
#ln_dt = datetime(2007, 10, 22, 16, 0, 0, tzinfo=london)
#print ln_dt.strftime(fmt)
#ny_dt = eastern.normalize(ln_dt.astimezone(eastern))
#print ny_dt.strftime(fmt)


