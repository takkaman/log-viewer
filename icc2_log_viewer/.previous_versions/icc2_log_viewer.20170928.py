#!/remote/us01home46/dguo/bin/python
# -*- coding: utf-8 -*-
"""
File: icc2_log_viewer.py
Brief:
  A script to help to quickly understand ICC2 optimization logs
  Usage: python-2.7 icc2_log_viewer.py <args>

Author:  Deyuan Guo <dguo@synopsys.com>
Manager: Jeng-Liang Tsai <jengt@synopsys.com>
Team:    ICC2 Optimization Team @ Synopsys, Inc.

SYNOPSYS CONFIDENTIAL - This is an unpublished, proprietary work of
Synopsys, Inc., and is fully protected under copyright and trade
secret laws. You may not view, use, disclose, copy, or distribute this
file or any information contained herein except pursuant to a valid
written license from Synopsys.

File history:
  09/25/2017 Created
"""

import sys
import os
import gzip
import re
import argparse


##############################################################################

# Author: Deyuan Guo
# Terminal ANSI colors
class ANSI:
  BOLD =      '\033[1m'
  UNDERLINE = '\033[4m'
  REVERSED =  '\033[7m'
  BGBLACK =   '\033[40m'
  BGBLUE =    '\033[44m'
  RED =       '\033[91m'
  GREEN =     '\033[92m'
  YELLOW =    '\033[93m'
  BLUE =      '\033[94m'
  MAGENTA =   '\033[95m'
  CYAN =      '\033[96m'
  ENDC =      '\033[0m'

##############################################################################

# Author: Deyuan Guo
# Data Model: cellMap
class M_cmap:
  TAG = 'CMAP'
  COLOR = ANSI.BLUE
  def __init__(self):
    self.ln = 0
    self.tag = self.TAG
    self.info = ''

# Author: Deyuan Guo
# Data View: cellMap
class V_cmap:
  @staticmethod
  def to_string(m):
    return m.info

# Author: Deyuan Guo
# Data Controller: cellMap
class C_cmap:
  @staticmethod
  def collect_data(logs):
    m_vec = []
    for i in range(0, len(logs)):
      line = logs[i]
      if line.startswith('START_FUNC: nplCellMap::nplCellMap'):
        m = M_cmap()
        m.ln = i + 1
        m.info = 'ctor'
        m_vec.append(m)
    return m_vec

##############################################################################

# Author: Deyuan Guo
# Data Model: ICC2 command
class M_cmd:
  TAG = 'CMD'
  COLOR = ANSI.BLUE
  def __init__(self):
    self.ln = 0
    self.tag = self.TAG
    self.cmd = ''

# Author: Deyuan Guo
# Data View: ICC2 command
class V_cmd:
  @staticmethod
  def to_string(m):
    return m.cmd

# Author: Deyuan Guo
# Data Controller: ICC2 command
class C_cmd:
  @staticmethod
  def collect_data(logs):
    m_vec = []
    for i in range(0, len(logs)):
      line = logs[i]
      if line.startswith('START_CMD:'):
        match = re.search('CMD:\s(.*)\sCPU:', line)
        if match:
          cmd = match.group(1).strip()
          if cmd == 'route_opt_cmd':
            continue # ignore route_opt_cmd for now
          m = M_cmd()
          m.ln = i + 1
          m.cmd = cmd
          m_vec.append(m)
    return m_vec

##############################################################################

# Author: Deyuan Guo
# Data Model: CTS/CCD
class M_cts:
  TAG = 'CTS'
  COLOR = ANSI.BLUE
  def __init__(self):
    self.ln = 0
    self.tag = self.TAG
    self.info = ''

# Author: Deyuan Guo
# Data View: CTS/CCD
class V_cts:
  @staticmethod
  def to_string(m):
    return m.info

