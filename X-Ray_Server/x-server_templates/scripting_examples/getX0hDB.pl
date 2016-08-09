#!/usr/bin/perl -W
#---------------------------------------------------------------------------
# This script is an analog of http://x-server.gmca.aps.anl.gov/x0h_list.html
# It can request the X0h server DB listings under various conditions.
#---------------------------------------------------------------------------
  use strict;
  use LWP::Simple;
  select STDOUT; $|=1;			# set unbuffered output

  my ($url, %FORM, $request, $key, $buffer);

  $url = 'http://x-server.gmca.aps.anl.gov/cgi/WWW_dbli.exe';
### Uncomment one:
# $FORM{'x0hdb'} = 'all%2Batoms';       # all structures + records from atom.x0h
# $FORM{'x0hdb'} = 'amorphous%2Batoms'; # all non-crystals + those from atom.x0h
# $FORM{'x0hdb'} = 'all';               # all structures from coord.x0h
# $FORM{'x0hdb'} = 'crystals';          # all crystals from coord.x0h
  $FORM{'x0hdb'} = 'cubic-crystals';    # all cubic crystals from coord.x0h
# $FORM{'x0hdb'} = 'amorphous';         # non-crystals from coord.x0h
# $FORM{'x0hdb'} = 'atoms';             # non-crystals from atom.x0h
# $FORM{'x0hdb'} = 'waves';             # characteristic X-ray lines

  $FORM{'textout'}   = 1;		# set 0 or comment out for HTML output
  $FORM{'namesonly'} = 1;		# set 0 or comment out for DB dump

  $request = '';
  foreach $key (keys %FORM) {$request .= '&'.$key.'='.$FORM{$key};}
  $request =~ s/^\&/\?/;
  $buffer = get($url.$request);
  $buffer =~ s/\r\n/\n/g;
  print $buffer;
