#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
#---TODO:

- Utilisation de redis bayes MAIS db par client !!!

- Envoi du message compressé et ajout de l'option compress dans les headers

- Personnalisation des add_header

- Daemon intermédiaire TCP ou zmq ou REST
    - client spamc python -> damon spamd python dans contenair SA ->
        - client spamc local
        ou - client spamassassin ?
    - permet aussi de crypter/compresser flux

- Utilisation de plusieurs instances spamd

- Récupération des rules avec leur points !!!
    - Tester quand whitelist !!!
    - Tester avec virus

    AMAVIS: X-Spam-Status: No, score=2.18 tag=-999 tag2=6 kill=6 tests=[BAYES_50=0.8,
        DBL_12_LETTER_FLDR=0.2, DKIM_SIGNED=0.1, DKIM_VALID=-0.1,
        DKIM_VALID_AU=-0.1, HTML_FONT_LOW_CONTRAST=0.001,
        HTML_IMAGE_RATIO_04=0.556, HTML_MESSAGE=0.001, MIME_HTML_ONLY=0.723,
        RCVD_IN_DNSWL_NONE=-0.0001, SPF_PASS=-0.001] autolearn=no
    SPAMD header
        X-Spam-Status: Yes, score=5.1 required=5.0 tests=DKIM_SIGNED,DKIM_VALID,
                DKIM_VALID_AU,HTML_IMAGE_RATIO_02,HTML_MESSAGE,T_RP_MATCHES_RCVD,
                URIBL_BLOCKED,URIBL_DBL_SPAM,URIBL_JP_SURBL autolearn=no autolearn_force=no
                version=3.4.0
    SPAM symbols
        DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,HTML_IMAGE_RATIO_02,HTML_MESSAGE,T_RP_MATCHES_RCVD,URIBL_BLOCKED,URIBL_DBL_SPAM,URIBL_JP_SURBL
    
    #etc/updates_spamassassin_org/10_default_prefs.cf    
    OK il faut un add_header _TESTSSCORES(,)_
    
    add_header all RS_SCORE _TESTSSCORES(,)_
        X-Spam-RS_SCORE: DKIM_SIGNED=0.1,DKIM_VALID=-0.1,DKIM_VALID_AU=-0.1,
                HTML_FONT_LOW_CONTRAST=0.001,HTML_IMAGE_RATIO_04=0.61,HTML_MESSAGE=0.001,
                MIME_HTML_ONLY=1.105,RCVD_IN_MSPIKE_H3=-0.01,RCVD_IN_MSPIKE_WL=-0.01,
                URIBL_BLOCKED=0.001
    

    add_header spam Flag _YESNOCAPS_
    add_header all Status _YESNO_, score=_SCORE_ required=_REQD_ tests=_TESTS_ autolearn=_AUTOLEARN_ version=_VERSION_
    add_header all Level _STARS(*)_
    add_header all Checker-Version SpamAssassin _VERSION_ (_SUBVERSION_) on _HOSTNAME_

- Envoi message GTUBE
- Envoi message brut à partir d'un fichier mail.txt ou mail.gz
- Par stdin
"""

try:
    from gevent.monkey import patch_all
    patch_all()
except ImportError:
    pass

import os, sys, re
import socket 
from cStringIO  import StringIO
import base64

SPAMC_PROTOCOL = "1.5"
EOL = "\015\012"

GTUBE = base64.b64decode('WEpTKkM0SkRCUUFETjEuTlNCTjMqMklETkVOKkdUVUJFLVNUQU5EQVJELUFOVEktVUJFLVRFU1QtRU1BSUwqQy4zNFg=')


"""
SYMBOLS 1.1
    SPAMD/1.1 0 EX_OK
    Spam: True ; 5.1 / 5.0
    DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,HTML_IMAGE_RATIO_02,HTML_MESSAGE,T_RP_MATCHES_RCVD,URIBL_BLOCKED,URIBL_DBL_SPAM,URIBL_JP_SURBL
"""

#---MODE CHECK 1.5
"""
    SPAMD/1.1 0 EX_OK
    Spam: True ; 5.1 / 5.0

    SPAMD/1.1 0 EX_OK
    Spam: False ; 1.6 / 5.0

