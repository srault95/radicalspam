#!/bin/bash

# ***************************************************************************************
# Version : 1.3
# Date    : 01/08/2011
# Auteur  : Stéphane RAULT - stephane.rault@radicalspam.org
# ***************************************************************************************
# Changement 1.1 :
# - Correction pour la génération des stats cumulés
# ***************************************************************************************
# Changement 1.2 :
# - Ajout d'une ligne de recherche maillog-xxx
# - Ajout de 4 compteurs : SMTP_DELAY_EXT, SMTP_DELAY_LOCAL, POSTGREY_DELAY, MAIL_SIZE
# ***************************************************************************************
# Changement 1.3 :
# - Option pour afficher les résultats de compteurs sur une seule ligne, séparé par des virgules
# - Option pour utiliser un autre fichier de log
# - Le fichier de stats n'est remplacé ou mis à jour qu'a la fin de collecte des stats - plus d'écrasement pendant l'analyse par nagios
# - Ajout d'un système de verrou pour n'executer qu'une instance du script à la fois
# ***************************************************************************************

# ---------------------------------------------------------------------------------------
# TODO: Si le fichier de log est fournie en paramètre, il faut aussi pouvoir utiliser un uptime différent ?
# TODO: Compteurs a renommer en CPT_XXX pour facilier la documentation, le référencement et l'activation/désactivation
# TODO: https://support.radical-spam.org/public/ticket/186
#       - Exclure les MAILER-DAEMON ou les comptabiliser à part
#       - Rejets postgrey
#       - Rejets RBL avec paramètre pour fournir RBL
#       - Rejets ANTI-SPOOFING
#       - Rejets FQDN 
# TODO: Revoir le MAILLOG_FORMAT !!!
# ---------------------------------------------------------------------------------------
# FIXME: Voir pourquoi --cpt=./fichier enregistrer dans répertoire parent !
# ---------------------------------------------------------------------------------------

if [ -e /var/rs ]; then
   . /var/rs/etc/radicalspam.conf
   . /var/rs/etc/scripts/common.sh  
else
   . /etc/radicalspam.conf
   . /etc/scripts/common.sh
fi

PROGNAME=`$BASENAME $0`
PROGPATH=`$ECHO $0 | $SED -e 's,[\\/][^\\/][^\\/]*$,,'`
REVISION=`$ECHO '$Revision: 1.3 $' | $SED -e 's/[^0-9.]//g'`

print_usage() {
   $ECHO "Usage: $PROGNAME --help"
   $ECHO "Usage: $PROGNAME --version"

   $ECHO ""

   $ECHO "(defaut) - Ancienne méthode - Ajoute une ligne par compteur et remplace fichier stats"
   $ECHO "Usage: $PROGNAME --multi-lines --cpt=/tmp/postfix_counters.txt --replace --log=/var/log/maillog-18072011.log"
   $ECHO ""
   $ECHO "Ajoute une ligne à un fichier de compteur"
   $ECHO "Usage: $PROGNAME --one-line --cpt=${RS_BASE}/addons/nagios/var/stats_postfix_logs_counters.txt --add"

   $ECHO ""
   $ECHO "Ajoute une ligne à un fichier de compteur (version étendue)"
   $ECHO "Usage: $PROGNAME --one-line-ext --cpt=${RS_BASE}/addons/nagios/var/stats_postfix_logs_counters.txt --add"
	
   $ECHO ""
   $ECHO "Ecrit une ligne dans un fichier de compteur par écrasement du fichier"
   $ECHO "Usage: $PROGNAME --one-line --cpt=${RS_BASE}/addons/nagios/var/stats_postfix_logs_counters.txt --add"

   $ECHO ""
   $ECHO "--------------------------------------------------------------------------------------------------------"
   $ECHO "Paramètres :"
   $ECHO ""
   $ECHO "[Modes]"
   $ECHO "     --multi-lines         : Une ligne par compteur"
   $ECHO "     --one-line            : Une ligne pour tous les compteurs"
   $ECHO "     --one-line-ext        : Une ligne pour tous les compteurs avec nom de chaque compteur"
   $ECHO ""
   $ECHO "[Fichier de compteur]"
   $ECHO "    --cpt=${RS_BASE}/addons/nagios/var/stats_postfix_logs_counters.txt"
   $ECHO ""
   $ECHO "[Option Add/Replace]"
   $ECHO "    --add                  : Remplit le fichier de compteur par ajout"
   $ECHO "    --replace              : Remplit le fichier de compteur par remplacement"
   $ECHO ""
   $ECHO "[Fichier de log]"
   $ECHO "    --log=/var/log/maillog : Utilisera le fichier de log fournit sinon utilisera celui configuré dans radicalspam.conf" 
   $ECHO ""
   $ECHO "[Server]"
   $ECHO "    --server=MX1           : Analysera seulement les entrées pour le serveur MX1 sinon toutes les entrées"
   $ECHO "--------------------------------------------------------------------------------------------------------"
	
}