# Author: Deyuan Guo
# Data Controller: CTS/CCD
class C_cts:
  @staticmethod
  def collect_data(logs):
    m_vec = []
    for i in range(0, len(logs)):
      line = logs[i]
      if line.startswith('START_FUNC: ctsInterf::'):
        match = re.search('START_FUNC: ctsInterf::(.*)\sCPU:', line)
        if match:
          cts = match.group(1).strip()
          if cts == 'ccd':
            continue # capture it in another way
          m = M_cts()
          m.ln = i + 1
          m.info = cts
          m_vec.append(m)
      elif line.startswith('START_FUNC: Concurrent Clock Data Optimization'):
        m = M_cts()
        m.ln = i + 1
        m.info = 'CCD'
        m_vec.append(m)
    return m_vec

##############################################################################

# Author: Deyuan Guo
# Data Model: GR
class M_gr:
  TAG = 'GR'
  COLOR = ANSI.MAGENTA
  def __init__(self):
    self.ln = 0
    self.tag = self.TAG
    self.info = ''

# Author: Deyuan Guo
# Data View: GR
class V_gr:
  @staticmethod
  def to_string(m):
    return m.info

# Author: Deyuan Guo
# Data Controller: GR
class C_gr:
  @staticmethod
  def collect_data(logs):
    m_vec = []
    for i in range(0, len(logs)):
      line = logs[i]
      if line.startswith('Start Global Route ...'):
        m = M_gr()
        m.ln = i + 1
        m.info = 'GR'
        m_vec.append(m)
    return m_vec

##############################################################################

# Author: Deyuan Guo
# Data Model: LGL
class M_lgl:
  TAG = 'LGL'
  COLOR = ANSI.MAGENTA
  def __init__(self):
    self.ln = 0
    self.tag = self.TAG
    self.info = ''
    self.lgl_moved = '--'
    self.lgl_total = '--'
    self.lgl_avg = '--'
    self.lgl_max = '--'
    self.lgl_large = '--'
    self.place_pct = '--'

# Author: Deyuan Guo
# Data View: LGL
class V_lgl:
  @staticmethod
  def to_string(m):
    if m.info == 'LGL':
      pct = '--'
      if m.lgl_moved != '--' and m.lgl_total != '--':
        moved = int(m.lgl_moved)
        total = int(m.lgl_total)
        if total != 0:
          pct = '%.3f' % (100.0 * moved / total)
      return '%s : moved %s/%s %s%% cells, avg %s, max %s, large %s' % (m.info,
             m.lgl_moved, m.lgl_total, pct, m.lgl_avg, m.lgl_max, m.lgl_large)
    elif m.info == 'PLACE':
      if m.place_pct != '--':
        return '%s : %s%% - 100%%' % (m.info, m.place_pct)
    return m.info

# Author: Deyuan Guo
# Data Controller: LGL
class C_lgl:
  @staticmethod
  def collect_data(logs):
    m_vec = []
    for i in range(0, len(logs)):
      line = logs[i]
      if line.startswith('Starting legalizer.'):
        m = M_lgl()
        m.ln = i + 1
        m.info = 'LGL'
        m_vec.append(m)
      elif line.startswith('Running placement using '):
        m = M_lgl()
        m.ln = i + 1
        m.info = 'PLACE'
        m_vec.append(m)

    C_lgl.discover_lgl_data(logs, m_vec)
    C_lgl.discover_place_data(logs, m_vec)
    return m_vec

  @staticmethod
  def discover_lgl_data(logs, m_vec):
    for k in range(0, len(m_vec)):
      m = m_vec[k]
      if m.info != 'LGL':
        continue
      ln = m.ln
      if k == len(m_vec) - 1:
        next_ln = len(logs)
      else:
        next_ln = m_vec[k + 1].ln
      for i in range(ln + 1, next_ln):
        line = logs[i]
        if line.startswith('number of cells aggregated:'):
          m.lgl_total = (line.split())[4].strip()
        elif line.startswith('max cell displacement:'):
          m.lgl_max = (line.split())[3].strip()
        elif line.startswith('avg cell displacement:'):
          m.lgl_avg = (line.split())[3].strip()
        elif line.startswith('number of cells moved:'):
          m.lgl_moved = (line.split())[4].strip()
        elif line.startswith('number of large displacements:'):
          m.lgl_large = (line.split())[4].strip()
          break
    return

  @staticmethod
  def discover_place_data(logs, m_vec):
    for k in range(0, len(m_vec)):
      m = m_vec[k]
      if m.info != 'PLACE':
        continue
      ln = m.ln
      for i in range(ln + 1, min(ln + 50, len(logs))):
        line = logs[i]
        match = re.search('coarse place (\d+)% done.', line)
        if match:
          m.place_pct = match.group(1)
          break
    return

