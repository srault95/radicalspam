#!/bin/bash

# ***************************************************************************************
# Version : 1.3
# Date    : 01/08/2011
# Auteur  : Stéphane RAULT - stephane.rault@radicalspam.org
# ***************************************************************************************
# Changement 1.1:
# - Correction pour la génération des stats cumulés
# ***************************************************************************************
# Changement 1.2:
# - Ajout d'une ligne de recherche maillog-xxx
# - Ajout de 2 compteurs : PROCESS_TIME_INPUT, PROCESS_TIME_OUTPUT
# - Ajout du compteur SA_TIMED_OUT pour les timeout d'interrogation SpamAssassin par Amavis
# ***************************************************************************************
# Changement 1.3 - 01/08/2011 :
# - Option pour afficher les résultats de compteurs sur une seule ligne, séparé par des virgules
# - Option pour utiliser un autre fichier de log
# - Le fichier de stats n'est remplacé ou mis à jour qu'a la fin de collecte des stats - plus d'écrasement pendant l'analyse par nagios
# - Ajout d'un système de verrou pour n'executer qu'une instance du script à la fois
# ***************************************************************************************

# ---------------------------------------------------------------------------------------
# TODO: TEMPFAIL|OVERSIZED|BAD-HEADER
# TODO: Ajouter freshclam/update
# TODO: Si le fichier de log est fournie en paramètre, il faut aussi pouvoir utiliser un uptime différent ?
# TODO: Compteurs a renommer en CPT_XXX pour facilier la documentation, le référencement et l'activation/désactivation
# TODO: https://support.radical-spam.org/public/ticket/186
# TODO: TEMPFAIL|OVERSIZED|BAD-HEADER
# TODO: Ajouter freshclam/update
# TODO: DCC dccproc (not asking)
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
   $ECHO "Usage: $PROGNAME --multi-lines --cpt=/tmp/radicalspam_counters.txt --replace --log=/var/log/maillog-18072011.log"
   $ECHO ""
   $ECHO "Ajoute une ligne à un fichier de compteur"
   $ECHO "Usage: $PROGNAME --one-line --cpt=/var/rs/addons/nagios/var/stats_radicalspam_logs_counters.txt --add"

   $ECHO ""
   $ECHO "Ajoute une ligne à un fichier de compteur (version étendue)"
   $ECHO "Usage: $PROGNAME --one-line-ext --cpt=/var/rs/addons/nagios/var/stats_radicalspam_logs_counters.txt --add"
	
   $ECHO ""
   $ECHO "Ecrit une ligne dans un fichier de compteur par écrasement du fichier"
   $ECHO "Usage: $PROGNAME --one-line --cpt=/var/rs/addons/nagios/var/stats_radicalspam_logs_counters.txt --add"

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
   $ECHO "    --cpt=/var/rs/addons/nagios/var/stats_radicalspam_logs_counters.txt"
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

search_maillog || exit 1

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

