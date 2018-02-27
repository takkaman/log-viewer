#!/bin/csh -f
# Author: Deyuan Guo
# Date: Oct 11, 2017

if ($#argv < 2) then
  echo "Usage: log_traverser <flow_dir> <command args>"
  echo "       For each nwcopt log in flow_dir/*/*, run: command args log"
  echo "       Example: log_traverser Nwtn_QOR_CCD echo"
  exit
endif

set loglist=`find -L $1 -maxdepth 2 -regex ".*nwcopt.out\|.*nwcopt.out.gz" -type f | sort -n`
foreach log ($loglist)
  set f=`basename $log`
  echo "==================================================================================================== $f"
  $argv[2-] $log
end

