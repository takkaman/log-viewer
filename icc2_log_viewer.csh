#!/bin/csh -f
# File:   icc2_log_viewer.csh
# Author: Deyuan Guo <dguo@synopsys.com>
# Brief:  A wrapper to run icc2_log_viewer.py
#         - Add <python>/lib to LD_LIBRARY_PATH
#         - Run <python>/bin/python icc2_log_viewer.py <args>
# File dependency:
#   icc2_log_viewer.py  - A self-contained Python-2.7 script.
#                         You could run 'python icc2_log_viewer.py <args>'
#                         with any available python-2.7 directly
# File history:
#   09/28/2017 - Created
#   10/01/2017 - Allow to run from different locations or from symlink
#   12/08/2017 - Support -regex option


# Configure the python-2.7 install directory
set python_install_dir='/depot/python-2.7.9_32'

# Temporarily add python/lib to LD_LIBRARY_PATH
if ! $?LD_LIBRARY_PATH then
  setenv LD_LIBRARY_PATH ""
endif
set ORIG_LD_LIBRARY_PATH="$LD_LIBRARY_PATH"
setenv LD_LIBRARY_PATH "$LD_LIBRARY_PATH\:$python_install_dir/lib"

# Make sure icc2_log_viewer.csh and icc2_log_viewer.py are in the same directory
set this_script_loc=`readlink -f -- $0`
set this_script_dir=`dirname $this_script_loc`
if ( -e $python_install_dir/bin/python ) then
  if ( -e $this_script_dir/icc2_log_viewer.py ) then
    $python_install_dir/bin/python $this_script_dir/icc2_log_viewer.py "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "$10" "$11" "$12" "$13" "$14" "$15"
  else
    echo "Cannot find $this_script_dir/icc2_log_viewer.py"
  endif
else
  echo "Cannot find $python_install_dir/bin/python"
endif

# Restore original LD_LIBRARY_PATH
setenv LD_LIBRARY_PATH "$ORIG_LD_LIBRARY_PATH"

