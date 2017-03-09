#!/bin/bash

# ***************************************************************************************
# Version : 1.1
# Date    : 01/08/2011
# Auteur  : Stéphane RAULT - stephane.rault@radicalspam.org
# ***************************************************************************************
# Changement 1.1 - 01/08/2011 :
# - Option pour afficher les résultats de compteurs sur une seule ligne, séparé par des virgules
# - Option pour utiliser un autre fichier de log
# - Le fichier de stats n'est remplacé ou mis à jour qu'a la fin de collecte des stats - plus d'écrasement pendant l'analyse par nagios
# - Ajout d'un système de verrou pour n'executer qu'une instance du script à la fois
# ***************************************************************************************

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
REVISION=`$ECHO '$Revision: 1.1 $' | $SED -e 's/[^0-9.]//g'`

print_usage() {
   $ECHO "Usage: $PROGNAME --help"
   $ECHO "Usage: $PROGNAME --version"

   $ECHO ""

   $ECHO "(defaut) - Ancienne méthode - Ajoute une ligne par compteur et remplace fichier stats"
   $ECHO "Usage: $PROGNAME --multi-lines --cpt=/tmp/stats_postfix_queue_counters --replace"
   $ECHO ""
   $ECHO "Ajoute une ligne à un fichier de compteur"
   $ECHO "Usage: $PROGNAME --one-line --cpt=${RS_BASE}/addons/nagios/var/stats_postfix_queue_counters.txt --add"

   $ECHO ""
   $ECHO "Ajoute une ligne à un fichier de compteur (version étendue)"
   $ECHO "Usage: $PROGNAME --one-line-ext --cpt=${RS_BASE}/addons/nagios/var/stats_postfix_queue_counters.txt --add"
	
   $ECHO ""
   $ECHO "Ecrit une ligne dans un fichier de compteur par écrasement du fichier"
   $ECHO "Usage: $PROGNAME --one-line --cpt=${RS_BASE}/addons/nagios/var/stats_postfix_queue_counters.txt --add"

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
   $ECHO "    --cpt=${RS_BASE}/addons/nagios/var/stats_radicalspam_logs_counters.txt"
   $ECHO ""
   $ECHO "[Option Add/Replace]"
   $ECHO "    --add                  : Remplit le fichier de compteur par ajout"
   $ECHO "    --replace              : Remplit le fichier de compteur par remplacement"
   $ECHO ""
   #$ECHO "[Options SSH] - En cours de developpement..."
   #$ECHO "    --ssh-options=\"ssh -2 -4 -l root -i /root/.ssh/id_dsa -o PreferredAuthentications=publickey 192.168.0.1\""
   #$ECHO ""
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

POSTFIX_SPOOL="${RS_BASE}/addons/postfix/var/spool"

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

if [ ! -e $POSTFIX_SPOOL ]; then
   $ECHO "Directory $POSTFIX_SPOOL not found"
   exit 1
fi

OPTION_CPT=""
OPTION_LINE=""
OPTION_REPLACE=""
OPTION_SERVER=""
OPTION_SSH=""

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
      --ssh-options)
         OPTION_SSH="$($ECHO $OPTION | $CUT -d'=' -f2)"
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
      if [ X"$OPTION_SERVER" == X"" ]; then
         OPTION_CPT="${RS_BASE}/addons/nagios/var/stats_postfix_queue_counters.txt"
      else
         OPTION_CPT="${RS_BASE}/addons/nagios/var/${OPTION_SERVER}-stats_postfix_queue_counters.txt"
      fi
   fi

   if [ X"$OPTION_REPLACE" == X"" ]; then
      OPTION_REPLACE="REPLACE"
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

if [ X"$OPTION_SSH" != X"" ]; then
   $ECHO "Fonction en cours de developpement.."
   exit 1
fi


output_file="$OPTION_CPT"
if [ ! -e $output_file ]; then
   $TOUCH $output_file
fi

