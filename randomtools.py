

# To do the last week until now():
# fake_big_fill('test1', 'au', 55, 7, 0)

# If today is a Monday, to add M-F last week:
# fake_big_fill('test1', 'au', 55, 7, 2)
def fake_big_fill(mxslug, probe_loc, ping_rtt, start_time_ago, end_time_ago):
    from monitor.models import Rtt
    from hosts.models import Mailserver
    from datetime import datetime, timedelta
    from random import randrange

    f_start = datetime.now()-timedelta(days=start_time_ago)
    f_end = datetime.now()-timedelta(days=end_time_ago)

    mx_obj = Mailserver.objects.get(slug=mxslug)
    while f_start < f_end:
        f_start = f_start + timedelta(minutes=1)
        Rtt.objects.create(mailserver=mx_obj, probe=probe_loc, ping_time=f_start,ping_rtt=ping_rtt+randrange(1, 3))


def fake_minified_fill(mxslug, probe_loc, ping_rtt, start_time_ago, end_time_ago):
    from monitor.models import RttMinified
    from monitor.views import minifyrtt
    from hosts.models import Mailserver
    from datetime import datetime, timedelta
    from random import randrange

    f_start = datetime.now()-timedelta(days=start_time_ago)
    f_end = datetime.now()-timedelta(days=end_time_ago)

    mx_obj = Mailserver.objects.get(slug=mxslug)
    while f_start < f_end:
        f_start = f_start + timedelta(hours=1)
        minifyrtt(mx_obj, probe_loc, f_start, ping_rtt+randrange(1, 3), 'up')


