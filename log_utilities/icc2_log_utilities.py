#!/remote/us01home46/dguo/bin/python
# -*- coding: utf-8 -*-
"""
ICC2 log file processing utilities
Created on Oct 12, 2017
@author: Deyuan Guo <dguo@synopsys.com>
"""

import sys
import os
import gzip
import re


###############################################################################
# Author: Deyuan Guo
# Note: Given the path of a log file, read and return log contents as a string
###############################################################################
def load_log_file(log_path):
  if not os.path.exists(log_path) or not os.path.isfile(log_path):
    print 'Error: Cannot access log file', log_path
    return ''

  log = ''
  if log_path.endswith('.gz'):
    logFileObj = open(log_path, 'r')
    decompressedFile = gzip.GzipFile(fileobj=logFileObj) #gunzip
    log = decompressedFile.read()
    logFileObj.close()
  else:
    logFileObj = open(log_path, 'r')
    log = logFileObj.read()
    logFileObj.close()

  return log


###############################################################################
# Author: Deyuan Guo
# Note: From line number start_ln, find the line number of the next line
#       starting with line_prefix
###############################################################################
def get_next_ln_starts_with(lines, start_ln, line_prefix, forward=True):
  if type(lines) != list or start_ln == None:
    return None

  if forward == True:
    for i in range(start_ln, len(lines)):
      if lines[i].startswith(line_prefix):
        return i
  else:
    for i in range(start_ln, 0, -1):
      if lines[i].startswith(line_prefix):
        return i

  return None


###############################################################################
# Author: Deyuan Guo
# Note: From line number start_ln, find the nearest ELAPSE time
###############################################################################
def get_elapse_time(lines, start_ln, forward=True):
  if type(lines) != list or start_ln == None:
    return 0

  if forward:
    for i in range(start_ln, len(lines)):
      if (lines[i].startswith('START_CMD:') or lines[i].startswith('END_CMD:') or
          lines[i].startswith('START_FUNC:') or lines[i].startswith('END_FUNC:')):
        match = re.search('ELAPSE:\s+(\d+) s', lines[i])
        if match:
          return int(match.group(1))
  else:
    for i in range(start_ln, 0, -1):
      if (lines[i].startswith('START_CMD:') or lines[i].startswith('END_CMD:') or
          lines[i].startswith('START_FUNC:') or lines[i].startswith('END_FUNC:')):
        match = re.search('ELAPSE:\s+(\d+) s', lines[i])
        if match:
          return int(match.group(1))

  return 0

###############################################################################
# Author: Deyuan Guo
# Note: Given a heartbeat line, extract data
###############################################################################
def parse_heartbeat(line):
  qor = {}
  qor['valid'] = False
  qor['type'] = ''
  qor['name'] = ''
  qor['elapsed'] = ''
  qor['wns'] = ''
  qor['tns'] = ''
  qor['nsv'] = ''
  qor['whs'] = ''
  qor['ths'] = ''
  qor['nhv'] = ''
  qor['area'] = ''
  qor['bufcnt'] = ''
  qor['invcnt'] = ''
  qor['instcnt'] = ''
  qor['maxtran'] = ''
  qor['maxtranv'] = ''
  qor['maxcap'] = ''
  qor['maxcapv'] = ''
  qor['leakage'] = ''
  qor['numlvth'] = ''
  qor['pctlvth'] = ''
  qor['peakmem'] = ''

  tokens = line.split()

  if len(tokens) < 10:
    return qor

  if line.startswith('    *   * '):
    if len(tokens) >= 16:
      qor['valid'] = True
      qor['type'] = 'NPO'
      qor['wns'] = tokens[2]
      qor['tns'] = tokens[3]
      qor['nsv'] = tokens[4]
      qor['whs'] = tokens[5]
      qor['ths'] = tokens[6]
      qor['nhv'] = tokens[7]
      qor['maxtranv'] = tokens[8]
      qor['maxtran'] = tokens[9]
      qor['maxcapv'] = tokens[10]
      qor['leakage'] = tokens[11]
      qor['area'] = tokens[12]
      qor['instcnt'] = tokens[13]
      qor['bufcnt'] = tokens[14]
      qor['invcnt'] = tokens[15]

    elif len(tokens) >= 13:
      qor['valid'] = True
      qor['type'] = 'NRO'
      qor['wns'] = tokens[2]
      qor['tns'] = tokens[3]
      qor['nsv'] = tokens[4]
      qor['whs'] = tokens[5]
      qor['ths'] = tokens[6]
      qor['nhv'] = tokens[7]
      qor['maxtranv'] = tokens[8]
      qor['maxcapv'] = tokens[9]
      qor['leakage'] = tokens[10]
      qor['area'] = tokens[11]
      qor['instcnt'] = tokens[12]

  else:
    if ':' not in tokens[0]:
      qor['name'] = tokens.pop(0)
    if len(tokens) >= 11:
      qor['valid'] = True
      qor['type'] = 'APS'
      qor['elapsed'] = tokens[0]
      qor['wns'] = tokens[1]
      qor['tns'] = tokens[2]
      qor['area'] = tokens[3]
      qor['maxtran'] = tokens[4]
      qor['maxcap'] = tokens[5]
      qor['bufcnt'] = tokens[6]
      qor['invcnt'] = tokens[7]
      qor['numlvth'] = tokens[8]
      qor['pctlvth'] = tokens[9]
      qor['peakmem'] = tokens[10]
    if len(tokens) >= 12:
      whs = tokens[11]
      if whs.startswith('-'):
        whs = whs[1:]
      qor['whs'] = whs

  return qor