debug_options()
{
   local_debug_file=$1
   log_debug $local_debug_file "OPTION_CPT      : $OPTION_CPT"
   log_debug $local_debug_file "OPTION_LINE     : $OPTION_LINE"
   log_debug $local_debug_file "OPTION_REPLACE  : $OPTION_REPLACE"
   log_debug $local_debug_file "OPTION_SSH      : $OPTION_SSH"
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

QUEUE_ALL=0
QUEUE_ACTIVE=0
QUEUE_DEFERRED=0
QUEUE_HOLD=0

# Stat pour un serveur unique. Sinon, toutes les entrées de logs
SERVER="$OPTION_SERVER"

run() {

   local_debug_file=$1

   UPTIME="`$DATE +%Y%m%d%H%M%S`"

   log_debug $local_debug_file "QUEUE_ACTIVE"
   QUEUE_ACTIVE=$($FIND $POSTFIX_SPOOL/active -type f | $WC -l)

   log_debug $local_debug_file "QUEUE_DEFERRED"
   QUEUE_DEFERRED=$($FIND $POSTFIX_SPOOL/deferred -type f | $WC -l)

   log_debug $local_debug_file "QUEUE_HOLD"
   QUEUE_HOLD=$($FIND $POSTFIX_SPOOL/hold -type f | $WC -l)

   log_debug $local_debug_file "QUEUE_ALL"
   QUEUE_ALL=$(( ${QUEUE_ACTIVE} + ${QUEUE_DEFERRED} + ${QUEUE_HOLD} ))
}

run_ssh() {

   local_debug_file=$1

   UPTIME="`$DATE +%Y%m%d%H%M%S`"

   log_debug $local_debug_file "QUEUE_ACTIVE"
   QUEUE_ACTIVE=$($OPTION_SSH $FIND $POSTFIX_SPOOL/active -type f | $WC -l)

   log_debug $local_debug_file "QUEUE_DEFERRED"
   QUEUE_DEFERRED=$($OPTION_SSH $FIND $POSTFIX_SPOOL/deferred -type f | $WC -l)

   log_debug $local_debug_file "QUEUE_HOLD"
   QUEUE_HOLD=$($OPTION_SSH $FIND $POSTFIX_SPOOL/hold -type f | $WC -l)

   log_debug $local_debug_file "QUEUE_ALL"
   QUEUE_ALL=$(( ${QUEUE_ACTIVE} + ${QUEUE_DEFERRED} + ${QUEUE_HOLD} ))

}

online_add() {
   $ECHO $1 >> $output_file
}

online_replace() {
   $ECHO $1 > $output_file
}

# La version multi-lines, écrase toujours le fichier
print_multi_lines() {
   $ECHO "UPTIME=${UPTIME}" > $output_file
   $ECHO "QUEUE_ACTIVE=${QUEUE_ACTIVE}" >> $output_file
   $ECHO "QUEUE_DEFERRED=${QUEUE_DEFERRED}" >> $output_file
   $ECHO "QUEUE_HOLD=${QUEUE_HOLD}" >> $output_file
   $ECHO "QUEUE_ALL=${QUEUE_ALL}" >> $output_file
}

print_one_lines() 
{
   local_v="${UPTIME},${QUEUE_ACTIVE},${QUEUE_DEFERRED},${QUEUE_HOLD},${QUEUE_ALL}"

   if [[ "$USE_ADD" = "true" ]]; then
      online_add $local_v
   else
      online_replace $local_v
   fi
}

print_one_lines_with_status() 
{
   local_v="UPTIME=${UPTIME},QUEUE_ACTIVE=${QUEUE_ACTIVE},QUEUE_DEFERRED=${QUEUE_DEFERRED},QUEUE_HOLD=${QUEUE_HOLD},QUEUE_ALL=${QUEUE_ALL}"

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
if [ X"$OPTION_SSH" == X"" ]; then
   run $debug_file
else
   run_ssh $debug_file
fi

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
