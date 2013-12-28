Name:         privoxyTor
Purpose:      Using multiple Tor connections simultaneously

Narrator:     In a project, I wanted to use multiple Tor connections to
              anonymously crawl a website. I googled and got a good answer for
              using one instance of Tor at:
              http://stackoverflow.com/questions/9887505/changing-tor-identity-inside-python-script
              But for multiple instances, how could we could that? I decided
              to write a Python script automating the configuration process and
              making Tor easier to use. I hope it works out well for you!

Usage:        Before running the demo accompanied with this script, you have
              to prepare prepare directory /abstract:
              1. Copy the installation of Tor to /abstract/tor
              2. Copy /conf/tr to  /abstract/tor
              3. Copy the installation of Privoxy to /abstract/privoxy
              4. Copy /conf/privoxy to  /abstract/privoxy

Author:       Anh Le

Dependencies: Tor (standalone)    https://www.torproject.org/download/download.html.en
              Privoxy             http://www.privoxy.org/

Created:      27/12/2013
Copyright:    (c) AnhLD 2013
Licence:      LGPL-2.1
