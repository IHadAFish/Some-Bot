import pytz, re
from datetime import datetime
from glob import iglob
from SomeError import SomeError

def get_timezone(zone):
    #return a pytz.timezone obj.
    for t_zone in iglob("./pytz/zoneinfo/**", recursive=True):
        if t_zone.upper().endswith("\\" + zone.upper()):
            temp = t_zone.replace("./pytz/zoneinfo\\", "").replace("\\", "/")
            return pytz.timezone(temp)

    raise SomeError("location_not_exist")

def get_datetime(t_time, t_date=None, zone=pytz.timezone("UTC")):

    #Take date and time as string, timezone as datetime.timezone obj, returh datetime obj.
    #date string should have format dd-mm or dd-mm-yyyy

    #date
    if not t_date:
        t_date = datetime.now(tz=zone)
    else:
        if re.match("\d-", t_date):
            t_date = "0" + t_date

        if re.search("-\d-", t_date) or re.search("-\d$", t_date):
            t_date.replace("-", "-0", 1)

        if re.match("\d\d-\d\d$", t_date):
            t_date += "-" + str(datetime.today().year)

        t_date = datetime.strptime(t_date, "%d-%m-%Y").date()

    #time
    if re.match("\d:", t_time):
        t_time = "0" + t_time

    if re.search("(:\d$)|(:\dam)|(:\dpm)", t_time):
        t_time = t_time.replace(":", ":0")

    if len(t_time) == 1:
        t_time = "0" + t_time

    if t_time.endswith("m"):
        if ":" in t_time:
            time_format = "%I:%M%P"
        else:
            time_format = "%H%P"
    else:
        if ":" in t_time:
            time_format = "%H:%M"
        else:
            time_format = "%H"

    return datetime.combine(t_date, datetime.strptime(t_time, time_format).time(), tzinfo=zone)

def time_convert(origin_tz, target_tz, t_time):

    origin_time = get_datetime(t_time, zone=origin_tz)
    target_time = origin_time.astimezone(tz=target_tz)
    print("origin", repr(origin_tz))
    print("target", repr(target_tz))

    day_diff = origin_time - target_time

    return target_time, day_diff

def datetime_convert(origin_tz, target_tz, t_time, t_date):

    origin_time = get_datetime(t_time, t_date, zone=origin_tz)

    return origin_time.astimezone(target_tz)

def delta_convert(f_tz, s_tz, f_time, f_date, s_time, s_date):

    f_datetime = get_datetime(f_time, f_date, f_tz)
    s_datetime = get_datetime(s_time, s_date, s_tz)

    return f_datetime - s_datetime

def time_converter(origin, target, mode, t_time, t_date=None, s_time=None, s_date=None):

    #return a datetime or timedelta obj repsenting the new time.
    t_time = t_time.strip().lower()
    origin_tz = get_timezone(origin)
    target_tz = get_timezone(target)

    if mode == "t":
        return time_convert(origin_tz, target_tz, t_time)
    elif mode == "dt":
        if not t_date:
            raise ValueError
        return datetime_convert(origin_tz, target_tz, t_time, t_date)
    else:
        if not (t_date and s_time and s_date):
            raise ValueError
        return delta_convert(origin_tz, target_tz, t_time, t_date, s_time, s_date)
