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

  ln_fo = 0
  for i in range(len(lines)):
    if lines[i] == 'Running final optimization step.':
      ln_fo = i
      break
  ln_begin = ln_fo
  for i in range(ln_fo, len(lines)):
    if lines[i].startswith('END_FUNC: APS_S_DRC'):
      ln_begin = i
      break
  ln_end = ln_begin
  for i in range(ln_begin + 10, len(lines)):
    if lines[i].startswith('END_FUNC: psynopt_delay_opto'):
      ln_end = i
      break

  hb1 = ''
  for i in range(ln_begin, ln_fo, -1):
    match = re.search('\s+ELAPSED\s+WORST NEG\s+TOTAL NEG', lines[i])
    if match:
      hb1 = lines[i + 3]
      break

  hb2 = ''
  for i in range(ln_end, ln_begin, -1):
    match = re.search('\s+ELAPSED\s+WORST NEG\s+TOTAL NEG', lines[i])
    if match:
      hb2 = lines[i + 3]

      # print out scenarios
      scenarios = []
      for j in range(i - 2, max(0, i - 100), -1):
        if lines[j].strip().startswith('Scenario'):
          scenarios.append(lines[j])
        else:
          break
      for l in reversed(scenarios):
        print l

      break

  ok = True

  qor1 = log_util.parse_heartbeat(hb1)
  qor2 = log_util.parse_heartbeat(hb2)

  if qor1['valid'] and qor2['valid']:

    hh, mm, ss = qor1['elapsed'].split(':')
    t1 = int(hh) * 3600 + int(mm) * 60 + int(ss)
    hh, mm, ss = qor2['elapsed'].split(':')
    t2 = int(hh) * 3600 + int(mm) * 60 + int(ss)

    print "runtime", t1, t2
    print "wns", qor1['wns'], qor2['wns']
    print "tns", qor1['tns'], qor2['tns']
    print "maxtran", qor1['maxtran'], qor2['maxtran']
    print "area", qor1['area'], qor2['area']
    print "buf", qor1['bufcnt'], qor2['bufcnt']
    print "inv", qor1['invcnt'], qor2['invcnt']
  else:
    print "runtime"
    print "wns"
    print "tns"
    print "maxtran"
    print "area"
    print "buf"
    print "inv"

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

