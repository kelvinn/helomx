#!/usr/bin/python
import timeit
import gc
import urllib
import simplejson
from random import randrange
from time import sleep, time
from boto.sqs.connection import SQSConnection

probe_loc = 'sg'
queue_name = 'helomx_to_%s' % probe_loc

conn = SQSConnection('', '')
q_incoming = conn.get_queue(queue_name)
q_return = conn.get_queue('helomx_return')

# We clear the queue just in case this probe was down, so we don't keep
# scanning the mailserver over and over.
q_incoming.clear()

def check_port(ip_parts):
    now = int(time())
    try:
        z = """\
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(('%s', %d))
        s.close()
        """ % (ip_parts[0], int(ip_parts[1]))
        t = timeit.Timer(stmt=z).timeit(number=1)*1000
        url = "http://www.helomx.com/api/read/port/?pk=%s&rtt=%s&probe_loc=%s&probe_time=%s&check_port=%s" % (ip_parts[2], int(t), probe_loc, now, int(ip_parts[1]))
    except:
        url = "http://www.helomx.com/api/read/port/?pk=%s&rtt=0&probe_loc=%s&probe_time=%s&check_port=%s" % (ip_parts[2], probe_loc, now, int(ip_parts[1]))
    urllib.urlopen(url)


def check_api():
    raw_json = urllib.urlopen('http://www.helomx.com/api/feed/%s/' % probe_loc).read()
    try:
        json_list = simplejson.loads(raw_json)
    except:
        json_list = None
    if json_list:
        for host_ip in json_list:
            #ip_parts = list([host_ip['fields']['ipaddr'], 25])
            ip_parts = list([host_ip['fields']['ipaddr'], 25, host_ip['pk']])
            check_port(ip_parts)
        del(json_list)
        gc.collect(2)


if __name__ == "__main__":
    while True:
        sleep(randrange(10,20))
        check_api()
        try:
            host_list = q_incoming.get_messages(10)
        except:
            host_list = False
        if host_list:
            for boto_object in host_list:
                boto_list = boto_object.get_body()
                q_incoming.delete_message(boto_object)
                if boto_list:
                    ip_list = boto_list.split(' ')
                    response_list = []

                    # we get and process the lists
                    for host_ip in ip_list:
                        if len(host_ip) > 6:
                            ip_parts = host_ip.split(':')
                            if len(ip_parts) == 3:
                                check_port(ip_parts)
            del(host_list)
            gc.collect(2)