#Vérifie les arguments et initialise les valeurs par défaut si nécessaire
verify_args() {

   if [ X"$OPTION_LINE" == X"" ]; then
      OPTION_LINE="MULTI"
   fi

   if [ X"$OPTION_CPT" == X"" ]; then
      OPTION_CPT="${RS_BASE}/addons/nagios/var/stats_radicalspam_logs_counters.txt"
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

# DEBUT PATCH AMAVIS 2.7
USE_AMAVIS_2_7=0
RELEASE_AMAVIS="$($CAT ${RS_BASE}/addons/amavis/RELEASE.TXT | $HEAD -1 | $AWK '{ print $2}')"
if [ X"$RELEASE_AMAVIS" = X"2.7.0"  ]; then
   USE_AMAVIS_2_7=1
fi
# FIN PATCH AMAVIS 2.7

VIRUS=0
SPAM=0
SPAMMY=0
BANNED=0
UNCHECKED=0
PROCESS_TIME_INPUT=0
PROCESS_TIME_OUTPUT=0
SA_TIMED_OUT=0

# Stat pour un serveur unique. Sinon, toutes les entrées de logs
SERVER="$OPTION_SERVER"

parse_log() {

   local_debug_file=$1

   UPTIME="`$DATE +%Y%m%d%H%M%S`"

   local_tmp_logfile="/tmp/${SCRIPT_NAME}-$($BASENAME $logfile)"

   #Exclusion de postfix et postgrey
   if [ X"$SERVER" = X"" ]; then
      $CAT $logfile | $GREP -vE '(postfix/|postgrey\[)' > $local_tmp_logfile
   else
      $CAT $logfile | $GREP -vE '(postfix/|postgrey\[)' | $GREP " $SERVER" > $local_tmp_logfile
   fi

   log_debug $local_debug_file "VIRUS"
   VIRUS=$($CAT $local_tmp_logfile | $GREP -E '(Blocked INFECTED|Passed INFECTED)' | $WC -l)
   
   log_debug $local_debug_file "SPAM"
   SPAM=$($CAT $local_tmp_logfile | $GREP -E '(Blocked SPAM|Passed SPAM)' | $GREP -v 'SPAMMY' | $WC -l)

   log_debug $local_debug_file "SPAMMY"
   SPAMMY=$($CAT $local_tmp_logfile | $GREP -E '(Blocked SPAMMY|Passed SPAMMY)' | $WC -l)

   log_debug $local_debug_file "BANNED"
   BANNED=$($CAT $local_tmp_logfile | $GREP -E '(Blocked BANNED|Passed BANNED)' | $WC -l)

   log_debug $local_debug_file "UNCHECKED"
   UNCHECKED=$($CAT $local_tmp_logfile | $GREP -E '(Blocked UNCHECKED|Passed UNCHECKED)' | $WC -l)

   #if [ $USE_AMAVIS_2_7 -eq 0 ]; then

   log_debug $local_debug_file "PROCESS_TIME_INPUT"
   PROCESS_TIME_INPUT=$($CAT $local_tmp_logfile | $GREP 'amavis\[' | $GREP -E '(Passed|Blocked)' | $GREP -v 'output' | $AWK -F 'mail_id' '{ print $2 }' | $AWK -F ',' '{ if ( /queued_as/ ) { v=$5 } else { v=$4 }; print v }' |  $AWK '{ print $1}' | $AWK 'BEGIN{ CONVFMT="%d"; cpt=0; val=0} { cpt++; val=val+$1  } END{ if ( val > 0 ) { printf "%d",((val/cpt)/1000) } else { print "0" } }')

   log_debug $local_debug_file "PROCESS_TIME_OUTPUT"
   PROCESS_TIME_OUTPUT=$($CAT $local_tmp_logfile | $GREP 'amavis\[' | $GREP -E '(Passed|Blocked)' | $GREP 'output' | $AWK -F 'mail_id' '{ print $2 }' | $AWK -F ',' '{ if ( /queued_as/ ) { v=$5 } else { v=$4 }; print v }' |  $AWK '{ print $1}' | $AWK 'BEGIN{ CONVFMT="%d"; cpt=0; val=0} { cpt++; val=val+$1  } END{ if ( val > 0 ) { printf "%d",((val/cpt)/1000) } else { print "0" } }')

   log_debug $local_debug_file "SA_TIMED_OUT"
   SA_TIMED_OUT=$($CAT $local_tmp_logfile | $GREP 'SA TIMED OUT' | $WC -l) 

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
   $ECHO "VIRUS=$VIRUS" >> $output_file
   $ECHO "SPAM=$SPAM" >> $output_file
   $ECHO "SPAMMY=$SPAMMY" >> $output_file
   $ECHO "BANNED=$BANNED" >> $output_file
   $ECHO "UNCHECKED=$UNCHECKED" >> $output_file
   $ECHO "PROCESS_TIME_INPUT=$PROCESS_TIME_INPUT" >> $output_file
   $ECHO "PROCESS_TIME_OUTPUT=$PROCESS_TIME_OUTPUT" >> $output_file
   $ECHO "SA_TIMED_OUT=$SA_TIMED_OUT" >> $output_file
}

print_one_lines() 
{
   local_v="${UPTIME},${VIRUS},${SPAM},${SPAMMY},${BANNED},${UNCHECKED},${PROCESS_TIME_INPUT},${PROCESS_TIME_OUTPUT},${SA_TIMED_OUT}"

   if [[ "$USE_ADD" = "true" ]]; then
      online_add $local_v
   else
      online_replace $local_v
   fi
}

print_one_lines_with_status() 
{
   local_v="UPTIME=${UPTIME},VIRUS=${VIRUS},SPAM=${SPAM},SPAMMY=${SPAMMY},BANNED=${BANNED},UNCHECKED=${UNCHECKED},PROCESS_TIME_INPUT=${PROCESS_TIME_INPUT},PROCESS_TIME_OUTPUT=${PROCESS_TIME_OUTPUT},SA_TIMED_OUT=${SA_TIMED_OUT}"

   if [[ "$USE_ADD" = "true" ]]; then
      online_add $local_v
   else
      online_replace $local_v
   fi
}

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
