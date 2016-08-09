#!/usr/bin/perl -W
#--------------------------------------------------------------
# This example PERL script:
# - calls the TRDS_SL program from http://x-server.gmca.aps.anl.gov/
# - tracks calculation.
# - gets and saves the data.
# The example is equivalent to the following page:
# http://x-server.gmca.aps.anl.gov/cgi/WWW_form.exe?template=TRDS_sl_omega.htm&method=post
#
# PERL interpreter is available by default on UNIX and MAC OS. Freeware
# PERL distribution for Windows can be installed either as a part of Cygwin
# (http://www.cygwin.com), or as a standalone package available from
# ActiveState (http://www.activestate.com/).
#
# To access data from remote web site, this script makes use of PERL LWP
# module (WWW library for Perl). The latter is usually a part of standard
# PERL distribution; otherwise it can be freely downloaded from CPAN
# (http://www.cpan.org/).
#
# This example script can be freely distributed and modified without any
# restrictions.
#
#     		Author: Sergey Stepanov
#
# Version-1.0:  2012/12/18
#--------------------------------------------------------------
  use strict;
  use LWP::Simple;			# World-Wide Web library for Perl (libwww-perl)
  use LWP::UserAgent;

  select STDOUT; $|=1;			# set unbuffered output

  my ($url, $prg, $query, $unzip, %FORM);
  my ($request, $name, $buffer, $jobID);
  my ($error_text, $status, $data_found);
  my ($ua, $response, $progress, $start_time, $end_time);

  $start_time = time();

### General parameters:
  $url   = 'http://x-server.gmca.aps.anl.gov';
  $prg   = $url.'/cgi/TRDS_frm.pl';
  $query = $url.'/cgi/WWWwatch.exe?';
  $unzip = $url.'/cgi/WWWunzip.exe?';

  $FORM{'comment1'} = 'Template: Perl script getTRDS_query_post';

### X-rays:
  $FORM{'xway'}     = 1;		# 1=wavelength, 2=energy, 3=line type
  $FORM{'wave'}     = 1.540562;		# works with xway=1 or xway=2
# $FORM{'line'}     = 'Cu-Ka1';		# works with xway=3 only
  $FORM{'line'}     = '';		# works with xway=3 only
  $FORM{'ipol'}     = 1;		# 1=sigma-polarization, 2=pi-polarization

### Substrate:
  $FORM{'subway'}   = 1;		# 1=database_code, 2=chemical_formula, 3=x0_value
  $FORM{'code'}     = 'GaAs';		# crystal code
  $FORM{'chem'}     = '';		# Chemical formula: works with subway=2 only
  $FORM{'rho'}      = '';		# Density (g/cm3): required for chemical formula
  $FORM{'x0'}       = '(0.,0.)';	# Direct input of chi_0: x0=2*delta (subway=3)
  $FORM{'w0'}       = 1.;		# Debye-Waller type correction for x0

### Substrate surface:
  $FORM{'sigma'}    = 3.;		# rms roughness at surface (Angstrom)

### Database Options for dispersion corrections df1, df2:
### -1 - Automatically choose DB for f',f"
###  0 - Use X0h data (5-25 keV or 0.5-2.5 A) -- recommended for Bragg diffraction.
###  2 - Use Henke data (0.01-30 keV or 0.4-1200 A) -- recommended for soft x-rays.
###  4 - Use Brennan-Cowan data (0.03-700 keV or 0.02-400 A)
  $FORM{'df1df2'}   = -1;

### Type of scan:
###  1: Theta-scans at fixed 2Theta
###  2: Theta-2Theta scans at fixed Theta-offsets
###  3: 2Theta (detector) scans at fixed Theta
###  4: qx scans at fixed qz
  $FORM{'scan'}     = 1;		# minimum scan angle (range)
  $FORM{'scanmin'}  = 0.;		# minimum scan angle (range)
  $FORM{'scanmax'}  = 2.;		# maximum scan angle (range)
  $FORM{'nscan'}    = 201;		# number of scan points
  $FORM{'offmin'}   = 2.;		# minimum offset angle (range)
  $FORM{'offmax'}   = 2.;		# maximum offset angle (range)
  $FORM{'noff'}     = 1;		# number of offset points
  $FORM{'unis'}     = 0;		# scan/offset angle units: 0=degr.,1=min,2=mrad,3=sec,4=urad
  $FORM{'unia'}     = 0;		# qx,qz units: 0=1/A (do not change!)

### What to compute at the specular rod:
  $FORM{'spec'}     = 1;		# 0=diffuse scattering, 1=specular reflectivity

