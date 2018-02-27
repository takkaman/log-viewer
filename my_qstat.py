#!/remote/us01home46/dguo/bin/python
# -*- coding: utf-8 -*-
"""
File: qstat_dguo.py
Version: Python-2.7
Brief:
  Show qstat in a nice format

Author:  Deyuan Guo <dguo@synopsys.com>
Team:    ICC2 Optimization Team @ Synopsys, Inc.

File history:
  10/17/2017 Created
"""

import argparse
import subprocess

def get_whoami():
  cmd = 'whoami'
  return subprocess.check_output(cmd, shell=True).strip()

def get_job_details(job_id):
  cmd = 'qstat -j ' + str(job_id)
  return subprocess.check_output(cmd, shell=True)

def get_job_list(user):
  cmd = 'qstat -u ' + user
  return subprocess.check_output(cmd, shell=True)

def show_job(job_id):
  job_details = get_job_details(job_id)

  job_number = '--'
  submission_time = '--/--/---- --:--:--'
  owner = '--'
  job_name = '--'
  start_time = '--/--/---- --:--:--'
  job_state = '--'
  exec_host_list = '--'
  mt = '1'

  lines = job_details.split('\n')
  for line in lines:
    if line.startswith('job_number'):
      job_number = line.split(':', 1)[1].strip()
    elif line.startswith('submission_time'):
      submission_time = line.split(':', 1)[1].split('.')[0].strip()
    elif line.startswith('owner'):
      owner = line.split(':', 1)[1].strip()
    elif line.startswith('job_name'):
      job_name = line.split(':', 1)[1].strip()
    elif line.startswith('start_time'):
      start_time = line.split(':', 1)[1].split('.')[0].strip()
    elif line.startswith('job_state'):
      job_state = line.split(':', 1)[1].strip()
    elif line.startswith('exec_host_list'):
      exec_host_list = line.split(':', 1)[1].split('.')[0].strip()
    elif line.startswith('parallel environment:  mt range:'):
      mt = line.split(':', 2)[2].strip()

  if start_time.startswith('--') and job_state == '--':
    job_state = 'qw'

  print '%10s %-40s  %10s %5s %5s  %-19s  %-19s  %-s' % (job_number, job_name[:40], owner, job_state, mt, submission_time, start_time, exec_host_list)

  return

def show_all_jobs(user):
  all_jobs = get_job_list(user)

  print '%10s %-40s  %10s %5s %5s  %-19s  %-19s  %-s' % ('job-ID', 'name', 'user', 'state', 'slots', 'submit at', 'start at', 'hosts')
  print '-------------------------------------------------------------------------------------------------------------------------------------------'

  lines = all_jobs.split('\n')
  for line in lines:
    if not line.startswith('job') and not line.startswith('---') and not line.strip() == '':
      job_id = line.strip().split(' ', 1)[0]
      show_job(job_id)

  return

# Entry. Deyuan Guo. 09/25/2017
if __name__ ==  '__main__' :
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group()
  group.add_argument('-u', metavar='user', help='Show qstat of a user', type=str)
  group.add_argument('-j', metavar='job-ID', help='Show qstat of a job', type=int)
  args = parser.parse_args()

  if args.u:
    show_all_jobs(args.u)
  elif args.j:
    show_job(args.j)
  else:
    show_all_jobs(get_whoami())