##############################################################################

# Author: Deyuan Guo
# Data Model: QoR Heartbeat
class M_qor:
  TAG = 'QOR'
  COLOR = ANSI.GREEN
  def __init__(self):
    self.ln = 0
    self.tag = self.TAG
    self.line = ''
    self.valid = False
    self.name = ''
    self.elapsed = '--'
    self.wns = '--'
    self.tns = '--'
    self.nsv = '--'
    self.whv = '--'
    self.thv = '--'
    self.nhv = '--'
    self.max_tran = '--'
    self.max_tran_v = '--'
    self.max_cap = '--'
    self.max_cap_v = '--'
    self.area = '--'
    self.num_inst = '--'
    self.num_buf = '--'
    self.num_inv = '--'
    self.num_lvth = '--'
    self.pct_lvth = '--'
    self.leakage = '--'
    self.peak_mem = '--'

# Author: Deyuan Guo
# Data View: QoR Heartbeat
class V_qor:
  @staticmethod
  def to_string(m):
    if not m.valid:
      return m.line.strip()
    if not ICC2LogParser.verbose:
      s = '%9s %10s %10s %12s %10s %10s %10s %10s' % (
          m.elapsed,
          m.wns, m.tns,
          m.area,
          m.num_buf, m.num_inv,
          m.max_tran, m.max_cap
          )
    else:
      s = '%9s %10s %10s %10s %10s %10s %10s %12s %10s %10s %10s %10s %7s %10s %7s %11s %8s %7s %7s' % (
          m.elapsed,
          m.wns, m.tns, m.nsv,
          m.whv, m.thv, m.nhv,
          m.area,
          m.num_buf, m.num_inv, m.num_inst,
          m.max_tran, m.max_tran_v, m.max_cap, m.max_cap_v,
          m.leakage, m.num_lvth, m.pct_lvth, m.peak_mem
          )
    return s

  @staticmethod
  def header():
    if not ICC2LogParser.verbose:
      h = '%9s %10s %10s %12s %10s %10s %10s %10s' % (
          'Elapsed',
          'WNS', 'TNS',
          'Area',
          'BufCnt', 'InvCnt',
          'MaxTran', 'MaxCap'
          )
    else:
      h = '%9s %10s %10s %10s %10s %10s %10s %12s %10s %10s %10s %10s %7s %10s %7s %11s %8s %7s %7s' % (
          'Elapsed',
          'WNS', 'TNS', 'NSV',
          'WHV', 'THV', 'NHV',
          'Area',
          'BufCnt', 'InvCnt', 'InstCnt',
          'MaxTran', 'MTranV', 'MaxCap', 'MCapV',
          'Leakage', 'NumLvth', '%Lvth', 'PeakMem'
          )
    return h