### Accelerators:
  $FORM{'Fourier'} = 0;			# 1=Use K instead of exp(K)-1 (small rms roughness),
					# 0=use exp(K)-1.
  $FORM{'Born'}    = 0;			# 1=Use semi-Born approximation (ignore scattering
                            		# from reflected waves), 0=use DWBA (all waves)

### Roughness models and parameters:
### See brief documentation at
### http://x-server.gmca.aps.anl.gov/TRDS_sl.html
  $FORM{'Lh'}	   = 1000.;	    	# lateral correlation length of roughness in Angstrem
  $FORM{'jagg'}    = 1.;	    	# rougness jaggedness (acceptable range: 0.1-1)
  $FORM{'Lv'}      = '';	    	# vertical correlation length of roughness in Angstrem
  $FORM{'skew'}    = 0.;	    	# angle of skew rougness correlation between interfaces
  $FORM{'uniw'}    = 0;		    	# skew angle units: 0=degr.,1=min,2=mrad,3=sec,4=urad
### Hint:
### The script can be called in a loop or
### from a fitting program. Then, it may be
### helpful to pass some parameters to the
### script as command line arguments:
# $FORM{'Lh'}   = $ARGV[0];
# $FORM{'jagg'} = $ARGV[1];

### Affine-type rougness models (see basic theory in Sinha,Sirota,Garoff,Stanley,
### Phys.Rev.B, 38 (1988) 2297, and program implementation details in Kaganer,
### Stepanov, Koehler, Physica B, 221, (1996) 33).
###   1: Uncorrelated roughness
###   2: Completely correlated roughness
###   3: Ming's model -- Ming,Krol,Soo,Kao,Park,Wang, Phys.Rev.B 47 (1993) 16373.
###   4: Lagally's model -- Phang,Savage,Kariotis,Lagally, J.Appl.Phys. 74 (1993) 3181.
###   5: Holy's model -- Holy,Baumbach, Phys.Rev.B 49 (1994) 10669.
###   6: Spiller's model (*very slow!*) -- Spiller,Stearns,Krumrey, J.Appl.Phys. 74 (1993) 107.
### Models of scattering from atomic steps at vicinal interfaces (see details in
### Kondrashkina,Stepanov,Opitz,Schmidbauer,Koehler,Hey,Wassermeier,Novikov,
### Phys.Rev.B, 56 (1997) 10469).
###   7: Classic Pukite's model -- Pukite,Lent,Cohen, Surf.Sci. 161 (1985) 39.
###   8: Smoothed Pukite's model -- Pukite,Lent,Cohen, Surf.Sci. 161 (1985) 39.
###   9: Pershan's model -- Rabedeau,Tidswell,Pershan,Bevk,Freer, Appl.Phys.Lett. 59 (1991) 3422.
  $FORM{'model'}   = 2;
  $FORM{'Lh2'}     = '';	    	# lateral size of vertically correlated roughness
				    	# in Angstem for Lagally's model.
  $FORM{'Qm'}      = 0.;	    	# miscut angle for all scattering-from-steps models (7-9)
  $FORM{'unim'}    = 0;		    	# miscut angle units: 0=degr.,1=min,2=mrad,3=sec,4=urad
  $FORM{'add'}     = 0;		    	# add affine roughness to scattering-from-steps models (7-9)
  $FORM{'stepH'}   = 0.;	    	# effect.rms height of steps (Angstrem) for smoothed Pukite's model (8)
  $FORM{'spread'}  = 0.;	    	# terraces size spread (Angstrem) for Pershan's model (9)

  $FORM{'watch'}   = 1;			# job watching option: do not change as this script only works with watch=1

### Surface layer profile
### (can also be read from
## a filename specified in
### the command line):
  $FORM{'profile'} = '';
### This is an example of non-empty profile:
### (use with care because the length of calculations
### is proportional to the 4th power of the number of
### layers, n^4). Long calculations may not return
### results within browser timeout. There is a way to
### detouch them from the browser session, but this
### script does not implement detouched sessions.
#  $FORM{'profile'} = '
# t=20 w0=0.5 sigma=5   !surface oxide, organic contamination or dust
# period=3
# t=100 code=GaAs sigma=4
# t=70 code=AlAs sigma=4
# end period
# ';

#-----------------------------------------------------------
### Request data from the server:
  print STDOUT 'Request string:'."\n".$prg."\n";

  $ua = LWP::UserAgent->new;
# $ua = LWP::UserAgent->new(keep_alive=>1);
### Get/set the timeout value in seconds. The default timeout()
### value is 180 seconds, i.e. 3 minutes.
# $ua->timeout(650);

