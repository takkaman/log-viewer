#!/remote/us01home46/dguo/bin/python
# -*- coding: utf-8 -*-
"""
09/17/2017
@author: Deyuan Guo <dguo@synopsys.com>
History:
  10/16/2017 - monitor total virtual memory per user as well
"""

import time
import psutil
import socket
from collections import deque
import smtplib
from email.mime.text import MIMEText


# Global settings
MachineName = socket.gethostname()
TimeInterval = 30                           # [1-60] seconds
CheckIteration = 5                          # iterations before sending an email
VirtMemThreshold = 15 * 1024 * 1024 * 1024  # 15GB
UserVirtMemThreshold = 3 * VirtMemThreshold # 45GB
LogFileName = 'monitor.log'


# Record of a process
class ProcessRecord:

  def __init__(self):
    self.procObj = None
    self.createTime = None
    self.sentEmail = False
    self.timestamp = '--:--:--'
    self.pid = -1
    self.username = '--'
    self.command = '--'
    self.cpuPct = 0.0   # %CPU
    self.memPct = 0.0   # %MEM
    self.vms = 0        # VIRT
    self.rss = 0        # RES
    self.count = 0

  def to_string(self):
    s = "%-20s %5d %-10s %12d %12d %6.2f%% %6.2f%% %s\n" % (
        self.timestamp,
        self.pid,
        self.username,
        self.vms,
        self.rss,
        self.cpuPct,
        self.memPct,
        self.command)
    return s


# Send a warning email to user
def sendEmail(procRecord, user, pid):

  # Generate email body in HTML format
  body = "<html><head></head><body><p>\n"
  body += 'Dear %s,<br>\n<br>\n' % (user)
  body += "This is a friendly warning message automatically sent from %s server. " % (MachineName)
  body += "The %s machine is served as a VNC server for R&Ds. " % (MachineName)
  if pid == -1:
    body += "Your processes consume more than %dGB virtual memory in total, which might slow down all VNC sessions on this machine because of memory page swapping. " % (VirtMemThreshold/1024/1024/1024)
  else:
    body += "Your process below consumes more than %dGB virtual memory, which might slow down all VNC sessions on this machine because of memory page swapping. " % (UserVirtMemThreshold/1024/1024/1024)
  body += "Please consider to run your heavy-duty job on PD/LS farm machines. Thanks.<br>\n<br>\n"

  body += "<pre><code><font face='monospace'>"
  body += '%-20s %5s %-10s %12s %12s %7s %7s %s\n' % ('TIME', 'PID', 'USER', 'VIRT', 'RES', '%CPU', '%MEM', 'COMMAND')

  if pid == -1:
    totalVm = 0
    for pid in sorted(procRecord.keys(), reverse=True):
      r = procRecord[pid]
      if r.username != user:
        continue
      body += r.to_string()
      totalVm += r.vms
    body += 'Total VIRT Memory Usage: %.3f GB' % (totalVm / 1024.0 / 1024.0 / 1024.0)
  else:
    r = procRecord[pid]
    body += r.to_string()

  body += "</font></code></pre>\n"

  body += "<br>\nRegards,<br>\nDeyuan\n"
  body += "</p></body></html>"

  # Email recipients
  fromAddress = 'dguo@synopsys.com'
  toAddress = user + '@synopsys.com'
  #ccAddress = 'jengt@synopsys.com'
  ccAddress = ''

  msg = MIMEText(body)
  msg.add_header('Content-Type', 'text/html')
  msg['Subject'] = '[Auto] Your process consumes more than %dGB virtual memory on %s server' % (VirtMemThreshold/1024/1024/1024, MachineName)
  msg['From'] = fromAddress
  msg['To'] = toAddress
  msg['Cc'] = fromAddress + ',' + ccAddress

  s = smtplib.SMTP('localhost')
  recipientList = [toAddress, fromAddress, ccAddress]
  s.sendmail(fromAddress, recipientList, msg.as_string())
  return


# Write start message to log file
def writeStartLog():
  with open(LogFileName, 'a') as f:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log = '%s: Start monitoring processes on server %s\n' % (timestamp, MachineName)
    f.write(log)


