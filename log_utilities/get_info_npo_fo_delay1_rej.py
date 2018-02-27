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

  cnt_at = cnt_xac = cnt_xrj = cnt_drj = cnt_mat = cnt_mrj = -1
  ln_sbo = log_util.get_next_ln_starts_with(lines, 0, '    SBO Optimization Summary')
  for i in range(ln_sbo + 3, ln_sbo + 18):
    line = lines[i]
    if 'Drivers Attempted' in line:
      cnt_at = line.split('=')[1].strip()
    elif 'Xform Acceptance Count' in line:
      cnt_xac = line.split('=')[1].strip()
    elif 'Xform Rejection Count' in line:
      cnt_xrj = line.split('=')[1].strip()
    elif 'Density Check Rejection Count' in line:
      cnt_drj = line.split('=')[1].strip()
    elif 'Main Graph Trial Count' in line:
      cnt_mat = line.split('=')[1].strip()
    elif 'Main Graph Rejection Count' in line:
      cnt_mrj = line.split('=')[1].strip()

  print "sum-sbo", cnt_at, cnt_xac, cnt_xrj, cnt_drj, cnt_mat, cnt_mrj


  cnt_at = cnt_xac = cnt_xrj = cnt_drj = cnt_mat = cnt_mrj = -1
  ln_pbo_w = log_util.get_next_ln_starts_with(lines, ln_sbo, '    WNS Optimization Summary')
  for i in range(ln_pbo_w + 3, ln_pbo_w + 18):
    line = lines[i]
    if 'Drivers Attempted' in line:
      cnt_at = line.split('=')[1].strip()
    elif 'Xform Acceptance Count' in line:
      cnt_xac = line.split('=')[1].strip()
    elif 'Xform Rejection Count' in line:
      cnt_xrj = line.split('=')[1].strip()
    elif 'Density Check Rejection Count' in line:
      cnt_drj = line.split('=')[1].strip()
    elif 'Main Graph Trial Count' in line:
      cnt_mat = line.split('=')[1].strip()
    elif 'Main Graph Rejection Count' in line:
      cnt_mrj = line.split('=')[1].strip()

  print "sum-pbo-w", cnt_at, cnt_xac, cnt_xrj, cnt_drj, cnt_mat, cnt_mrj

  cnt_at = cnt_xac = cnt_xrj = cnt_drj = cnt_mat = cnt_mrj = -1
  ln_pbo_t = log_util.get_next_ln_starts_with(lines, ln_pbo_w, '    TNS Optimization Summary')
  for i in range(ln_pbo_t + 3, ln_pbo_t + 18):
    line = lines[i]
    if 'Drivers Attempted' in line:
      cnt_at = line.split('=')[1].strip()
    elif 'Xform Acceptance Count' in line:
      cnt_xac = line.split('=')[1].strip()
    elif 'Xform Rejection Count' in line:
      cnt_xrj = line.split('=')[1].strip()
    elif 'Density Check Rejection Count' in line:
      cnt_drj = line.split('=')[1].strip()
    elif 'Main Graph Trial Count' in line:
      cnt_mat = line.split('=')[1].strip()
    elif 'Main Graph Rejection Count' in line:
      cnt_mrj = line.split('=')[1].strip()

  print "sum-pbo-t", cnt_at, cnt_xac, cnt_xrj, cnt_drj, cnt_mat, cnt_mrj

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

