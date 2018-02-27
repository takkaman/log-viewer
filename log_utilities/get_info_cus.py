#!/remote/us01home46/dguo/bin/python
# -*- coding: utf-8 -*-
"""
Template for extracting information from an ICC2 log file
Created on Oct 11, 2017
@author: Deyuan Guo <dguo@synopsys.com>
"""

import sys
import re
import icc2_log_utilities as log_util

###############################################################################
# Process log file
###############################################################################
def process(log):

  # Match patterns here
  lines = log.split('\n')

  ln = log_util.get_next_ln_starts_with(lines, 0, 'Final optimized QoR')

  wns = "--"
  tns = "--"
  whs = "--"
  ths = "--"
  match = re.search("\s+WNS\(setup\)=(\S+)\s+TNS\(setup\)=(\S+)\s.*", lines[ln + 1])
  if match:
    wns = match.group(1)
    tns = match.group(2)
  match = re.search("\s+WNS\(hold\)=(\S+)\s+TNS\(hold\)=(\S+)\s.*", lines[ln + 2])
  if match:
    whs = match.group(1)
    ths = match.group(2)

  print "wns", wns
  print "tns", tns
  print "whs", whs
  print "ths", ths

  return


###############################################################################
# Command line entry. Deyuan Guo. Oct 11, 2017
###############################################################################
if __name__ ==  '__main__':
  sys.tracebacklimit = 1

  if len(sys.argv) != 2:
    print 'Usage: script <log>'
    exit(0)

  log = log_util.load_log_file(sys.argv[1])

  process(log)

