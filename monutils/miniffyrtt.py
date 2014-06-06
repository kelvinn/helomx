# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="kelvinn"
__date__ ="$23/02/2010 10:27:51 AM$"

if __name__ == "__main__":
    import dateutil.parser
    from datetime import datetime, time, timedelta, date

    filter_time_start = datetime.now() - timedelta(hours=2)
    filter_time_end = datetime.now() - timedelta(hours=2)
    rtt_list = Rtt.objects.filter(ping_time__gte=filter_time).order_by('ping_time')

    # do list filter
    #



    for item in rtt_list:

        RttMinified.objects.create(mailserver=mx_obj, probe=probe_loc, ping_rtt=rtt, ping_time=ping_time)

