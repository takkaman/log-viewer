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

  print 'runtime',

  ln_start = 0
  while True:

    ln1 = log_util.get_next_ln_starts_with(lines, ln_start, 'START_CMD: place_opt')
    if ln1 == ln_start:
      break
    t1 = log_util.get_elapse_time(lines, ln1, forward=True)

    ln2 = log_util.get_next_ln_starts_with(lines, ln1, 'END_CMD: place_opt')
    if ln2 == ln1:
      break
    t2 = log_util.get_elapse_time(lines, ln2, forward=True)

    print t1, t2,
    ln_start = ln2

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

