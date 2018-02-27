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

  # only for -debug
  t1 = 0
  t2 = 0
  t3 = 0
  ln = log_util.get_next_ln_starts_with(lines, 0, '   POWER   ')
  hb = lines[ln]
  for i in range(ln, 0, -1):
    if lines[i].startswith('END_FUNC: propagate_switching_activity'):
      match = re.search('ELAPSE:\s+(\d+) s', lines[i])
      if match:
        t2 = int(match.group(1))
    elif lines[i].startswith('START_FUNC: propagate_switching_activity'):
      match = re.search('ELAPSE:\s+(\d+) s', lines[i])
      if match:
        t1 = int(match.group(1))
        break

  qor = log_util.parse_heartbeat(hb)
  if qor['valid']:
    hh, mm, ss = qor['elapsed'].split(':')
    t3 = int(hh) * 3600 + int(mm) * 60 + int(ss)

    print "runtime", t1, t2, t3
  else:
    print "runtime"

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

