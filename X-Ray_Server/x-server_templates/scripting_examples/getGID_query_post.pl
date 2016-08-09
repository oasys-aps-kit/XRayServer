#!/usr/bin/perl -W
#--------------------------------------------------------------
# This example PERL script:
# - calls the GID_SL program from http://x-server.gmca.aps.anl.gov/
# - tracks calculation.
# - gets and saves the data.
# - the example is equivalent to the following page:
# http://x-server.gmca.aps.anl.gov/cgi/WWW_form.exe?template=GID_sl_multilay.htm&method=post
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
# Version-1.0:  2012/04/12
#--------------------------------------------------------------
  use strict;
  use LWP::Simple;			# World-Wide Web library for Perl (libwww-perl)
  use LWP::UserAgent;

  select STDOUT; $|=1;			# set unbuffered output

  my ($url, $prg, $query, $unzip, %FORM, $request);
  my ($ua, $response, $buffer, $jobID, $error_text);
  my ($start_time, $end_time, $name, $status, $progress);
  $start_time = time();

### General parameters:
  $url      = 'http://x-server.gmca.aps.anl.gov';
  $prg      = $url.'/cgi/GID_form.pl';
  $query    = $url.'/cgi/WWWwatch.exe?';
  $unzip    = $url.'/cgi/WWWunzip.exe?';

  $FORM{'comment1'} = 'Template: script getGID_query_post';
### X-rays:
  $FORM{'xway'}     = 1;		# 1=wavelength, 2=energy, 3=line type, 4=Bragg angle
  $FORM{'wave'}     = 1.540562;		# works with xway=1 or xway=2 or xway=4 where used as Bragg angle input
# $FORM{'line'}     = 'Cu-Ka1';		# works with xway=3 only
  $FORM{'line'}     = '';		# works with xway=3 only
  $FORM{'ipol'}     = 1;		# 1=sigma-polarization; 2=pi-polarization 3=mixed

### Substrate:
  $FORM{'code'}     = 'GaAs';		# crystal code
  $FORM{'w0'}       = 1.;		# Debye-Waller type correction for x0
  $FORM{'wh'}       = 1.;		# Debye-Waller type correction for xh
  $FORM{'daa'}      = 0.;		# substrate strain da/a
  $FORM{'sigma'}    = 0.;		# rms roughness at surface (Angstrom)

### Database Options for dispersion corrections df1, df2:
### -1 - Automatically choose DB for f',f"
###  0 - Use X0h data (5-25 keV or 0.5-2.5 A) -- recommended for Bragg diffraction.
###  2 - Use Henke data (0.01-30 keV or 0.4-1200 A) -- recommended for soft x-rays.
###  4 - Use Brennan-Cowan data (0.03-700 keV or 0.02-400 A)
  $FORM{'df1df2'}   = -1;

### Bragg reflection:
  ($FORM{'i1'},$FORM{'i2'},$FORM{'i3'}) = (4, 0, 0);

### Geometry specification:
### 1: Surface orientation & incidence angle of K0
### 2: Surface orientation & exit angle of Kh
### 3: Surface orientation & condition of coplanar grazing incidence
### 4: Surface orientation & condition of coplanar grazing exit
### 5: Surface orientation & condition of symmetric Bragg case
### 6: Condition of coplanar reflection & angle of Bragg planes to surface
### 7: Condition of coplanar reflection & incidence angle of K0
### 8: Condition of coplanar reflection & exit angle of Kh
### 9: Condition of coplanar reflection & asymmetry factor beta=g0/gh
  $FORM{'igie'}     = 5;		# minimum scan angle (range)
### Geometry parameter:
### - incidence angle for [1,7],
### - exit angle for [2,8],
### - Bragg planes angle for [6],
### - asymmetry factor beta=g0/gh for [9].
  $FORM{'fcentre'}  = '';
  $FORM{'unic'}     = 0;		#fcentre units: 0=none/degr,1=min,2=mrad,3=sec,4=urad

### Crystal surface (used with geometry modes 1-5 only):
  ($FORM{'n1'},$FORM{'n2'},$FORM{'n3'}) = (1, 0, 0);   # indices of surface base plane
  ($FORM{'m1'},$FORM{'m2'},$FORM{'m3'}) = (0, 1, 1);   # indices of miscut direction
  $FORM{'miscut'} = 0.;			# miscut angle of surface with respect to $n_hkl
  $FORM{'unim'}   = 0;			# miscut units: 0=degr,1=min,2=mrad,3=sec,4=urad