### Request data from the server:
  $response = $ua->post($prg,\%FORM);
  if (! $response->is_success) {
     print STDOUT "\n".'*** getTRDS: Error reading response from the server: %s'."\n", $response->status_line;
     $end_time = time();
     printf STDOUT 'Elapsed time=%ds'."\n", int($end_time-$start_time);
#    die $response->status_line;
     exit 1;
  }

  $buffer = $response->content;
  $buffer =~ s/[\r\n]//g;			# remove CR/LF

### Find job ID on the server:
  $jobID = $buffer;
  if ($buffer =~ /Download ZIPped results:/i) {
### Remove all text before and after job name in the string like:
### Download ZIPped results: <A HREF="x-ray/TDSxxxxx.zip">TDSxxxxx.zip</A>
     $jobID =~ s/^.*Download ZIPped results: <A HREF=\"x-ray\///i;
     $jobID =~ s/\.zip.*$//i;
  }
  elsif ($buffer =~ /Job ID:/i) {
### Job is in progress:
### Remove all text before and after job name in the string like:
### Job ID: <b>TDS70410</b>
     $jobID =~ s/^.*Job ID: <b>//i;
     $jobID =~ s/<\/b>.*$//i;
     print STDOUT 'Job ID = '.$jobID."\n";
     $request = $query.'jobname='.$jobID;    # utility to track job progress
### Track and print the progress until the results page is received:
     do {
        $response = $ua->get($request);
        if (! $response->is_success) {
           printf STDOUT "\n".'*** getTRDS: Error reading response from the server: %s'."\n",$response->status_line;
           exit 1;
        }
        $buffer = $response->content;
        $buffer =~ s/[\r\n]//g;			# remove CR/LF
	if ($buffer =~ /Points done =/i) {
	   $progress = $buffer;
	   $progress =~ s/^.*Points done/Points done/i;
	   $progress =~ s/<br>.*$//i;
	   print STDOUT $progress."\n";
	}
	if ($buffer !~ /Download ZIPped results:/i) {sleep(5);}
     } while ($buffer !~ /Download ZIPped results:/i);
  }
  else {
     die 'Unexpected completion, no job ID found';
  }

  $error_text = "/images/stop1.gif";
  $status     = 0;
  $data_found = 0;

### Analyze server response and download data:
  if ($buffer =~ /${error_text}/i) {
### Erroneous completion:
     print STDOUT 'Request was unsuccessful, job ID='.$jobID."\n";
     $buffer =~ s/^.*${error_text}//i;		# remove all before error message
     $buffer =~ s/^.*<font size=\+1>//i;	# remove all before error message
     $buffer =~ s/<\/font>.*$//i;		# remove all after  error message
     $buffer =~ s/<br>/\n/ig;			# replace HTML tags
     $buffer =~ s/\&nbsp;/ /ig;			# replace HTML tags
     print STDOUT 'Saving log: '.$jobID.'.tbl'."\n";
     &getstore($unzip.'jobname='.$jobID.'&filext=tbl',$jobID.'.tbl');
     print STDOUT "\n".'ERROR message:'."\n".$buffer."\n";
     $status = 1;
  }
  else {
### Normal completion:
     print STDOUT 'Request was successful, job ID='.$jobID."\n";
     if ($buffer =~ /Display DAT file/i) {
        $status = &getcheckstore($unzip,$jobID,'dat');
	if (!$status) {$data_found++;}
     } else {
	$status = 1;			# no data
     }
### GRD files are produced for 2D maps only ($nscan>1 && $noff>1):
     if ($buffer =~ /Display GRD file/i) {
        $status = &getcheckstore($unzip,$jobID,'grd');
	if (!$status) {$data_found++;}
     }
     if ($data_found == 0) {$status = 1;}	# no data
  }

  print STDOUT 'Saving packed results: '.$jobID.'.zip'."\n";
  &getstore($url.'/x-ray/'.$jobID.'.zip',$jobID.'.zip');
  print STDOUT 'Done!'."\n";
  exit $status;

############################################################################

#sub getcheckstore ($$$);
sub  getcheckstore {
  my $unzip   = shift(@_);
  my $prefix  = shift(@_);
  my $ext     = shift(@_);
  my $file = $prefix.'.'.$ext;
  print STDOUT 'Saving data: '.$file."\n";
  my $data = get($unzip.'jobname='.$prefix.'&filext='.$ext);
  $data =~ s/\015//g;			# Perl for Windows workaround
  if ($data =~ /stop/i) {		# stop1.gif is returned when no data
     print STDOUT '!!! No data on server!'."\n";
     return 1;
  } else {
     open (DAT,'> '.$file) or die 'Cannot open '.$file;
     print DAT ${data};
     close(DAT);
     return 0;
  }
}

############################################################################
