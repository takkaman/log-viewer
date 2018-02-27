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

def do_work(lines, ln, prefix):
  vat = vac = vrj = vrt = -1
  eat = eac = erj = ert = -1
  rat = rac = rrj = rrt = -1

  for i in range(ln, min(ln + 500, len(lines))):
    line = lines[i]
    if not line.startswith('ROPTSTATS'):
      continue

    match = re.search('ROPTSTATS:\s+valid\s+attempt=(\d+)\s+pass=(\d+)\s+fail=(\d+)\s+cpu=(\S+)\s+LRX', line)
    if match:
      vat = match.group(1)
      vac = match.group(2)
      vrj = match.group(3)
      vrt = match.group(4)

    match = re.search('ROPTSTATS:\s+estimate\s+attempt=(\d+)\s+pass=(\d+)\s+fail=(\d+)\s+cpu=(\S+)\s+LRX', line)
    if match:
      eat = match.group(1)
      eac = match.group(2)
      erj = match.group(3)
      ert = match.group(4)

    match = re.search('ROPTSTATS:\s+run\s+attempt=(\d+)\s+pass=(\d+)\s+fail=(\d+)\s+cpu=(\S+)\s+LRX', line)
    if match:
      rat = match.group(1)
      rac = match.group(2)
      rrj = match.group(3)
      rrt = match.group(4)
      break

  print prefix + 'v', vat, vac, vrj, vrt
  print prefix + 'e', eat, eac, erj, ert
  print prefix + 'r', rat, rac, rrj, rrt
  return


###############################################################################
# Process log file
###############################################################################
def process(log):

  # Match patterns here
  lines = log.split('\n')

  ln = log_util.get_next_ln_starts_with(lines, 0, '    WNS Optimization Summary')
  do_work(lines, ln, 'w')

  ln = log_util.get_next_ln_starts_with(lines, ln, '    TNS Optimization Summary')
  do_work(lines, ln, 't')

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