# Author: Deyuan Guo
# Data Controller: QoR Heartbeat
class C_qor:
  @staticmethod
  def collect_data(logs):
    m_vec = []
    for i in range(0, len(logs)):
      line = logs[i]
      if line.strip().startswith('ELAPSED  WORST NEG TOTAL NEG'):
        if i + 3 < len(logs):
          m_vec.append(C_qor.collect_aps_qor(logs, i + 3))
      elif line.startswith('    *   * '):
        if len(line.split()) == 16:
          m_vec.append(C_qor.collect_npo_qor(logs, i))
        elif len(line.split()) == 13:
          m_vec.append(C_qor.collect_nro_qor(logs, i))

    # Discover more information from logs
    C_qor.discover_time_mem(logs, m_vec)
    C_qor.discover_heartbeat_name(logs, m_vec)
    return m_vec

  @staticmethod
  def collect_aps_qor(logs, ln):
    m = M_qor()
    m.ln = ln + 1
    m.tag = 'APS'
    m.line = logs[ln]
    tokens = m.line.split()

    if len(tokens) > 0:
      if ':' not in tokens[0]: # APS QoR Heartbeat - debug
        m.name = tokens.pop(0)

    if len(tokens) >= 11:
      m.valid = True
      m.elapsed = tokens[0]
      m.wns = tokens[1]
      m.tns = tokens[2]
      m.area = tokens[3]
      m.max_tran = tokens[4]
      m.max_cap = tokens[5]
      m.num_buf = tokens[6]
      m.num_inv = tokens[7]
      m.num_lvth = tokens[8]
      m.pct_lvth = tokens[9]
      m.peak_mem = tokens[10]
    if len(tokens) >= 12:
      m.whv = tokens[11]
      if m.whv.startswith('-'): # negative whv value is shown
        m.whv = m.whv[1:]
    return m

  @staticmethod
  def collect_npo_qor(logs, ln):
    m = M_qor()
    m.ln = ln + 1
    m.tag = 'NPO'
    m.line = logs[ln]
    tokens = m.line.split()
    if len(tokens) == 16: # NPO QoR Heartbeat
      m.valid = True
      m.tag = 'NPO'
      m.wns = tokens[2]
      m.tns = tokens[3]
      m.nsv = tokens[4]
      m.whv = tokens[5]
      m.thv = tokens[6]
      m.nhv = tokens[7]
      m.max_tran_v = tokens[8]
      m.max_tran = tokens[9]
      m.max_cap_v = tokens[10]
      m.leakage = tokens[11]
      m.area = tokens[12]
      m.num_inst = tokens[13]
      m.num_buf = tokens[14]
      m.num_inv = tokens[15]
    return m

  @staticmethod
  def collect_nro_qor(logs, ln):
    m = M_qor()
    m.ln = ln + 1
    m.tag = 'NRO'
    m.line = logs[ln]
    tokens = m.line.split()
    if len(tokens) == 13: # NRO QoR Heartbeat
      m.valid = True
      m.wns = tokens[2]
      m.tns = tokens[3]
      m.nsv = tokens[4]
      m.whv = tokens[5]
      m.thv = tokens[6]
      m.nhv = tokens[7]
      m.max_tran_v = tokens[8]
      m.max_cap_v = tokens[9]
      m.leakage = tokens[10]
      m.area = tokens[11]
      m.num_inst = tokens[12]
    return m

  @staticmethod
  def discover_time_mem(logs, m_vec):
    prev_ln = 0
    for m in m_vec:
      if m.elapsed != "--":
        continue
      ln = m.ln
      for i in range(ln, prev_ln, -1):
        line = logs[i]
        match = re.search('ELAPSE:\s+(\d+) s ', line)
        if match:
          elapsed = int(match.group(1))
          mm, ss = divmod(elapsed, 60)
          hh, mm = divmod(mm, 60)
          m.elapsed = '%d:%02d:%02d' % (hh, mm, ss)
          if m.peak_mem == '--':
            match = re.search('MEM-PEAK:\s+(\d+) Mb', line)
            if match:
              m.peak_mem = match.group(1)
          break
      prev_ln = ln
    return

  @staticmethod
  def discover_heartbeat_name(logs, m_vec):
    for m in m_vec:
      if m.name != '':
        continue
      if m.tag == 'APS':
        ln = m.ln
        met_start = False
        for i in range(ln, max(0, ln-500), -1):
          line = logs[i]
          if not met_start:
            if line.startswith('START_FUNC: APS_S_DRC'):
              m.name = 'DRC'
              break
            elif line.startswith('START_FUNC: psynopt_delay_opto'):
              met_start = True
            elif line.startswith('START_FUNC: ') or line.startswith('END_FUNC: '):
              break
          else:
            if line.startswith('START_FUNC: APS_S_HOLD'):
              m.name = 'HOLD'
              break
            elif line.startswith('START_FUNC: ') or line.startswith('END_FUNC: '):
              m.name = 'OPT'
              break
    return

