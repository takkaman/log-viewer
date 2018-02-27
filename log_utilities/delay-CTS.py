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

  ln_init = log_util.get_next_ln_starts_with(lines, 0, '    *   * ')

  ln_delay = log_util.get_next_ln_starts_with(lines, ln_init, 'INFO: check if proc nro_prelude_delay-CTS exists')
  t_delay = log_util.get_elapse_time(lines, ln_delay, forward=False)

  ln_prev_hb = log_util.get_next_ln_starts_with(lines, ln_delay, '    *   * ', forward=False)
  if ln_prev_hb == None:
    hb1 = ""
  else:
    hb1 = lines[ln_prev_hb]

  print "SCN BEFORE:"
  print_scn_table(lines, ln_prev_hb)

  ln_sbo = log_util.get_next_ln_starts_with(lines, ln_delay, '    SBO Optimization Summary')
  t_sbo = log_util.get_elapse_time(lines, ln_sbo, forward=True)

  ln_pbo_w1 = log_util.get_next_ln_starts_with(lines, ln_sbo, 'PBO-WNS: Iteration 2')
  t_pbo_wns_1 = log_util.get_elapse_time(lines, ln_pbo_w1, forward=True)

  ln_pbo_w2 = log_util.get_next_ln_starts_with(lines, ln_pbo_w1, '    WNS Optimization Summary')
  t_pbo_wns_2 = log_util.get_elapse_time(lines, ln_pbo_w2, forward=True)

  ln_pbo_t1 = log_util.get_next_ln_starts_with(lines, ln_pbo_w2, 'PBO-TNS: Iteration 2')
  t_pbo_tns_1 = log_util.get_elapse_time(lines, ln_pbo_t1, forward=True)

  ln_end = log_util.get_next_ln_starts_with(lines, ln_pbo_t1, '    *   * ')
  t_end = log_util.get_elapse_time(lines, ln_end, forward=False)
  if ln_end == None:
    hb2 = ""
  else:
    hb2 = lines[ln_end]

  print "SCN AFTER:"
  print_scn_table(lines, ln_end)

  qor1 = log_util.parse_heartbeat(hb1)
  qor2 = log_util.parse_heartbeat(hb2)
  if qor1['valid'] and qor2['valid']:
    print 'runtime', t_delay, t_sbo, t_pbo_wns_1, t_pbo_wns_2, t_pbo_tns_1, t_end
    print "wns", qor1['wns'], qor2['wns']
    print "tns", qor1['tns'], qor2['tns']
    print "maxtran", qor1['maxtran'], qor2['maxtran']
    print "area", qor1['area'], qor2['area']
    print "buf", qor1['bufcnt'], qor2['bufcnt']
    print "inv", qor1['invcnt'], qor2['invcnt']
  else:
    print 'runtime'
    print "wns"
    print "tns"
    print "maxtran"
    print "area"
    print "buf"
    print "inv"

  return


# Pring scenario table. ln needs to be the line number of NPO QoR heartbeat
def print_scn_table(lines, ln):
  if ln == None:
    return
  scenarios = []
  for m in range(ln - 3, max(0, ln - 100), -1):
    match = re.search('^\s+\d+\s+\*\s+', lines[m])
    if match:
      scenarios.append(lines[m])
    if lines[m].startswith('Scene'):
      break
  for l in reversed(scenarios):
    print l


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

