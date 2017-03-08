Postfix Protocol
================

http://www.postfix.org/SMTPD_POLICY_README.html

Postfix 2.12 - Nouveaux paramètres
----------------------------------

::

    smtpd_policy_service_request_limit (default: 0)
    
        The maximal number of requests per SMTPD policy service connection, or zero (no limit). Once a connection reaches this limit, the connection is closed and the next request will be sent over a new connection. This is a workaround to avoid error-recovery delays with policy servers that cannot maintain a persistent connection.
    
        This feature is available in Postfix 2.12 and later.

    smtpd_policy_service_retry_delay (default: 1s)
    
        The delay between attempts to resend a failed SMTPD policy service request. Specify a value greater than zero.
    
        This feature is available in Postfix 2.12 and later.
    
    smtpd_policy_service_try_limit (default: 2)
    
        The maximal number of attempts to send an SMTPD policy service request before giving up. Specify a value greater than zero.
    
        This feature is available in Postfix 2.12 and later.

    smtpd_policy_service_default_action (default: 451 4.3.5 Server configuration problem)
    
        The default action when an SMTPD policy service request fails. Specify "DUNNO" to behave as if the failed SMTPD policy service request was not sent, and to continue processing other access restrictions, if any.
    
        Limitations:
    
            This parameter may specify any value that would be a valid SMTPD policy server response (or access(5) map lookup result). An access(5) map or policy server in this parameter value may need to be declared in advance with a restriction_class setting.
    
            If the specified action invokes another check_policy_service request, that request will have the built-in default action.
    
        This feature is available in Postfix 2.12 and later.


Réponse possible d'un serveur Policy à la fin de la transaction
---------------------------------------------------------------

::

    4NN text
    DUNNO optional text...              # Ne sait pas - Pas de décision
    WARN optional text...               # Aucune action mais Postfix ajoutera le warning dans ses logs
    5NN optional text...                # Rejet définitif du mail
    521 text (Postfix 2.6 and later)    # pour botnets et malware
    REJECT optional text...             # comme ci-dessus
    FILTER transport:destination        # Demande à postfix de soumettre le mail au filtre (amavis)
    HOLD optional text...               # Postfix placera le mail en queue HOLD
    PREPEND headername: headervalue     # Ajout d'entête dans le mail
    REJECT using zen.spamhaus.org; http://www.spamhaus.org/query/bl?ip=41.211.139.61;
    
Plusieurs Actions possibles à la chaine
---------------------------------------

::

    action=BCC user@domain
    action=ADD_HEADER X-Spam-Verdict: OK
    action=WARN This policy was delegate
    [empty line] (= \n\n)

    DOC: postconf XCLIENT et serveur policy :
    
        - Avant :        
        smtpd_client_restrictions = permit_mynetworks, check_client_access hash:/addons/postfix/etc/local-whitelist-clients, check_client_access hash:/addons/postfix/etc/local-blacklist-clients, reject_rbl_client zen.spamhaus.org
        smtpd_recipient_restrictions = check_recipient_access hash:/addons/postfix/etc/local-blacklist-recipients, reject_non_fqdn_recipient, reject_unauth_destination, check_policy_service inet:127.0.0.1:10023, reject_unlisted_recipient, check_recipient_access hash:/addons/postfix/etc/local-filters-in
        smtpd_sender_restrictions = permit_mynetworks, check_sender_access hash:/addons/postfix/etc/local-whitelist-senders, reject_non_fqdn_sender, check_sender_access hash:/addons/postfix/etc/local-spoofing, check_sender_access hash:/addons/postfix/etc/local-blacklist-senders
        smtpd_reject_unlisted_recipient = yes
        smtpd_reject_unlisted_sender = no
        smtpd_delay_reject = yes
        
    -----------------------------------------------------------------------------------------------
    
        
    -----------------------------------------------------------------------------------------------
    
        - Apres :
        postconf -e 'smtpd_client_restrictions =' 
        postconf -e 'smtpd_recipient_restrictions = check_policy_service inet:192.168.0.120:7080, reject_unauth_destination'
        postconf -e 'smtpd_sender_restrictions ='
        postconf -e 'smtpd_reject_unlisted_recipient = no'
        postconf -e 'smtpd_reject_unlisted_sender = no'
        
        
                
        > Utiliser un fichier de mapping :
        postconf -e 'smtpd_authorized_xclient_hosts = 192.168.0.120 127.0.0.1 192.168.0.125'
        smtpd_delay_reject = yes
                

Paramètres postfix supplémentaires
----------------------------------
    
::
    
    Paramètre pour éviter le NOQUEUE dans les logs :
        postconf -e 'smtpd_delay_open_until_valid_rcpt = no'
    
    Paramètre postfix pour obliger à ne distribuer qu'à un seul destinataire à la fois :
        postconf -e 'default_destination_recipient_limit = 1'
        #default: default_destination_recipient_limit = 50

Tests avec python SMTP et XCLIENT
---------------------------------

::
    
    #pour générer queueID même quand aucun RCPT n'a été accepté mettre à 'no'
    #(défaut : yes)
    $ postconf -e 'smtpd_delay_open_until_valid_rcpt = no' 
    $ postconf -e 'smtpd_delay_reject = no'
    $ postconf -e "smtpd_authorized_xclient_hosts = 127.0.0.1"
    $ postfix reload
    $ python
    >>> import smtplib
    >>> s = smtplib.SMTP()
    >>> s.set_debuglevel(1)
    >>> ret_code = s.connect('127.0.0.1', 2500)
    >>> ret_code = s.docmd('XCLIENT', 'PROTO=ESMTP ADDR=127.0.0.1 NAME=smtp.test.net HELO=test.net')
    >>> ret_code = s.docmd('MAIL FROM:', smtplib.quoteaddr("sender@test.net") )
    >>> ret_code = s.docmd('RCPT TO:', smtplib.quoteaddr("recipient1@test.net") )
    >>> ret_code = s.docmd('RCPT TO:', smtplib.quoteaddr("recipient2@test.net") )
    >>> s.quit()
    $ postconf -e 'smtpd_delay_reject = yes'
    $ postconf -e 'smtpd_authorized_xclient_hosts ='
    $ postfix reload
                
                
Extractions Log postgrey sur mx mutualisé
-----------------------------------------

::

    gzip -cd /var/log/maillog-11072014.log.1.gz | grep postgrey | grep sender | awk -F 'client_name=' '{ print "client_name="$2}' >/tmp/postgrey-2014-07-11
    client_name=revd64.neolane.net, client_address=195.154.153.64, sender=voyages-sncf@newsletter.voyages-sncf.com, recipient=gg@abakus.fr
    client_name=marketing-message.net, client_address=78.46.98.113, sender=root@marketing-message.net, recipient=info@abakus.fr
    #senders:
    cat /tmp/postgrey-2014-07-11 | awk '{ print $3}' | cut -d '@' -f2 | sort -f | uniq -c -i | sort -f -k1,1 -rn | more     
        91 pole-emploi.fr,
        43 blois.fr,
        42 gmail.com,
        38 orange.fr,
        28 sendgrid.info,
        26 renault.com,
    #recipients:
    cat /tmp/postgrey-2014-07-11 | awk '{ print $4}' | cut -d '@' -f2 | sort -f | uniq -c -i | sort -f -k1,1 -rn | more
        540 ciasdublaisois.fr
        446 gcrfrance.com
        366 brasseurs-de-france.com
        338 ciscar.fr
        263 abakus.fr
         64 globallp.com
         55 csem.fr
         52 snbr.fr
         25 gcnf.fr
    
            