##############################################################################

# Author: Deyuan Guo
# Data Model: Flow information
class M_flow:
  TAG = 'FLOW'
  COLOR = ANSI.CYAN
  def __init__(self):
    self.ln = 0
    self.tag = self.TAG
    self.info = ''

# Author: Deyuan Guo
# Data View: Flow information
class V_flow:
  @staticmethod
  def to_string(m):
    return m.info

# Author: Deyuan Guo
# Data Controller: Flow information
class C_flow:
  @staticmethod
  def collect_data(logs):
    m_vec = []
    for i in range(0, len(logs)):
      line = logs[i]
      info = ''

      if line.startswith('Running'):
        if line == 'Running initial placement':
          info = 'initial_place'
        elif line == 'Running initial HFS and DRC step.':
          info = 'initial_drc'
        elif line == 'Running initial optimization step.':
          info = 'initial_opto'
        elif line == 'Running final (timing-driven) placement step.':
          info = 'final_place'
        elif line == 'Running final optimization step.':
          info = 'final_opto'
        elif line == 'Running clock synthesis step.':
          info = 'build_clock'
        elif line == 'Running clock routing step.':
          info = 'route_clock'

      if info != '':
        m = M_flow()
        m.ln = i + 1
        m.info = info
        m_vec.append(m)
    return m_vec

##############################################################################

