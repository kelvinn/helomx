import socket
from django.core.cache import cache
servers = {
'arin': 'whois.arin.net',
'ripe': 'whois.ripe.net',
'apnic': 'whois.apnic.net',
'lacnic': 'whois.lacnic.net',
'afrinic': 'whois.afrinic.net',
'asia': 'whois.nic.asia',
'biz': 'whois.biz',
'com': 'whois.internic.net',
'coop': 'whois.nic.coop',
'info': 'whois.afilias.net',
'jobs': 'jobswhois.verisign-grs.com',
'mobi': 'whois.dotmobiregistry.net',
'name': 'whois.nic.name',
'net': 'whois.verisign-grs.com',
'org': 'whois.pir.org',
'pro': 'whois.registrypro.pro',
'tel': 'whois.nic.tel',
'travel': 'whois.nic.travel',
'gov': 'whois.dotgov.gov',
'edu': 'whois.educause.edu',
'int': 'whois.iana.org',
'museum': 'whois.museum',
'ac': 'whois.nic.ac',
'ae': 'whois.nic.ae',
'ag': 'whois.nic.ag',
'am': 'whois.amnic.net',
'at': 'whois.nic.at',
'au': 'whois.audns.net.au',
'be': 'whois.dns.be',
'bg': 'whois.register.bg',
'bj': 'whois.nic.bj',
'br': 'whois.registro.br',
'ca': 'whois.cira.ca',
'ch': 'whois.nic.ch',
'ci': 'whois.nic.ci',
'cl': 'whois.nic.cl',
'cn': 'whois.cnnic.net.cn',
'cx': 'whois.nic.cx',
'cz': 'whois.nic.cz',
'de': 'whois.denic.de',
'dk': 'whois.dk-hostmaster.dk',
'ee': 'whois.eenet.ee',
'fi': 'whois.ficora.fi',
'fr': 'whois.nic.fr',
'gd': 'whois.adamsnames.com',
'gg': 'whois.channelisles.net',
'gi': 'whois2.afilias-grs.net',
'gs': 'whois.nic.gs',
'gw': 'whois.nic.gw',
'gy': 'whois.registry.gy',
'hk': 'whois.hkirc.hk',
'hn': 'whois2.afilias-grs.net',
'ie': 'whois.domainregistry.ie',
'il': 'whois.isoc.org.il',
'in': 'whois.inregistry.net',
'io': 'whois.nic.io',
'ir': 'whois.nic.ir',
'is': 'whois.isnic.is',
'it': 'whois.nic.it',
'je': 'whois.channelisles.net',
'jp': 'whois.jprs.jp',
'ke': 'whois.kenic.or.ke',
'kg': 'www.domain.kg',
'ki': 'whois.nic.ki',
'kr': 'whois.nic.or.kr',
'kz': 'whois.nic.kz',
'la': 'whois.nic.la',
'li': 'whois.nic.li',
'lt': 'whois.domreg.lt',
'lu': 'whois.dns.lu',
'lv': 'whois.nic.lv',
'ly': 'whois.nic.ly',
'ma': 'whois.iam.net.ma',
'mg': 'whois.nic.mg',
'mn': 'whois.nic.mn',
'ms': 'whois.adamsnames.tc',
'mx': 'whois.nic.mx',
'my': 'whois.mynic.net.my',
'na': 'whois.na-nic.com.na',
'nl': 'whois.domain-registry.nl',
'no': 'whois.norid.no',
'nu': 'whois.nic.nu',
'nz': 'whois.srs.net.nz',
'pl': 'whois.dns.pl',
'pm': 'whois.nic.pm',
'pr': 'whois.uprr.pr',
're': 'whois.nic.re',
'ro': 'whois.rotld.ro',
'ru': 'whois.ripn.net',
'sa': 'whois.nic.net.sa',
'sb': 'whois.nic.net.sb',
'sc': 'whois2.afilias-grs.net',
'se': 'whois.iis.se',
'sg': 'whois.nic.net.sg',
'sh': 'whois.nic.sh',
'si': 'whois.arnes.si',
'st': 'whois.nic.st',
'tc': 'whois.adamsnames.tc',
'tf': 'whois.nic.tf',
'tk': 'whois.dot.tk',
'tl': 'whois.nic.tl',
'tm': 'whois.nic.tm',
'tr': 'whois.nic.tr',
'tw': 'whois.twnic.net.tw',
'ua': 'whois.net.ua',
'ug': 'whois.co.ug',
'uk': 'whois.nic.uk',
'us': 'whois.nic.us',
'uz': 'whois.cctld.uz',
'vc': 'whois2.afilias-grs.net',
've': 'whois.nic.ve',
'vg': 'whois.adamsnames.tc',
'wf': 'whois.nic.wf',
'ws': 'whois.website.ws',
'yt': 'whois.nic.yt',
}
class ClientException(Exception):
        pass
class Client:
  def __init__(self):
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  def __del__(self):
    self._socket.close()
  def query(self, item):
    item = item.split(".");
    print item[-1]
    if(item[-1] not in servers):
      return False
    server = servers[item[-1]]
    print server
    #data = cache.get('whois_%s' % item)
    item = '.'.join(item)
    print item

    try:
        self._socket.connect((server, 43 ))
        self._socket.send(item+'\n')
        print "sent"
    except socket.error, msg1:
        self._socket.close()
        return msg1

    data = []
    try:
        while True:
            print "receiving"
            chunk = self._socket.recv(1024)
            print str(chunk)
            print "a"
            if not chunk: break
            data.append(chunk)
        return ''.join(data)
    except socket.error, msg2:
        return msg2


