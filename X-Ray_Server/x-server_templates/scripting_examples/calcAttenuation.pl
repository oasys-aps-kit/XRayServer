#!/usr/bin/perl -W
#--------------------------------------------------------------
# This example PERL script:
# - calls the X0h program from http://x-server.gmca.aps.anl.gov/
# - gets the attenuation coefficient mu for specified energy [and material]
# - calculates attenuation for given thickness (in micrones)
#
# The script uses the LWP PERL module to fetch the pages.
#
#     		Author: Sergey Stepanov
#
# Version-1:    2007/12/13
#--------------------------------------------------------------
  use strict;
  use LWP::Simple;	# World-Wide Web library for Perl (libwww-perl)

  my ($syntax, $narg, $energy, $thickness, $code, $url);
  my ($xway, $wave, $line, $coway, $amor, $chem, $rho);
  my ($i1, $i2, $i3, $df1df2, $modeout, $detail, $begin);
  my ($buffer, @content, $ncon, $string, $mu, $attenuation);

  $syntax =  $0 . '  energy(keV) thickness(um) material [density(g/cm3)]'."\n";
  $narg = @ARGV;
  if ($narg < 3) {die 'Syntax: '.$syntax;}
#--------------Input parameters---------------------------
### Paramters can  be passed
### as command line arguments:
  $energy    = $ARGV[0];		# energy (in keV)
  $thickness = $ARGV[1];		# filter thickness (um)

  $url = 'http://x-server.gmca.aps.anl.gov/cgi/X0h_form.exe';

###--------------Parameters of X0h CGI interface--------------
  $xway = 2;				# 1 - wavelength, 2 - energy, 3 - line type
  $wave = $energy;  			# works with xway=2 or xway=3
  $line = '';				# works with xway=3 only

### Target:
  if ($narg > 3) {			# when material density is specified
     $code  = '';
     $chem  = $ARGV[2];			# we expect that specified material is chemical formula
     $rho   = $ARGV[3];			# density (g/cm3), needed for chemical formulae only
     $coway = 2;			# -1=auto, 0=crystal, 1=other_material, 2=chemical_formula
  } else {				# when material density is NOT specified
     $code  = $ARGV[2];			# material code from X0h database
     $chem  = '';			# needed for coway=2 only
     $rho   = '';			# density (g/cm3): needed for chemical formulae only
     $coway =-1;			# -1=auto, 0=crystal, 1=other_material, 2=chemical_formula
  }
  $amor  = '';    			# needed for coway=1 only

### Miller indices:
  $i1 = 0;
  $i2 = 0;
  $i3 = 0;

### Database Options for dispersion corrections df1, df2:
### -1 - Automatically choose DB for f',f"
###  0 - Use X0h data (5-25 keV or 0.5-2.5 A) -- recommended for Bragg diffraction.
###  2 - Use Henke data (0.01-30 keV or 0.4-1200 A) -- recommended for soft x-rays.
###  4 - Use Brennan-Cowan data (0.03-700 keV or 0.02-400 A)
### 10 - Compare results for all of the above sources.
  $df1df2 = -1;

### Output options:
  $modeout = 1;				# 0 - html out, 1 - quasy-text out with keywords
  $detail  = 0;				# 0 - don't print coords, 1 = print coords
###-----------------------------------------------------------

  $url .= '?xway='.$xway
         .'&wave='.$wave
         .'&line='.$line
         .'&coway='.$coway
         .'&code='.$code
         .'&amor='.$amor
         .'&chem='.$chem
         .'&rho='.$rho
         .'&i1='.$i1
         .'&i2='.$i2
         .'&i3='.$i3
         .'&df1df2='.$df1df2
         .'&modeout='.$modeout
         .'&detail='.$detail;

### Request X0h data from the server:
  $buffer = get($url);
  @content = split /\n/, $buffer;			# split page into lines
  $ncon = @content; 					# number of lines on page

  if ($buffer =~ /E R R O R/ || $buffer =~ /not found in these databases/) {
     print STDOUT 'X-Server returned error:'."\n";
     $begin = 0;
     foreach $string (@content) {			# loop over page lines
        chop $string;					# strip LF/CR
        if ($string =~ /E R R O R/ || $string =~ /Atom\.X0h/) {$begin = 1; next;}
	if ($begin) {
	   $string =~ s/\&nbsp\;//ig;
	   $string =~ s/\<br\>//ig;
	   if ($string =~ /\<\/font\>/i || $string =~ /\<\/td\>/i) {exit;}
	   print STDOUT $string,"\n";
	}
     }
  }
  foreach $string (@content) {				# loop over page lines
     chop $string;					# strip LF/CR
     if ($string =~ /^ *Absorption factor.*mu0=/i) {	# if line contains "mu0="
        $string =~ s/^.*mu0=//ig;			# erase everything before the data
        $string =~ s/\s+/ /g;				# compress spaces
        $string =~ s/^ //;				# remove spaces at the beginning
        $mu = $string;
        last;
     }
  }
  if (!defined $mu) {die 'Failed to find "Absorption factor" in X-Server response.';}
  print STDOUT 'X-ray energy E='.$energy.'KeV, material='.$code.', absorption factor mu='.$mu.'(1/cm)'."\n";
  $attenuation = exp(0.0001*$mu*$thickness);
  print STDOUT 'X-ray attenuation on material thickess='.$thickness.'um is: '.$attenuation."\n";
  exit;
