#!/bin/csh -f
# File:   icc2_log_comparator.csh
# Author: Deyuan Guo <dguo@synopsys.com>
# Brief:  A wrapper to run icc2_log_comparator.py
#         - Add <python>/lib to LD_LIBRARY_PATH
#         - Run <python>/bin/python icc2_log_comparator.py <args>
# File dependency:
#   icc2_log_comparator.py  - A Python-2.7 script
#   icc2_log_viewer.py      - Used by icc2_log_comparator
# File history:
#   10/16/2017 - Created


# Configure the python-2.7 install directory
set python_install_dir='/depot/python-2.7.9_32'

# Temporarily add python/lib to LD_LIBRARY_PATH
if ! $?LD_LIBRARY_PATH then
  setenv LD_LIBRARY_PATH ""
endif
set ORIG_LD_LIBRARY_PATH="$LD_LIBRARY_PATH"
setenv LD_LIBRARY_PATH "$LD_LIBRARY_PATH\:$python_install_dir/lib"

# Make sure icc2_log_comparator.csh and icc2_log_comparator.py are in the same directory
set this_script_loc=`readlink -f -- $0`
set this_script_dir=`dirname $this_script_loc`
if ( -e $python_install_dir/bin/python ) then
  if ( -e $this_script_dir/icc2_log_comparator.py ) then
    $python_install_dir/bin/python $this_script_dir/icc2_log_comparator.py $argv
  else
    echo "Cannot find $this_script_dir/icc2_log_comparator.py"
  endif
else
  echo "Cannot find $python_install_dir/bin/python"
endif

# Restore original LD_LIBRARY_PATH
setenv LD_LIBRARY_PATH "$ORIG_LD_LIBRARY_PATH"