print_help() {
   $ECHO $PROGNAME $REVISION
   $ECHO ""
   print_usage
}

BASE_DIR=`dirname $0`
SCRIPT_NAME=`basename $0`

case "$1" in
   --help)
      print_help
      exit 0
      ;;
   --version)
      $ECHO $PROGNAME $REVISION
      exit 0
      ;;
esac

OPTION_CPT=""
OPTION_LINE=""
OPTION_LOGFILE=""
OPTION_REPLACE=""
OPTION_SERVER=""

for OPTION in $@; do
   case "$OPTION" in
      --multi-lines)
         OPTION_LINE="MULTI"
         ;;
      --one-line)
         OPTION_LINE="ONE"
         ;;
      --one-line-ext)
         OPTION_LINE="ONE-EXT"
         ;;
      --cpt*)
         OPTION_CPT="$($ECHO $OPTION | $CUT -d'=' -f2)"
         ;;
      --add)
         OPTION_REPLACE="ADD"  
         ;;
      --replace)
         OPTION_REPLACE="REPLACE"
         ;;
      --log*)
         OPTION_LOGFILE="$($ECHO $OPTION | $CUT -d'=' -f2)"
         ;;
      --server*)
         OPTION_SERVER="$($ECHO $OPTION | $CUT -d'=' -f2)"
         ;;
      *)
         $ECHO "***************************************************"
         $ECHO "!!! Bad parameter : $OPTION"
         $ECHO "***************************************************"
         print_usage
         exit 1
         ;;
   esac
done

search_maillog || exit 1

#Vérifie les arguments et initialise les valeurs par défaut si nécessaire
verify_args() {

   if [ X"$OPTION_LINE" == X"" ]; then
      OPTION_LINE="MULTI"
   fi

   if [ X"$OPTION_CPT" == X"" ]; then
      OPTION_CPT="${RS_BASE}/addons/nagios/var/stats_postfix_logs_counters.txt"
   fi

   if [ X"$OPTION_REPLACE" == X"" ]; then
      OPTION_REPLACE="REPLACE"
   fi

   if [ X"$OPTION_LOGFILE" == X"" ]; then
      OPTION_LOGFILE=$LOG_MAILLOG
   fi

}

verify_args

#Verifie compatibilité des options :
if [ $OPTION_LINE = "MULTI" ]; then
   if [ $OPTION_REPLACE = "ADD" ]; then
      $ECHO "L'option REPLACE est incompatible avec le mode Multi-Lignes"
      exit 1
   fi
fi

logfile="$OPTION_LOGFILE"
if [ ! -e $logfile ]; then
   $ECHO "File not found : $logfile"
   exit 1
fi

output_file="$OPTION_CPT"
if [ ! -e $output_file ]; then
   $TOUCH $output_file
fi

debug_options()
{
   local_debug_file=$1
   log_debug $local_debug_file "OPTION_LOGFILE  : $OPTION_LOGFILE"
   log_debug $local_debug_file "OPTION_CPT      : $OPTION_CPT"
   log_debug $local_debug_file "OPTION_LINE     : $OPTION_LINE"
   log_debug $local_debug_file "OPTION_REPLACE  : $OPTION_REPLACE"
   log_debug $local_debug_file "OPTION_SERVER   : $OPTION_SERVER"
}

#Si true, ajoute le contenu à la dernière ligne du fichier ouput existant
#Si false, remplace le contenu du fichier ouput par le nouveau contenu
USE_ADD="true"

if [[ "$OPTION_REPLACE" = "REPLACE" ]]; then
   USE_ADD="false"
fi

if [[ "$OPTION_REPLACE" = "ADD" ]]; then
   USE_ADD="true"
fi

REJECT_5XX=0
REJECT_4XX=0
REJECT_WARNING=0
REJECT_CLIENT=0
REJECT_SENDER=0
REJECT_RECIPIENT=0
ERROR=0
WARNING=0
SMTP_MAIL_SENT=0
SMTP_MAIL_DEFERRED=0
SMTP_MAIL_BOUNCED=0
SMTP_DELAY_EXT=0
SMTP_DELAY_LOCAL=0
MAIL_SIZE=0
POSTGREY_DELAY=0

# Stat pour un serveur unique. Sinon, toutes les entrées de logs
SERVER="$OPTION_SERVER"

