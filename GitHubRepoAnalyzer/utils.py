import datetime
import pytz

class TimeUtils:
    @staticmethod
    def days_elapsed(reference_date, d):
        s = int((reference_date - d).total_seconds())
        return s // (24 * 60 * 60)  # seconds per day

    @staticmethod
    def human_elapsed_time(reference_date, d):
        if (d > reference_date):
           return "Some time in the future (?)"
        s = int((reference_date - d).total_seconds())
        # if s < 0:
        #     return "Some time in the future (?)"
        if s == 0:
            return "Just now"
        minute = 60
        hour = 60 * minute
        day = 24 * hour
        month = 30 * day

        def msg(s, unit_size, unit_name):
            count = s // unit_size
            pluralized = unit_name
            if count > 1:
               pluralized += 's'
            return "{n} {units} ago".format(n = count, units = pluralized)
        if s < minute:  return "< 1 minute ago"
        if s < hour:    return msg(s, minute, 'minute')
        if s < day:     return msg(s, hour, 'hour')
        if s < month:   return msg(s, day, 'day')
        if s < 2*month: return "1 month ago"
        if s < 7*month: return "{n} months ago".format(n = s // month)
        return "> 6 months ago"