### Scan axis:
### 1: Along surface normal (N_surface)
### 2: Along [k0 x N_surface] (vector product)
### 3: Along Reciprocal lattice vector (h)
### 4: Along [k0 x h] (vector product)
### 5: Along Other axis
### 6: Takeoff spectrum (PSD)
### 7: Energy
### 8: Energy, no X0/xh recalculation
  $FORM{'axis'}   = 4;
  ($FORM{'a1'},$FORM{'a2'},$FORM{'a3'}) = (0, 0, 0);   # indices of 'other' axis, if selected
  $FORM{'invert'} = 0;			# 1=invert axis, 0=don't invert

### Scan limits:
  $FORM{'scanmin'}  = -2000.;		# minimum scan angle (range)
  $FORM{'scanmax'}  =  2000.;		# maximum scan angle (range)
  $FORM{'unis'}     = 3;		# scan angle units: 0=degr.,1=min,2=mrad,3=sec,4=urad,5=eV
  $FORM{'nscan'}    = 401;		# number of scan points
  $FORM{'column'}   = 'I';		# A='scan angle', I='incidence angle', E='exit angle'

### Approximations:
  $FORM{'alphamax'} = 1.E+8;		# maximum alpha/|xh| when crystal is still considered a 'crystal'

  $FORM{'watch'}    = 1;		# job watching option

### Surface layer profile
### (can also be read from
## a filename specified in
### the command line):
  $FORM{'profile'} = '
	period=20
	 t=100 code=GaAs sigma=2
	 t=70 code=AlAs sigma=2 da/a=a
	end period
       ';

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
     print STDOUT "\n".'*** getGID: Error reading response from the server: %s'."\n", $response->status_line;
     $end_time = time();
     printf STDOUT 'Elapsed time=%ds'."\n", int($end_time-$start_time);
#    die $response->status_line;
     exit 1;
  }

  $buffer = $response->content;
  $buffer =~ s/[\015\012]//g;			# remove CR/LF

### Find job ID on the server:
  $jobID = $buffer;
  if ($buffer =~ /Download ZIPped results:/i) {
### Job is complete:
### Remove all text before and after job name in the string like:
### Download ZIPped results: <A HREF="x-ray/GIDxxxxx.zip">GIDxxxxx.zip</A>
     $jobID =~ s/^.*Download ZIPped results: <A HREF=\"\/x-ray\///i;
     $jobID =~ s/\.zip.*$//i;
  }
  elsif ($buffer =~ /Job ID:/i) {
### Job is in progress:
### Remove all text before and after job name in the string like:
### Job ID: <b>GID70410</b>
     $jobID =~ s/^.*Job ID: <b>//i;
     $jobID =~ s/<\/b>.*$//i;
     print STDOUT 'Job ID = '.$jobID."\n";
     $request = $query.'jobname='.$jobID;    	# utility to track job progress
### Track and print the progress until the results page is received:
     do {
        $response = $ua->get($request);
        if (! $response->is_success) {
           printf STDOUT "\n".'*** getGID: Error reading response from the server: %s'."\n",$response->status_line;
           exit 1;
        }
        $buffer = $response->content;
        $buffer =~ s/[\015\012]//g;		# remove CR/LF
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
     die 'Unexpected completion, no job ID found'."\n";
  }

  $error_text = 'images/stop1.gif';
  $status = 0;

### Analyze server response and download the data:
  if ($buffer =~ /${error_text}/i) {
### Erroneous completion:
     print STDOUT '*** getGID: Request was unsuccessful, job ID='.$jobID."\n";
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
     } else {
	$status = 1;			# no data
     }
  }

  print STDOUT 'Saving packed results: '.$jobID.'.zip'."\n";
  &getstore($url.'/x-ray/'.$jobID.'.zip',$jobID.'.zip');
  $end_time = time();
  printf STDOUT 'Done! Elapsed time=%ds'."\n",int($end_time-$start_time);
  exit $status;

############################################################################

#sub getcheckstore ($$$);
sub  getcheckstore {
  my $unzip   = shift(@_);
  my $prefix  = shift(@_);
  my $ext     = shift(@_);
  my $file = $prefix.'.'.$ext;
  print STDOUT 'Saving data: '.$file."\n";
# my $agent = LWP::UserAgent->new;
# my $respn = $ua->get($unzip.'jobname='.$prefix.'&filext='.$ext);
# if (! $respn->is_success) {
#   print "\n".'*** getGID: Error reading response from the server'."\n";
#   die $respn->status_line;
# }
# my $data = $respn->content;;
  my $data = get($unzip.'jobname='.$prefix.'&filext='.$ext);
  $data =~ s/\015//g;			# Perl for Windows workaround
  if ($data =~ /stop/i) {		# stop1.gif is returned when no data
     print STDOUT '!!! No data on server!'."\n";
     return 1;
  } else {
     open (DAT,'> '.$file) or die 'Cannot open '.$file;
     print DAT $data;
     close(DAT);
     return 0;
  }
}

############################################################################
