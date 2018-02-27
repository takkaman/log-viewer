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

  ln_fo = log_util.get_next_ln_starts_with(lines, 0, 'Running final optimization step.')
  ln_lgl1 = log_util.get_next_ln_starts_with(lines, ln_fo, 'START_FUNC: legalize_placement')

  t1 = log_util.get_elapse_time(lines, ln_fo, forward=True)
  t2 = log_util.get_elapse_time(lines, ln_lgl1, forward=False)

  print t2 - t1

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