"""

#---MODE SYMBOLS 1.5
"""
    SPAMD/1.1 0 EX_OK
    Content-length: 131
    Spam: True ; 5.1 / 5.0
    
    DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,HTML_IMAGE_RATIO_02,HTML_MESSAGE,T_RP_MATCHES_RCVD,URIBL_BLOCKED,URIBL_DBL_SPAM,URIBL_JP_SURBL
"""

#---MODE HEADERS 1.5
"""
    SPAMD/1.1 0 EX_OK
    Content-length: 767
    Spam: True ; 5.1 / 5.0
    
    Received: from localhost by 69aa3890ed8f
            with SpamAssassin (version 3.4.0);
            Sat, 29 Nov 2014 12:11:51 +0000
    From: "Blanc Cerise - GDW" <elsa@lobafu.com>
    To: s.rota@ciscar.fr
    Subject: Remises exceptionnelles sur votre linge de maison
    Date: Sat, 29 Nov 2014 11:17:01 +0100
    Message-Id: <081cd9d75fb8d09ca909f0c9c95947db@www.lobafu.com>
    X-Spam-Checker-Version: SpamAssassin 3.4.0 (2014-02-07) on 69aa3890ed8f
    X-Spam-Flag: YES
    X-Spam-Level: *****
    X-Spam-Status: Yes, score=5.1 required=5.0 tests=DKIM_SIGNED,DKIM_VALID,
            DKIM_VALID_AU,HTML_IMAGE_RATIO_02,HTML_MESSAGE,T_RP_MATCHES_RCVD,
            URIBL_BLOCKED,URIBL_DBL_SPAM,URIBL_JP_SURBL autolearn=no autolearn_force=no
            version=3.4.0
    MIME-Version: 1.0
    Content-Type: multipart/mixed; boundary="----------=_5479B807.89131629"
"""
    
#---MODE REPORT 1.5
"""
    brut:  SPAMD/1.1 0 EX_OK
    Content-length: 3189
    Spam: True ; 5.1 / 5.0
    
    
    ------------------ Rapport SpamAssassin Version 3.4.0 ------------
    Spam ?  : Yes
    Date    : Mon, 18 Sep 1972 16:57:12 +0000
    Host    : 69aa3890ed8f
    Hits    : 5.1 points sur 5.0 requis
    Bayes   : 0.5
    Learn   : no autolearn_force=no
    DCCR    :
    DCCB    :
    Pyzor   : Reported 2 times.
    Langs   :
    Ver     : 3.4.0 / 2014-02-07
    Country : _RELAYCOUNTRY_
    
    --------------------------- RBL --------------------------------------
    <dns:lobafu.com?type=MX> [5 mail.lobafu.com.]
    <dns:lobafu.com> [89.234.149.240]
    
    -------------------------- RELAYS ------------------------------------
    TRUSTED          : [ ip=127.0.0.1 rdns= helo=smtp.radicalspam.org by=localhost ident= envfrom= intl=1 id=VrAjvD9ChTNg auth= msa=0 ]
    UNTRUSTED        : [ ip=91.236.255.153 rdns=mta33fr.lobafu.com helo=mta33fr.lobafu.com by=smtp.radicalspam.org ident= envfrom= intl=0 id=BC6B9431C1BD auth= msa=0 ]
    INTERNAL         : [ ip=127.0.0.1 rdns= helo=smtp.radicalspam.org by=localhost ident= envfrom= intl=1 id=VrAjvD9ChTNg auth= msa=0 ]
    EXTERNAL         : [ ip=91.236.255.153 rdns=mta33fr.lobafu.com helo=mta33fr.lobafu.com by=smtp.radicalspam.org ident= envfrom= intl=0 id=BC6B9431C1BD auth= msa=0 ]
    LASTEXTERNALIP   : 91.236.255.153
    LASTEXTERNALRDNS : mta33fr.lobafu.com
    LASTEXTERNALHELO : mta33fr.lobafu.com
    
    ---------------------------- TESTS -----------------------------------
    DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,HTML_IMAGE_RATIO_02,HTML_MESSAGE,T_RP_MATCHES_RCVD,URIBL_BLOCKED,URIBL_DBL_SPAM,URIBL_JP_SURBL
    
    DKIM_SIGNED=0.1,DKIM_VALID=-0.1,DKIM_VALID_AU=-0.1,HTML_IMAGE_RATIO_02=0.805,HTML_MESSAGE=0.001,T_RP_MATCHES_RCVD=-0.01,URIBL_BLOCKED=0.001,URIBL_DBL_SPAM=2.5,URIBL_JP_SURBL=1.948
    
    ---------------------------- SCORES ----------------------------------
     0.0 URIBL_BLOCKED          ADMINISTRATOR NOTICE: The query to URIBL was blocked.
                                See
                                http://wiki.apache.org/spamassassin/DnsBlocklists#dnsbl-block
                                 for more information.
                                [URIs: lobafu.com]
     2.5 URIBL_DBL_SPAM         Contains a spam URL listed in the DBL blocklist
                                [URIs: lobafu.com]
    -0.0 T_RP_MATCHES_RCVD      Envelope sender domain matches handover relay
                                domain
     0.8 HTML_IMAGE_RATIO_02    BODY: HTML has a low ratio of text to image area
     0.0 HTML_MESSAGE           BODY: HTML included in message
    -0.1 DKIM_VALID             Message has at least one valid DKIM or DK signature
    -0.1 DKIM_VALID_AU          Message has a valid DKIM or DK signature from author's
                                domain
     0.1 DKIM_SIGNED            Message has a DKIM or DK signature, not necessarily valid
     1.9 URIBL_JP_SURBL         Contains an URL listed in the JP SURBL blocklist
                                [URIs: lobafu.com]
    
    
    ------------------------ PREVISUALISATION ----------------------------
    Your email client cannot read this email. To view it online,
       please go here: http://www.lobafu.com/display.php?M=288094&C=d719f28d56a562ebcc5800e7cff518ca&S=161&L=6&N=154
       To stop receiving these emails:http://www.lobafu.com/unsubscribe.php?M=288094&C=d719f28d56a562ebcc5800e7cff518ca&L=6&N=161
       [...]
    
    
