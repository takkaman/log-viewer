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

  hb1 = ''
  hb2 = ''
  t1 = 0
  t2 = 0
  cnt = 0
  for j in range(ln_fo, len(lines)):
    line = lines[j]
    if line.startswith('    *   * '):
      cnt += 1
      if cnt == 1:
        hb1 = line
      elif cnt == 2:
        hb2 = line

        # print scenarios
        scenarios = []
        for m in range(j - 3, max(0, j - 100), -1):
          match = re.search('^\s+\d+\s+\*\s+', lines[m])
          if match:
            scenarios.append(lines[m])
          if lines[m].startswith('Scene'):
            break
        for l in reversed(scenarios):
          print l

      for k in range(j, ln_fo, -1):
        if lines[k].startswith('START_FUNC'):
          match = re.search('ELAPSE:\s+(\d+) s', lines[k])
          if match:
            if cnt == 1:
              t1 = int(match.group(1))
            elif cnt == 2:
              t2 = int(match.group(1))
            break
    if cnt >= 2:
      break

  ok = True

  match = re.search('    \*   \*\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\s+\S+\s+\S+\s+(\S+)\s+\S+\s+(\S+)\s+(\S+)', hb1)
  if match:
    wns1 = match.group(1)
    tns1 = match.group(2)
    maxtran1 = match.group(3)
    area1 = match.group(4)
    buf1 = match.group(5)
    inv1 = match.group(6)
  else:
    ok = False

  match = re.search('    \*   \*\s+(\S+)\s+(\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(\S+)\s+\S+\s+\S+\s+(\S+)\s+\S+\s+(\S+)\s+(\S+)', hb2)
  if match:
    wns2 = match.group(1)
    tns2 = match.group(2)
    maxtran2 = match.group(3)
    area2 = match.group(4)
    buf2 = match.group(5)
    inv2 = match.group(6)
  else:
    ok = False

  if ok:
    print "runtime", t1, t2
    print "wns", wns1, wns2
    print "tns", tns1, tns2
    print "maxtran", maxtran1, maxtran2
    print "area", area1, area2
    print "buf", buf1, buf2
    print "inv", inv1, inv2


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

