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

def do_work(lines, ln, record):

  for i in range(ln, ln+3):
    line = lines[i]
    if not line.startswith('ROPTSTATS'):
      continue

    at = ac = rj = rt = -1
    match = re.search('ROPTSTATS:\s+(\S+)\s+attempt=(\d+)\s+pass=(\d+)\s+fail=(\d+)\s+cpu=(\S+)\s+(\S+)', line)
    if match:
      t = match.group(1)
      at = match.group(2)
      ac = match.group(3)
      rj = match.group(4)
      rt = match.group(5)
      x = match.group(6)

      if x not in record:
        record[x] = {}
      record[x][t] = (at, ac, rj, rt)


  return


###############################################################################
# Process log file
###############################################################################
def process(log):

  # Match patterns here
  lines = log.split('\n')

  ln = 0
  for i in range(len(lines) - 1, 0, -1):
    if lines[i] == 'Co-efficient Ratio Summary:':
      ln = i
      break

  record = {}
  if ln != 0:
    for i in range(ln-4, ln-100, -1):
      if lines[i].startswith('---'):
        break
      if not lines[i].startswith('ROPTSTATS:  valid'):
        continue
      do_work(lines, i, record)

  xlist = ['ABUF', 'buf_rem', 'single_size', 'filter_size', 'inv_rem', 'LRX', 'ld_size']

  for x in xlist:
    if x in record.keys():
      vat, vac, vrj, vrt = record[x]['valid']
      eat, eac, erj, ert = record[x]['estimate']
      rat, rac, rrj, rrt = record[x]['run']
      print x, vat, vac, vrj, vrt, eat, eac, erj, ert, rat, rac, rrj, rrt
    else:
      print x

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