"""
#---MODE PROCESS
"""
    Doit retourner comme header mais avec le message complet
"""

#---MODE TELL
"""
    To learn a message as spam:
    TELL SPAMC/1.3\r\n
    Message-class: spam\r\n
    Set: local\r\n

"""

first_line_pattern = re.compile(r'^SPAMD/[^ ]+ 0 EX_OK$')
spammy_pattern = re.compile(r'^Spam: ([^ ]+)', re.MULTILINE)
divider_pattern = re.compile(r'^(.*?)\r?\n(.*?)\r?\n\r?\n', re.DOTALL)
symbols_pattern = re.compile(r'[^\s,]+')

HOST = None
PORT = 783

"""
# available methods
SKIP = 'SKIP'
PROCESS = 'PROCESS'
CHECK = 'CHECK'
SYMBOLS = 'SYMBOLS'
REPORT = 'REPORT'
REPORT_IFSPAM = 'REPORT_IFSPAM'
"""

def _get_socket(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

def ping(host, port):
    """
    Le serveur doit renvoyer: SPAMD/1.5 0 PONG
    """
    sock = _get_socket(host, port)
    request = "PING SPAMC/%s%s" % (SPAMC_PROTOCOL, EOL)
    sock.send(request)
    sock.send(EOL)
    sock.shutdown(1)
    fp = sock.makefile('rb')
    response = fp.readline()
    print response
    #SPAMD/1.0 76 Bad header line: (EOF during headers)\r\n
    #SPAMD/1.5 0 PONG

def _recv_all(sock):
    resfp = StringIO()
    #with Timeout(self.timeout):
    while True:
        data = sock.recv(4096)
        #log.recv(sock, data)
        if data == '':
            break
        resfp.write(data)
    response = resfp.getvalue()
    
    print "brut: ", response
    
    match = divider_pattern.match(response)
    if not match:
        raise Exception("not match")
    first_line = match.group(1)
    headers = match.group(2)
    after = response[match.end(0):]
    return first_line, headers, after

def _recv_response(sock):
    first_line, headers, body = _recv_all(sock)
    symbols = symbols_pattern.findall(body)
    match = first_line_pattern.match(first_line)
    if not match:
        raise Exception("not match")
    spammy = False
    match = spammy_pattern.search(headers)
    if match and match.group(1) == 'True':
        spammy = True
    return spammy, symbols

def _build_request_str(message_data):
    reqfp = StringIO()
    data_len = len(message_data)
    reqfp.write('CHECK SPAMC/{0}\r\n'.format(SPAMC_PROTOCOL))
    #reqfp.write('HEADERS SPAMC/{0}\r\n'.format(SPAMC_PROTOCOL))
    #reqfp.write('REPORT SPAMC/{0}\r\n'.format(SPAMC_PROTOCOL))
    #reqfp.write('SYMBOLS SPAMC/{0}\r\n'.format(SPAMC_PROTOCOL))
    reqfp.write('Content-Length: {0!s}\r\n'.format(data_len))
    reqfp.write('User: {0}\r\n\r\n'.format('root'))
    #reqfp.write('User: {0}\r\n\r\n'.format(self.SPAMC_USER))
    #reqfp.write(header_data)
    reqfp.write(message_data)
    return reqfp.getvalue()

def _send_request(sock, message_data):
    request_str = _build_request_str(message_data)
    sock.sendall(request_str)
    sock.shutdown(1)
    #socket.shutdown(SHUT_WR)
    
def _scan(host, port, message_data):
    sock = None
    try:
        #socket = self._socket_creator(self.address)
        sock = _get_socket(host, port)
        _send_request(sock, message_data)
        return _recv_response(sock)
    finally:
        if sock:
            sock.close()

def check(host, port, message_data):
    spammy, symbols = _scan(host, port, message_data)
    if spammy:
        print "X-Spam-Status : YES"
        #envelope.headers['X-Spam-Status'] = 'YES'
        #envelope.headers['X-Spam-Symbols'] = ','.join(symbols)
    else:
        print "X-Spam-Status : NO"
        #envelope.headers['X-Spam-Status'] = 'NO'
    print "Symbols: %s" % ','.join(symbols)


def options():
    import argparse

    parser = argparse.ArgumentParser(description='SpamAssassin client',
                                     formatter_class=argparse.RawTextHelpFormatter, 
                                     prog=os.path.basename(sys.argv[0]), 
                                     add_help=True)

    commands = ['ping', 
                'check',
    ]    

    parser.add_argument(choices=commands,
                        dest='command',
                        help="Run command.")

    parser.add_argument(
        '--host',
        default=os.environ.get('SPAMD_HOST', "127.0.0.1"),
        help='Host spamd.  Defaults to %(default)s'
    )
        
    parser.add_argument(
        '--port',
        default=int(os.environ.get('SPAMD_PORT', PORT)),
        type=int,
        help='Port spamd.  Defaults to %(default)s'
    )

    parser.add_argument(
        '--message',
        help='filepath of message'
    )
    
    args = parser.parse_args()
       
    kwargs = dict(args._get_kwargs())
    
    return kwargs

def main():
    opts = options()
    command = opts.pop('command')
    host = opts.pop('host')
    port = opts.pop('port')
    
    if command == "ping":
        ping(host, port)
        
    elif command == "check":
        data = None
        with open(opts.pop('message')) as fp:
            data = fp.read()
        check(host, port, data)


if __name__ == "__main__":
    """
    SA_IP=$(docker inspect -f '{{.NetworkSettings.IPAddress}}' spamd1)
    python sa-client.py ${SA_IP} 783 ping 
    
    python ./sa-client.py --host 37.187.249.195 --message  messages/spam.eml check
        X-Spam-Status : YES
        Symbols: DKIM_SIGNED,DKIM_VALID,DKIM_VALID_AU,HTML_IMAGE_RATIO_02,HTML_MESSAGE,T_RP_MATCHES_RCVD,URIBL_BLOCKED,URIBL_DBL_SPAM,URIBL_JP_SURBL    
    """
    main()
    
    """
    cmd = "ping"
    if len(sys.argv) > 1:
       HOST = sys.argv[1]
    if len(sys.argv) > 2:
       PORT = int(sys.argv[2])
    if len(sys.argv) > 3:
       cmd = sys.argv[3]

    if cmd == "ping":
       ping(HOST, PORT)
       sys.exit(0)
    else:
       print "commande inconnue : %s" % cmd
       sys.exit(1)
    """