# Refresh
def refreshRecord(procRecord, timestamp):

  # Remove non-exist processes in record
  for pid in procRecord.keys():
    proc = procRecord[pid].procObj
    if not proc.is_running():
      procRecord.pop(pid, None)

  # Check current processes
  procs = [proc for proc in psutil.process_iter()]
  for p in procs:
    try:
      pid = p.pid
      username = p.username()
      if username == 'root': # skip root processes
        continue
      command = p.name()
      createTime = p.create_time()
      cpuPct = p.cpu_percent()
      memPct = p.memory_percent()
      rss = p.memory_info().rss
      vms = p.memory_info().vms

      if procRecord.has_key(pid) and procRecord[pid].createTime == createTime:
        # Refresh record
        procRecord[pid].timestamp = timestamp
        procRecord[pid].cpuPct = cpuPct
        procRecord[pid].memPct = memPct
        procRecord[pid].rss = rss
        procRecord[pid].vms = vms
        if vms <= VirtMemThreshold:
          procRecord[pid].count = 0
        else:
          procRecord[pid].count += 1
      else:
        # New record
        record = ProcessRecord()
        record.procObj = p
        record.pid = pid
        record.username = username
        record.command = command
        record.createTime = createTime
        record.timestamp = timestamp
        record.cpuPct = cpuPct
        record.memPct = memPct
        record.rss = rss
        record.vms = vms
        if vms <= VirtMemThreshold:
          record.count = 0
        else:
          record.count += 1
        procRecord[pid] = record

    except psutil.NoSuchProcess:
      pass

  return


# Check
def checkRecord(procRecord, userRecord, timestamp):
  users = {}

  # Calculate total vms and max vms
  for pid in procRecord.keys():
    r = procRecord[pid]
    if r.command == 'ld': # skip ld processes
      continue
    if users.has_key(r.username):
      totalVm, maxVm, maxPid = users[r.username]
      totalVm += r.vms
      if maxVm < r.vms:
        maxVm = r.vms
        maxPid = pid
      users[r.username] = (totalVm, maxVm, maxPid)
    else:
      users[r.username] = (r.vms, r.vms, pid)

  # Sent email if vms exceed the threshold for some continuous time intervals
  for u in users.keys():
    totalVm, maxVm, maxPid = users[u]
    r = procRecord[maxPid]
    #print u, totalVm, maxVm, maxPid

    # Check max vms
    if maxVm > VirtMemThreshold:
      if r.sentEmail == False and r.count >= CheckIteration:
        sendEmail(procRecord, u, maxPid)
        r.sentEmail = True
        with open(LogFileName, 'a') as f:
          log = '%s: Sent an email to %s for process %d %s with %d GB virt mem\n' % (timestamp, u, maxPid, r.command, r.vms/1024/1024/1024)
          f.write(log)
      print '%s: [count = %3d] user %s pid %d consumes virt mem %d GB' % (timestamp, r.count, u, maxPid, r.vms/1024/1024/1024)

    # Check total vms
    if totalVm > UserVirtMemThreshold:
      if not userRecord.has_key(u):
        count = 1
        sentEmail = False
        userRecord[u] = (count, sentEmail)
      else:
        count, sentEmail = userRecord[u]
        count += 1
        if count >= CheckIteration and sentEmail == False:
          sendEmail(procRecord, u, -1)
          sentEmail = True
          with open(LogFileName, 'a') as f:
            log = '%s: Sent an email to %s for total virt mem %d GB\n' % (timestamp, u, totalVm/1024/1024/1024)
            f.write(log)
        userRecord[u] = (count, sentEmail)
      print '%s: [count = %3d] user %s consumes total virt mem %d GB' % (timestamp, count, u, totalVm/1024/1024/1024)
    else:
      count = 0
      sentEmail = False
      userRecord[u] = (count, sentEmail)

  return


# Main Loop
def mainLoop():
  writeStartLog()

  procRecord = {}
  userRecord = {}

  while (True):

    # Monitor time interval
    now = time.localtime()
    time.sleep(TimeInterval - now.tm_sec % TimeInterval)
    now = time.localtime()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", now)

    # Empty user record every hour for total virt mem usage check
    #if time.localtime().tm_min == 0 and time.localtime().tm_sec < TimeInterval:
    #  userRecord = {}

    # Refresh
    refreshRecord(procRecord, timestamp)

    # Check and send email
    checkRecord(procRecord, userRecord, timestamp)


# Main entry
if __name__ == '__main__':
  mainLoop()


