helomx
======

HeloMX **was** a personal side project to build a mailserver monitoring system circa 2009-2010. It included the following features:

+ Multiple probes in different countries that measured response times (i.e. ICMP latency)
+ Measurement of connection times to the desired mailserver port
+ Automated blacklist testing
+ Monitoring of open relay
+ Alerting (email / SMS) of any errors
+ Graphing of response times / latency (at various intervals)
+ Payment via Paypal
+ Architected around multiple AWS tools
+ Probably other stuff I have since forgotten

The front of it looked like this (I don't think Bootstrap existed back then):

![alt text](https://lh6.googleusercontent.com/-uvhT9mopwD0/U5HA2MBp23I/AAAAAAAANJc/qNYBdxYaArg/w900-h845-no/HeloMX.png "HeloMX Screenshot")

After a number of months working on HeloMX in the evenings, it got to the point where it worked, and worked quite well. I put it out there for people to test, nobody complained, but it never took off. I promoted it a little, but I was only picking up a few users from time to time. Technically the tool worked great - I used it on all my clients at the time - yet I never really marketed it. After a few more months of minimal usage, I had learned a lot, but realised this probably wouldn't let me retire anytime soon, so turned it off.

Four or five years later and I've finally package up the repository and stick it on GitHub, not because I want to collaborate, but perhaps some snippet somewhere will be useful. To that end, now that I look back, there are some Lessons Learned:

I wish I had read *The Four Steps to the Epiphany* much, much earlier. I spent many months creating a product before talking to people, let alone anybody who would actually pay to use it. It eventually turned into more of a technical excercise than a product to market and produce enough income to feed myself. I should have talked first, programmed second. Or even better, found a company that had to manage a lot of mailservers and built it for them.

There are some things I just couldn't have changed due to it being five years ago when I started this project, e.g. I couldn't give myself a recommendation to use AngularJS and Bootstrap instead of jQuery and YUI, or to just use django-rest-framework instead of building my own API. Setting that aside, there are several technical things that, looking back, I deserved a slap on the wrist

+ No attention to tests. I had always been coding just for myself: C++ in High School/Uni, PHP in Uni, then onto Python and Java. Many developers I encounter even now don't write tests, and I can't help but think *what was I thinking*. There is a lot of gratification having Jenkins pull down your commit and see your Lint score improve.
+ No configuration management. I didn't really have an excuse to not use Puppet, even as a solo developer. I probably downloaded it and got an SSL cert error and went about my normal ways of creating install scripts. However, after stumbling on the writings of Martin Fowler, I realised just how much better all of this should be done. I once found it interesting when I saw developers not even bothering with version control - isn't that obvious? - I feel the same way now about people not even thinking about CI/CD. It is rewarding to have Jenkins fire up a blank VM, pull the config from SaltStack, configure everything, run my tests, and terminate (after 30 minutes of not more commits). I know my configs and code work well together. *What was I thinking...*
+ Wrong choice of stack. I had very simple linear data. I probably should have fired up Hadoop and built more experience with that, instead of sticking it in Postgres and writing custom scripts to reduce it. It probably would have been a good career move, now that everybody loves "big data".

Live and learn. And now to the next project...
