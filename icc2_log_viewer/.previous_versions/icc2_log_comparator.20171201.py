#!/remote/us01home46/dguo/bin/python
# -*- coding: utf-8 -*-
"""
File: icc2_log_comparator.py
Brief:
  A script to help to compare two ICC2 log files
  Usage: python-2.7 icc2_log_comparator.py <args>

Author:  Deyuan Guo <dguo@synopsys.com>
Manager: Jeng-Liang Tsai <jengt@synopsys.com>
Team:    ICC2 Optimization Team @ Synopsys, Inc.

SYNOPSYS CONFIDENTIAL - This is an unpublished, proprietary work of
Synopsys, Inc., and is fully protected under copyright and trade
secret laws. You may not view, use, disclose, copy, or distribute this
file or any information contained herein except pursuant to a valid
written license from Synopsys.

File history:
  10/01/2017 Created
  10/16/2017 Release for testing
  10/17/2017 Support combinations of two categories
  10/18/2017 Show compact information during comparison
  12/01/2017 Support DFT category
"""

import sys
import os
import gzip
import re
import argparse
import icc2_log_viewer as V

Version = '20171201'


##############################################################################

# Author: Deyuan Guo
# ICC2 Log Comparator
class ICC2LogComparator:

  # Constructor
  def __init__(self):
    self.parser = self.create_argparse()
    self.log1 = None
    self.log2 = None
    self.area = False
    self.buf = False
    self.drc = False
    self.hold = False
    self.power = False
    self.runtime = False
    self.setup = False
    self.colored = True
    self.msg_width = 80                     # width of log message
    self.log_width = self.msg_width + 25    # width of log (ln + tag + message)
    return


  # Run
  def run(self):
    if len(sys.argv) <= 2:
      print '------------------------------------'
      print ' ICC2 Log Comparator (ver.' + Version + ') '
      print ' Deyuan Guo <dguo@synopsys.com> '
      print '------------------------------------'
      print
      self.parser.print_help()
      print
      print 'Due to window width, this script can support at most two QoR categories simultaneously'
      return

    print 'Info: ICC2 Log Comparator (ver.' + Version + ')'
    ok = self.parse_args()
    if not ok:
      return

    #print 'Info: Parsing log file 1 ...'
    v1 = V.ICC2LogViewer()
    v1.log = self.log1
    v1.cmd = True
    v1.cts = True
    v1.flow = True
    v1.gr = True
    v1.lgl = True
    v1.dft = True
    v1.qor = True
    v1.load_file()
    v1.parse_log_file()

    #print 'Info: Parsing log file 2 ...'
    v2 = V.ICC2LogViewer()
    v2.log = self.log2
    v2.cmd = True
    v2.cts = True
    v2.flow = True
    v2.gr = True
    v2.lgl = True
    v2.dft = True
    v2.qor = True
    v2.load_file()
    v2.parse_log_file()

    self.show(v1, v2)
    return


  # Create argparse object
  def create_argparse(self):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('log1',         help='ICC2 log file 1', type=file)
    parser.add_argument('log2',         help='ICC2 log file 2', type=file)

    #group = parser.add_mutually_exclusive_group()
    parser.add_argument('-s', '-setup',     help='compare (S)etup timing (default)', action='store_true')
    parser.add_argument('-h', '-hold',      help='compare (H)old timing', action='store_true')
    parser.add_argument('-a', '-area',      help='compare (A)rea and inst count', action='store_true')
    parser.add_argument('-d', '-drc',       help='compare (D)RC (default)', action='store_true')
    parser.add_argument('-b', '-buf',       help='compare (B)uffer and inverter count', action='store_true')
    parser.add_argument('-p', '-power',     help='compare (P)ower: leakage and lvth', action='store_true')
    parser.add_argument('-r', '-runtime',   help='compare (R)untime and peak memory', action='store_true')

    parser.add_argument('--help',       help='show this help message and exit', action='help')
    parser.add_argument('--no-color',   help='turn off color decorations for output redirection', action='store_true')
    return parser


  # Parse command line auguments
  def parse_args(self):
    args = self.parser.parse_args()
    self.log1 = args.log1
    self.log2 = args.log2
    self.setup = args.s
    self.hold = args.h
    self.area = args.a
    self.drc = args.d
    self.buf = args.b
    self.power = args.p
    self.runtime = args.r
    self.colored = not args.no_color

    count = 0
    if self.area:    count += 1
    if self.buf:     count += 1
    if self.drc:     count += 1
    if self.hold:    count += 1
    if self.power:   count += 1
    if self.runtime: count += 1
    if self.setup:   count += 1
    if count == 0:
      self.setup = True
      self.drc = True
    elif count > 2:
      print "Abort: Cannot support more than two QoR categories yet."
      return False



    if not (self.area or self.buf or self.drc or self.hold or self.power or self.runtime or self.setup):
      self.setup = True

    return True


  # Get separator of left and right
  def get_sep(self):
    if self.colored:
      sep = ' ' + V.ANSI.BGYELLOW + ' ' + V.ANSI.ENDC
    else:
      sep = ' |'
    return sep


  # Print header with ANSI color
  def cprint_header(self):
    header = '%9s   %-10s  ' % ('Line', 'Tag')

    if self.setup:
      header += ' %10s %10s %10s' % ('WNS', 'TNS', 'NSV')
    if self.hold:
      header += ' %10s %10s %10s' % ('WHS', 'THS', 'NHV')
    if self.area:
      header += ' %12s %10s' % ('AREA', 'InstCnt')
    if self.drc:
      header += ' %10s %7s %10s %7s' % ('MaxTran', 'MTranV', 'MaxCap', 'MCapV')
    if self.buf:
      header += ' %10s %10s' % ('BufCnt', 'InvCnt')
    if self.power:
      header += ' %11s %8s %7s' % ('Leakage', 'NumLvth', '%Lvth')
    if self.runtime:
      header += ' %9s %7s %7s' % ('Elapsed', 'DltElps', 'PeakMem')

    header = header.ljust(self.log_width)[:self.log_width]
    if self.colored:
      header = V.ANSI.REVERSED + V.ANSI.BOLD + header + V.ANSI.ENDC

    fn1 = self.log1.name.ljust(self.log_width)[:self.log_width]
    fn2 = self.log2.name.ljust(self.log_width)[:self.log_width]

    print fn1 + self.get_sep() + fn2
    print header + self.get_sep() + header
    return


  # Get needed info from a record
  def get_message(self, m):
    if m == None:
      return ''.ljust(self.msg_width)

    msg = ''
    if m.TAG == 'QOR':
      if self.setup:
        msg += ' %10s %10s %10s' % (m.wns, m.tns, m.nsv)
      if self.hold:
        msg += ' %10s %10s %10s' % (m.whv, m.thv, m.nhv)
      if self.area:
        msg += ' %12s %10s' % (m.area, m.num_inst)
      if self.drc:
        msg += ' %10s %7s %10s %7s' % (m.max_tran, m.max_tran_v, m.max_cap, m.max_cap_v)
      if self.buf:
        msg += ' %10s %10s' % (m.num_buf, m.num_inv)
      if self.power:
        msg += ' %11s %8s %7s' % (m.leakage, m.num_lvth, m.pct_lvth)
      if self.runtime:
        msg += ' %9s %6ds %7s' % (m.elapsed, m.delta_elapsed, m.peak_mem)
      if msg != '':
        msg = msg[1:]
    else:
      msg = m.to_compact_string()

    if len(msg) > self.msg_width:
      msg = msg[:self.msg_width - 4] + ' ...'
    else:
      msg = msg.ljust(self.msg_width)
    return msg


  # Compose line with ANSI color
  def compose_line(self, m):
    ln = ''
    tag = ''
    color = ''
    if m != None:
      ln = m.ln
      tag = m.get_tag()
      color = m.COLOR

    msg = self.get_message(m)

    if self.colored:
      line = '%9s ' % (str(ln))
      line += V.ANSI.REVERSED + ' ' + V.ANSI.ENDC
      line += color + ' %-10s ' % (tag) + V.ANSI.ENDC
      line += V.ANSI.REVERSED + ' ' + V.ANSI.ENDC
      line += ' ' + color + msg + V.ANSI.ENDC
    else:
      line = '%9s | %-10s | %s' % (str(ln), tag, msg)

    return line


  # Used for finding best match
  def is_similar(self, m1, m2):
    if m1 == None or m2 == None:
      return True
    if m1.tag != m2.tag:
      return False
    if m1.TAG != 'QOR':
      return m1.to_string().split(' ')[0] == m2.to_string().split(' ')[0]
    else:
      if m1.tag == 'APS':
        name1 = m1.name
        name2 = m2.name
        if name1 == '' or name1 == 'OPT' or name2 == '' or name2 == 'OPT':
          return True
        else:
          return name1 == name2
      elif m1.tag == 'NPO' or m1.tag == 'NRO':
        name1 = m1.name
        name2 = m2.name
        if name1 == '' or name1.startswith('Ph.') or name2 == '' or name2.startswith('Ph.'):
          return True
        else:
          return name1 == name2

    return True


  # Show comparison
  def show(self, v1, v2):
    if len(v1.info) == 0 and len(v2.info) == 0:
      return

    # print header
    print
    self.cprint_header()

    # find best match
    lnvec1 = sorted(v1.info.keys())
    lnvec2 = sorted(v2.info.keys())
    len1 = len(lnvec1)
    len2 = len(lnvec2)
    dp = [[0 for x in range(len2 + 1)] for y in range(len1 + 1)]
    for i in range(len1):
      m1 = v1.info[lnvec1[i]]
      for j in range(len2):
        m2 = v2.info[lnvec2[j]]
        if self.is_similar(m1, m2):
          dp[i][j] = dp[i - 1][j - 1] + 1
        else:
          dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    best_match = []
    i = len1 - 1
    j = len2 - 1
    while i >= 0 and j >= 0:
      if i > 0 and j > 0:
        if dp[i-1][j-1] >= dp[i][j-1] and dp[i-1][j-1] >= dp[i-1][j]:
          best_match.append((lnvec1[i], lnvec2[j]))
          i -= 1
          j -= 1
        elif dp[i-1][j-1] < dp[i-1][j]:
          best_match.append((lnvec1[i], None))
          i -= 1
        else:
          best_match.append((None, lnvec2[j]))
          j -= 1
      elif i > 0:
        best_match.append((lnvec1[i], None))
        i -= 1
      elif j > 0:
        best_match.append((None, lnvec2[j]))
        j -= 1
      else:
       break; # stop when i == 0 and j == 0

    # show results
    for match in reversed(best_match):
      ln1, ln2 = match
      if ln1 != None:
        m1 = v1.info[ln1]
      else:
        m1 = None
      if ln2 != None:
        m2 = v2.info[ln2]
      else:
        m2 = None

      left = self.compose_line(m1)
      right = self.compose_line(m2)
      print left + self.get_sep() + right

    print
    return


##############################################################################

# Author: Deyuan Guo
def icc2_log_comparator():
  sys.tracebacklimit = 0
  comparator = ICC2LogComparator()
  comparator.run()
  return


# Entry. Deyuan Guo. 09/25/2017
if __name__ ==  '__main__' :
  icc2_log_comparator()