parse_log() {

   local_debug_file=$1

   UPTIME="`$DATE +%Y%m%d%H%M%S`"

   local_tmp_logfile="/tmp/${SCRIPT_NAME}-$($BASENAME $logfile)"

   if [ X"$SERVER" = X"" ]; then
      $CAT $logfile | $GREP -E '(postfix/|postgrey\[)' > $local_tmp_logfile
   else
      $CAT $logfile | $GREP -E '(postfix/|postgrey\[)' | $GREP " $SERVER" > $local_tmp_logfile
   fi

   log_debug $local_debug_file "REJECT_5XX"
   REJECT_5XX=$($CAT $local_tmp_logfile | $GREP 'postfix/smtpd\[' | $GREP 'reject:' | $GREP -E '\]: (554|550|504|501) ' | $WC -l)

   log_debug $local_debug_file "REJECT_4XX"
   REJECT_4XX=$($CAT $local_tmp_logfile | $GREP 'postfix/smtpd\[' | $GREP 'reject:' | $GREP -E '\]: (450) ' | $WC -l)

   log_debug $local_debug_file "REJECT_WARNING"
   REJECT_WARNING=$($CAT $local_tmp_logfile | $GREP 'postfix/smtpd\[' | $GREP 'reject_warning:' | $WC -l)

   log_debug $local_debug_file "REJECT_CLIENT"
   REJECT_CLIENT=$($CAT $local_tmp_logfile | $GREP " $SERVER" | $GREP 'postfix/smtpd\[' | $GREP 'reject:' | $GREP 'Client host rejected:' | $WC -l)

   log_debug $local_debug_file "REJECT_SENDER"
   REJECT_SENDER=$($CAT $local_tmp_logfile | $GREP 'postfix/smtpd\[' | $GREP 'reject:' | $GREP 'Sender address rejected:' | $WC -l)

   log_debug $local_debug_file "REJECT_RECIPIENT"
   REJECT_RECIPIENT=$($CAT $local_tmp_logfile | $GREP 'postfix/smtpd\[' | $GREP 'reject:' | $GREP 'Recipient address rejected:' | $GREP -v ' Greylisted' | $WC -l)

   log_debug $local_debug_file "ERROR"
   ERROR=$($CAT $local_tmp_logfile | $GREP 'postfix/' | $GREP -E '\]: (error|fatal|panic): ' | $WC -l)

   log_debug $local_debug_file "WARNING"
   WARNING=$($CAT $local_tmp_logfile | $GREP 'postfix/' | $GREP '\]: warning: ' | $WC -l)

   log_debug $local_debug_file "SMTP_MAIL_SENT"
   SMTP_MAIL_SENT=$( $CAT $local_tmp_logfile | $GREP 'postfix/smtp\[' | $GREP 'status=sent' | $GREP -v 'relay=127.0.0.1' | $WC -l)

   log_debug $local_debug_file "SMTP_MAIL_DEFERRED"
   SMTP_MAIL_DEFERRED=$($CAT $local_tmp_logfile | $GREP 'postfix/smtp\[' | $GREP 'status=deferred' | $WC -l)

   log_debug $local_debug_file "SMTP_MAIL_BOUNCED"
   SMTP_MAIL_BOUNCED=$($CAT $local_tmp_logfile | $GREP 'postfix/smtp\[' | $GREP 'status=bounced' | $WC -l)

   log_debug $local_debug_file "SMTP_DELAY_EXT"
   SMTP_DELAY_EXT=$($CAT $local_tmp_logfile | $GREP 'postfix/smtp\[' | $GREP 'status=sent' | $GREP -v 'orig_to=' | $GREP -v 'relay=127.0.0.1' | $AWK -F 'delay=' '{ print $2}' | $CUT -d ',' -f1 | $AWK 'BEGIN{ CONVFMT="%d"; cpt=0; val=0} { cpt++; val=val+$1  } END{ if ( val > 0 ) { printf "%d",((val/cpt)) } else { print "0" } }')

   log_debug $local_debug_file "SMTP_DELAY_LOCAL"
   SMTP_DELAY_LOCAL=$($CAT $local_tmp_logfile | $GREP 'postfix/smtp\[' | $GREP 'status=sent' | $GREP -v 'orig_to=' | $GREP 'relay=127.0.0.1' | $AWK -F 'delay=' '{ print $2}' | $CUT -d ',' -f1 | $AWK 'BEGIN{ CONVFMT="%d"; cpt=0; val=0} { cpt++; val=val+$1  } END{ if ( val > 0 ) { printf "%d",((val/cpt)) } else { print "0" } }')

   log_debug $local_debug_file "MAIL_SIZE"
   MAIL_SIZE=$($CAT $local_tmp_logfile | $GREP 'postfix/qmgr' | $GREP 'size=' | $AWK -F 'size=' '{ print $2}' | $CUT -d',' -f1 | $AWK 'BEGIN{ CONVFMT="%d"; cpt=0; val=0} { cpt++; val=val+$1  } END{ if ( val > 0 ) { printf "%d",((val/cpt)/1024) } else { print "0" } }')

   log_debug $local_debug_file "POSTGREY_DELAY"
   POSTGREY_DELAY=$($CAT $local_tmp_logfile | $GREP 'postgrey\[' | $GREP 'delay=' | $AWK -F 'delay=' '{ print $2 }' | $CUT -d ',' -f1 | $AWK 'BEGIN{ CONVFMT="%d"; cpt=0; val=0} { cpt++; val=val+$1} END{ if ( val > 0 ) { printf "%d",((val/cpt)/60) } else { print "0" } }')

   rm -f $local_tmp_logfile

}