# Author: Deyuan Guo
# ICC2 Log Parser
class ICC2LogParser:

  # static data members
  colored = True
  verbose = False


  # Constructor
  def __init__(self):
    self.args = None  # command line args
    self.logs = []    # log file contents
    self.info = {}    # extracted info
    return


  # Run
  def run(self):
    if self.parse_args():
      self.load_file()
      self.parse_log_file()
      self.show()
    return


  # Parse command line auguments
  def parse_args(self):
    parser = argparse.ArgumentParser()
    parser.add_argument('log',    help='ICC2 log file', type=file)
    parser.add_argument('-cmd',   help='show ICC2 command information', action='store_true')
    parser.add_argument('-cts',   help='show CTS/CCD information', action='store_true')
    parser.add_argument('-gr',    help='show GR information', action='store_true')
    parser.add_argument('-lgl',   help='show placement/legalization information', action='store_true')
    parser.add_argument('-qor',   help='show QoR information', action='store_true')
    parser.add_argument('-all',   help='show -cmd/cts/gr/lgl/qor (default)', action='store_true')
    parser.add_argument('-more',  help='show -all with more QoR columns', action='store_true')
    #parser.add_argument('-scn',   help='show scenario information', action='store_true')
    parser.add_argument('-cmap',  help='show cellMap information', action='store_true')
    parser.add_argument('-flow',  help='show opto flow information', action='store_true')
    parser.add_argument('--no-color', help='turn off color decorations for output redirection', action='store_true')

    if len(sys.argv) <= 1:
      print '--------------------------------'
      print ' ICC2 Log Viewer (ver.20170928) '
      print ' Deyuan Guo <dguo@synopsys.com> '
      print '--------------------------------'
      print
      parser.print_help()
      return False

    self.args = parser.parse_args()

    # Enable -all if no other option is provided
    if not (self.args.cmd or self.args.cts or self.args.gr or self.args.lgl or self.args.qor):
      self.args.all = True

    if self.args.no_color:
      ICC2LogParser.colored = False

    if self.args.more:
      ICC2LogParser.verbose = True

    if self.args.all:
      self.args.cmd = True
      self.args.cts = True
      self.args.gr = True
      self.args.lgl = True
      self.args.qor = True

    return True


  # Load file contents
  def load_file(self):
    if self.args == None or self.args.log == None:
      return False
    if self.args.log.name.endswith('.gz'):
      decompressedFile = gzip.GzipFile(fileobj=self.args.log) #gunzip
      contents = decompressedFile.read()
    else:
      contents = self.args.log.read()
    self.logs = contents.split('\n')

    print 'Info: File ' + self.args.log.name + ' has ' + str(len(self.logs)) + ' lines'

    banner = 'No ICC2 banner'
    for i in range(0, min(10, len(self.logs))):
      if self.logs[i].strip() == 'IC Compiler II (TM)':
        banner = 'IC Compiler II (TM)'
        if i + 2 < len(self.logs) and self.logs[i + 2].strip().startswith('Version'):
          banner += ' ' + self.logs[i + 2].strip()
    if banner != '':
      print 'Info:', banner

    return True


  # Parse log file
  def parse_log_file(self):
    if len(self.logs) == 0:
      return False

    if self.args.cmap:
      m_vec = C_cmap.collect_data(self.logs)
      for m in m_vec:
        self.info[m.ln] = m

    if self.args.cmd:
      m_vec = C_cmd.collect_data(self.logs)
      for m in m_vec:
        self.info[m.ln] = m

    if self.args.cts:
      m_vec = C_cts.collect_data(self.logs)
      for m in m_vec:
        self.info[m.ln] = m

    if self.args.gr:
      m_vec = C_gr.collect_data(self.logs)
      for m in m_vec:
        self.info[m.ln] = m

    if self.args.lgl:
      m_vec = C_lgl.collect_data(self.logs)
      for m in m_vec:
        self.info[m.ln] = m

    if self.args.qor:
      m_vec = C_qor.collect_data(self.logs)
      for m in m_vec:
        self.info[m.ln] = m

    if self.args.flow:
      m_vec = C_flow.collect_data(self.logs)
      for m in m_vec:
        self.info[m.ln] = m

    return True


  # Print message with ANSI color
  def cprint(self, lineno, tag, color, message):
    if ICC2LogParser.colored:
      msg = '%9s ' % (str(lineno))
      msg += ANSI.REVERSED + ' ' + ANSI.ENDC
      msg += color + ' %-10s ' % (tag) + ANSI.ENDC
      msg += ANSI.REVERSED + ' ' + ANSI.ENDC
      msg += ' ' + color + message + ANSI.ENDC
      print msg
    else:
      msg = '%9s | %-10s | %s' % (str(lineno), tag, message)
      print msg
    return


  # Print header with ANSI color
  def cprint_header(self):
    if self.args.qor:
      header = '%9s   %-10s   %-125s' % ('Line', 'Tag', V_qor.header())
    else:
      header = '%9s   %-10s   %-125s' % ('Line', 'Tag', 'Info')
    if ICC2LogParser.colored:
      print ANSI.REVERSED + ANSI.BOLD + header + ANSI.ENDC
    else:
      print header
    return


  # Show results
  def show(self):
    if len(self.info) == 0:
      return True

    print
    self.cprint_header()

    for i in sorted(self.info.keys()):
      m = self.info[i]

      if m.TAG == 'CMAP':
        self.cprint(m.ln, m.tag, m.COLOR, V_cmap.to_string(m))

      elif m.TAG == 'CMD':
        self.cprint(m.ln, m.tag, m.COLOR, V_cmd.to_string(m))

      elif m.TAG == 'CTS':
        self.cprint(m.ln, m.tag, m.COLOR, V_cts.to_string(m))

      elif m.TAG == 'GR':
        self.cprint(m.ln, m.tag, m.COLOR, V_gr.to_string(m))

      elif m.TAG == 'LGL':
        self.cprint(m.ln, m.tag, m.COLOR, V_lgl.to_string(m))

      elif m.TAG == 'QOR':
        self.cprint(m.ln, (m.tag + ' ' + m.name)[:10], m.COLOR, V_qor.to_string(m))

      elif m.TAG == 'FLOW':
        self.cprint(m.ln, m.tag, m.COLOR, V_flow.to_string(m))

    print
    return True


##############################################################################

# Author: Deyuan Guo
def icc2_log_viewer():
  sys.tracebacklimit = 0
  parser = ICC2LogParser()
  parser.run()
  return


# Entry. Deyuan Guo. 09/25/2017
if __name__ ==  '__main__' :
  icc2_log_viewer()

