use strict;

$pid_file = undef;

$max_servers                = {{ filter.instances|default("2")}};

@bypass_header_checks_maps 	= (1);

$mydomain = "$ENV{MY_DOMAIN}";
$myhostname = "$ENV{MY_HOSTNAME}";

$QUARANTINEDIR = "$MYHOME/quarantine";
$quarantine_subdir_levels = 0;

$log_level = 0;
$log_recip_templ = undef;
$do_syslog = 1;
$syslog_facility = 'mail';

$enable_db = 0;
$enable_global_cache = 0;
$enable_dkim_verification = 0;
$enable_dkim_signing = 0;
#$enable_zmq = 1;

$virus_quarantine_method        = 'local:virus/%i-%n.gz';
$banned_files_quarantine_method = 'local:banned/%i-%n.gz';
$archive_quarantine_method      = 'local:archives/%i-%n.gz';
#$clean_quarantine_method        = 'local:clean/%i-%n.gz';
#$spam_quarantine_method         = 'local:spam/%i-%n.gz';

$virus_quarantine_to            = 'virus-quarantine';
$banned_quarantine_to           = 'banned-quarantine';
$bad_header_quarantine_to       = undef;
#$spam_quarantine_to             = 'spam-quarantine';
$spam_quarantine_to             = undef;
$spam_quarantine_bysender_to    = undef;
$archive_quarantine_to          = 'archive-quarantine';
#$clean_quarantine_to            = 'clean-quarantine';

$X_HEADER_TAG 			= 'X-Virus-Scanned';
$X_HEADER_LINE 			= 'by amavis';

$undecipherable_subject_tag 	= '[*** UNCHECKED ***] ';

$remove_existing_x_scanned_headers 	= 1;
$remove_existing_spam_headers  		= 1;

$inet_socket_port        	 = read_array("$MYHOME/inet_socket_port");

@local_domains_maps 		= ( read_hash("$MYHOME/local_domains") );

@mynetworks = qw( 127.0.0.0/8 [::1] [FE80::]/10 [FEC0::]/10
                  10.0.0.0/8 172.17.0.0/16 172.16.0.0/12 192.168.0.0/16 );

@mynetworks_maps = (read_array("$MYHOME/mynetworks"), \@mynetworks);

$forward_method 		= "smtp:[127.0.0.1]:10025";
$notify_method 			= $forward_method;

#FIXME: redis Insecure dependency in socket while running
@storage_redis_dsn = ( {server=>"$ENV{REDIS_SERVER}", db_id=>1} );
$redis_logging_key = 'amavis-log';
$redis_logging_queue_size_limit = 300000;  # about 250 MB / 100000

@whitelist_sender_maps 		= ( read_hash("$MYHOME/whitelist_sender") );
@blacklist_sender_maps 		= ( read_hash("$MYHOME/blacklist_sender") );
@virus_lovers_maps 		= ( read_hash("$MYHOME/virus_lovers") );
@spam_lovers_maps 		= ( read_hash("$MYHOME/spam_lovers") );
@banned_files_lovers_maps 	= ( read_hash("$MYHOME/banned_lovers") );

@bypass_virus_checks_maps = (
   \%bypass_virus_checks, \@bypass_virus_checks_acl, \$bypass_virus_checks_re);

@bypass_spam_checks_maps = (
   \%bypass_spam_checks, \@bypass_spam_checks_acl, \$bypass_spam_checks_re);

$allowed_added_header_fields{lc('Received')} 		= 0;
$allowed_added_header_fields{lc('X-Spam-Report')} 	= 1;
$allowed_added_header_fields{lc('X-Relay-Country')} 	= 1;
$allowed_added_header_fields{lc('X-Relay-Countries')} 	= 1;
$allowed_added_header_fields{lc('X-RadicalSpam')} 	= 1;

$final_virus_destiny  = D_DISCARD;
$final_banned_destiny = D_DISCARD;
$final_spam_destiny   = D_PASS;
$final_bad_header_destiny = D_PASS;
$final_unchecked_destiny = D_BOUNCE;

$warnbannedsender 		= 0;
$warnbadhsender 		= 0;
$warnvirusrecip 		= 1;
$warnbannedrecip 		= 1;
$warnbadhrecip 			= 0;
$warn_offsite 			= 1;

%banned_rules = (
  'DEFAULT' => new_RE(
    qr'.\.(ade|adp|app|bas|bat|chm|cmd|com|cpl|crt|fxp|hlp|hta|inf|ins|isp|lnk|mdt|mdw|msc|msp|mst|ops|pif|prg|reg|scr|sct|shb|shs|vbs|wsc|wsf|wsh)$'i,
  ),
);

$sa_local_tests_only 		= 0;
$sa_mail_body_size_limit 	= 400*1024; 

$sa_tag_level_deflt  		= -999.0;
$sa_tag2_level_deflt 		= 8.0;
$sa_tag3_level_deflt 		= 10.0;
$sa_kill_level_deflt 		= 10.0;
$sa_dsn_cutoff_level 		= 999.0;
$sa_quarantine_cutoff_level 	= 50;
$sa_crediblefrom_dsn_cutoff_level = 18; # likewise, but for a likely valid From
$sa_quarantine_cutoff_level = 999; # disable quarantine
$bounce_killer_score = 100;  # spam score points to add for joe-jobbed bounces

$sa_spam_subject_tag 		= undef;
@spam_subject_tag2_maps 	= ('[*** ? SPAM ***] ');
@spam_subject_tag3_maps 	= ('[*** SPAM ***] ');

my $my_from			= "$ENV{MY_ROOT_EMAIL}";
my $my_from_rfc2822		= "'Alert' <$ENV{MY_ROOT_EMAIL}>";
my $my_admin			= "$ENV{MY_ROOT_EMAIL}";

$newvirus_admin 			= $my_admin;
$virus_admin				= $my_from;		#notif.recip
$spam_admin 				= $my_admin;
$banned_admin 				= $my_admin;
$bad_header_admin 			= $my_admin;
$mailfrom_notify_admin		= $my_from;		#notif. sender
$mailfrom_notify_recip		= $my_from;		#notif. sender
$mailfrom_notify_spamadmin	= $my_from;		#notif. sender
$mailfrom_to_quarantine 	= '';

@av_scanners = (
 ['ClamAV-clamd',
   \&ask_daemon, ["CONTSCAN {}\n", "/var/run/clamav/clamd.ctl"],
   qr/\bOK$/m, qr/\bFOUND$/m,
   qr/^.*?: (?!Infected Archive)(.*) FOUND$/m ],
);

@av_scanners_backup = (
#  ['ClamAV-clamscan', 'clamscan',
#    "--stdout --no-summary -r --tempdir=$TEMPBASE {}",
#    [0], qr/:.*\sFOUND$/m, qr/^.*?: (?!Infected Archive)(.*) FOUND$/m ],
);

#include_config_files('/etc/amavis/amavis.d/amavis-custom.conf');

#------------ Do not modify anything below this line -------------
1;  # ensure a defined return