online_add() {
   $ECHO $1 >> $output_file
}

online_replace() {
   $ECHO $1 > $output_file
}

# La version multi-lines, écrase toujours le fichier
print_multi_lines() {
   $ECHO "UPTIME=$UPTIME" > $output_file
   $ECHO "REJECT_5XX=$REJECT_5XX" >> $output_file
   $ECHO "REJECT_4XX=$REJECT_4XX" >> $output_file
   $ECHO "REJECT_WARNING=$REJECT_WARNING" >> $output_file
   $ECHO "REJECT_CLIENT=$REJECT_CLIENT" >> $output_file
   $ECHO "REJECT_SENDER=$REJECT_SENDER" >> $output_file
   $ECHO "REJECT_RECIPIENT=$REJECT_RECIPIENT" >> $output_file
   $ECHO "ERROR=$ERROR" >> $output_file
   $ECHO "WARNING=$WARNING" >> $output_file
   $ECHO "SMTP_MAIL_SENT=$SMTP_MAIL_SENT" >> $output_file
   $ECHO "SMTP_MAIL_DEFERRED=$SMTP_MAIL_DEFERRED" >> $output_file
   $ECHO "SMTP_MAIL_BOUNCED=$SMTP_MAIL_BOUNCED" >> $output_file
   $ECHO "SMTP_DELAY_EXT=$SMTP_DELAY_EXT" >> $output_file
   $ECHO "SMTP_DELAY_LOCAL=$SMTP_DELAY_LOCAL" >> $output_file
   $ECHO "MAIL_SIZE=$MAIL_SIZE" >> $output_file
   $ECHO "POSTGREY_DELAY=$POSTGREY_DELAY" >> $output_file
}

print_one_lines() 
{
   local_v="${UPTIME},${REJECT_5XX},${REJECT_4XX},${REJECT_WARNING},${REJECT_CLIENT},${REJECT_SENDER},${REJECT_RECIPIENT},${ERROR},${WARNING},${SMTP_MAIL_SENT},${SMTP_MAIL_DEFERRED},${SMTP_MAIL_BOUNCED},${SMTP_DELAY_EXT},${SMTP_DELAY_LOCAL},${MAIL_SIZE},${POSTGREY_DELAY}"

   if [[ "$USE_ADD" = "true" ]]; then
      online_add $local_v
   else
      online_replace $local_v
   fi
}

print_one_lines_with_status() 
{
   local_v= "UPTIME=${UPTIME},REJECT_5XX=${REJECT_5XX},REJECT_4XX=${REJECT_4XX},REJECT_WARNING=${REJECT_WARNING},REJECT_CLIENT=${REJECT_CLIENT},REJECT_SENDER=${REJECT_SENDER},REJECT_RECIPIENT=${REJECT_RECIPIENT},ERROR=${ERROR},WARNING=${WARNING},SMTP_MAIL_SENT=${SMTP_MAIL_SENT},SMTP_MAIL_DEFERRED=${SMTP_MAIL_DEFERRED},SMTP_MAIL_BOUNCED=${SMTP_MAIL_BOUNCED},SMTP_DELAY_EXT=${SMTP_DELAY_EXT},SMTP_DELAY_LOCAL=${SMTP_DELAY_LOCAL},MAIL_SIZE=${MAIL_SIZE},POSTGREY_DELAY=${POSTGREY_DELAY}"

   if [[ "$USE_ADD" = "true" ]]; then
      online_add $local_v
   else
      online_replace $local_v
   fi
}


#/var/rs/tmp/stats_postfix_logs.sh.lock
lockfile="${RS_BASE}/tmp/${SCRIPT_NAME}.lock"

debug_file="${RS_BASE}/tmp/${SCRIPT_NAME}.log"

#Verification de l'etat du process
get_lock $lockfile $debug_file

lock_debug $debug_file "BEGIN"

debug_options $debug_file

#Lance l'analyse des logs
parse_log $debug_file

case "$OPTION_LINE" in
   MULTI)
      print_multi_lines
      ;;
   ONE)
      print_one_lines
      ;;
   ONE-EXT)
      print_one_lines_with_status
      ;;   
esac

lock_debug $debug_file "END"

#Release du verrou
release_lock $lockfile $debug_file


exit 0
