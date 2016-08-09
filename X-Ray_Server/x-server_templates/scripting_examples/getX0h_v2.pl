#!/usr/bin/perl -W
#--------------------------------------------------------------
# This example PERL script:
# - calls the X0h program from http://x-server.gmca.aps.anl.gov/
# - gets the scattering factors chi_0r and chi_0i
# - saves them into a file as a function of energy
#
# The script can use either the LWP PERL module or wget (external program).
# In the later case it can run on Microsoft Windows under Cygwin
# (http://www.cygwin.com).
#
#     		Author: Sergey Stepanov
#
# Version-1.0:  2005/12/31
# Version-1.1:  2006/11/08
# Version-2.0:  2012/06/28
#--------------------------------------------------------------
  use strict;
  use LWP::Simple;		# World-Wide Web library for Perl (libwww-perl)

  select STDOUT; $|=1;		# set unbuffered output

  my ($url, %FORM, $request, $file, @E, $nE, $dE);
  my ($key, $buffer, @content, $i, $string);
#--------------Input parameters---------------------------
### Output file:
  $file = 'X0h_example.dat';

### Energy range and the number of energy points
  @E  = (10, 12); 		# start & end energy
  $nE = 3;			# number of energy points
### The paramters can also be passed
### as command line arguments:
# @E  = ($ARGV[0], $ARGV[1]);	# start & end energy
# $nE = $ARGV[2];		# number of energy ppints

### Energy step:
  if ($nE > 1) {$dE = ($E[1]-$E[0])/($nE-1);} else {$dE = 0;}

  $url = 'http://x-server.gmca.aps.anl.gov/cgi/X0h_form.exe';
###--------------Parameters of X0h CGI interface--------------
  $FORM{'xway'} = 3;		# 1=wavelength, 2=energy, 3=characteristic line
# $FORM{'wave'} = 0;   		# works with xway=2 or xway=3 (see below)
  $FORM{'line'} = 'Cu-Ka1';	# works with xway=3 only
#  $FORM{'line'} = '';		# works with xway=3 only

### Target:
  $FORM{'coway'} = 0;		# 0=crystal, 1=other material, 2=chemicalformula
  $FORM{'code'} = 'Silicon';	# specify crystal (works with coway=0 only)
  $FORM{'amor'} = '';		# specify other material (coway=1 only)
  $FORM{'chem'} = '';		# specify chemical formula (coway=2 only)
  $FORM{'rho'}  = '';		# specify density in g/cm3 (coway=2 only)

### Bragg reflection:
  ($FORM{'i1'},$FORM{'i2'},$FORM{'i3'}) = (1, 1, 1);

### Database Options for dispersion corrections df1, df2:
### -1 - Automatically choose DB for f',f"
###  0 - Use X0h data (5-25 keV or 0.5-2.5 A) -- recommended for Bragg diffraction.
###  2 - Use Henke data (0.01-30 keV or 0.4-1200 A) -- recommended for soft x-rays.
###  4 - Use Brennan-Cowan data (0.03-700 keV or 0.02-400 A)
### 10 - Compare results for all of the above sources.
  $FORM{'df1df2'} = 0;

### Output options:
  $FORM{'modeout'} = 1;		# 0=html, 1=quasytext
  $FORM{'detail'}  = 1;		# 0=no coords, 1=print coords
###-----------------------------------------------------------

### Open output file for writing:
  open (DAT,' > ',$file) || die 'Cannot open '.$file."\n";	# overwrite DAT file
  select DAT; $|=1;						# set unbuffered output

### Print data header:
  print DAT '#Energy,      xr0,        xi0'."\n";

  for ($i=0; $i<$nE; $i++) { 			# Energy loop
     $FORM{'wave'} = $E[0] + $dE * $i;
     $request = '';
     foreach $key (keys %FORM) {$request .= '&'.$key.'='.$FORM{$key};}
     $request =~ s/^\&/\?/;			# replace 1st "&" by "?"

     $buffer = get($url.$request);		# request X0h data from server:
     @content = split /\r\n?/, $buffer;		# split response into lines

     print DAT '   '.$FORM{'wave'};
     foreach $string (@content) {		# loop over page lines
        if ($string =~ m/xr0=/) {		# if the line contains "xr0="
      	   $string =~ s/^.*xr0=//g;		# erase everything before the data
           print DAT ',  '.$string;
        }
        elsif ($string =~ m/xi0=/) {		# if the line contains "xi0="
      	   $string =~ s/^.*xi0=//g;		# erase everything before the data
           print DAT ',  '.$string;
        }
     }
     print DAT "\n";
  }
