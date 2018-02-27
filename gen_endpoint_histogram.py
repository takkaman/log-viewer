#!/remote/us01home46/dguo/bin/python3.5
# -*- coding: utf-8 -*-
# Author: Deyuan Guo
# File History:
#   11/01/2017 released

import os
import sys
import math
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np


# from /u/brent/util/hash/hash.c
def hash_chars(text):
  mask = 0xFFFFFFFF
  ret = 7653
  for i in range(0, len(text)):
    ret ^= ord(text[i])
    ret ^= ((ret << 8) & mask)
    ret ^= (ret >> 5)
  ret ^= ret >> 29
  ret ^= ((ret << 23) & mask)
  ret ^= ret >> 19
  ret ^= ((ret << 17) & mask)
  ret ^= ret >> 13
  ret ^= ((ret << 11) & mask)
  ret ^= ret >> 7
  ret ^= ((ret << 5) & mask)
  ret ^= ret >> 3
  ret ^= ((ret << 1) & mask)
  return ret


# Author: Deyuan Guo
def read_endpoint_file(path):
  ep_dict = {} # key = endpoint name, val = (slack, length, levels)

  names_inorder = True
  if names_inorder:
    names = []
    with open(path + ".names", "r") as f:
      contents = f.readlines()
      for line in contents:
        names.append(line.strip())

    data = []
    with open(path, "r") as f:
      contents = f.readlines()
      for line in contents:
        record = line.strip().split("\t")
        hashKey = int(record[0], 16)
        slack = float(record[1])
        length = float(record[2])
        levels = int(record[3])
        data.append([slack, length, levels])

    if len(names) != len(data):
      print("Warning: end points names do not match (%d names, %d records)" % (len(names), len(data)))
    for i in range(0, min(len(names), len(data))):
      ep_dict[names[i]] = data[i]

  else:
    name_dict = {}
    with open(path + ".names", "r") as f:
      contents = f.readlines()
      for line in contents:
        name = line.strip()
        key = hash_chars(name)
        name_dict[key] = name

    with open(path, "r") as f:
      contents = f.readlines()
      for line in contents:
        record = line.strip().split("\t")
        hashKey = int(record[0], 16)
        slack = float(record[1])
        length = float(record[2])
        levels = int(record[3])
        if hashKey in name_dict.keys():
          ep_dict[name_dict[hashKey]] = (slack, length, levels)

  return ep_dict


# Author: Deyuan Guo
def get_slack_list(ep_dict):
  tns = 0
  tps = 0
  cnt_neg = 0
  cnt_pos = 0
  all_slack = []
  for ep in ep_dict.keys():
    slack, length, levels = ep_dict[ep]
    if slack >= 0:
      tps += slack
      cnt_pos += 1
    else:
      tns += slack
      cnt_neg += 1
    all_slack.append(slack)
  print('#neg', cnt_neg, 'tns', tns, '#pos', cnt_pos, 'tps', tps)
  return all_slack


# Author: Deyuan Guo
def show_ep_hist_1(ep_d1):
  plt.figure(figsize=(20,5))
  ep_l1 = get_slack_list(ep_d1)
  lb = min(ep_l1)
  rb = max(ep_l1)
  interval = 0.005
  num_bins = int((rb - lb) / interval)
  plt.hist(ep_l1, bins=num_bins, range=(lb, rb))
  plt.suptitle('design endpoint histogram (interval = 5ps)')
  plt.xlabel('Endpoint Slack')
  plt.ylabel('Number of Endpoints')
  filename = 'design.ephist.png'
  print("Saving as", filename, "...")
  plt.savefig(filename, dpi=200)
  plt.close()
  return


# Author: Deyuan Guo
def show_ep_hist_2(ep_d1, ep_d2, legend1, legend2, design):
  plt.figure(figsize=(20,5))
  ep_l1 = get_slack_list(ep_d1)
  ep_l2 = get_slack_list(ep_d2)

  # slack lower bound and upper bound
  lb = -0.2
  rb = 0.6
  interval = 0.005
  num_bins = int((rb - lb) / interval)

  if len(ep_l1) < len(ep_l2):
    ep_l1 += [1000]*(len(ep_l2)-len(ep_l1))
  elif len(ep_l1) > len(ep_l2):
    ep_l2 += [1000]*(len(ep_l1)-len(ep_l2))

  # lower bound saturate
  for i in range(len(ep_l1)):
    if ep_l1[i] < lb:
      ep_l1[i] = lb + 0.001
  for i in range(len(ep_l2)):
    if ep_l2[i] < lb:
      ep_l2[i] = lb + 0.001

  data = np.vstack([ep_l1, ep_l2]).T

  plt.hist(data, bins=num_bins, range=(lb, rb), label=[legend1, legend2], color=['orange','royalblue'])
  plt.legend(loc='upper right')
  plt.suptitle(design + ' endpoint histogram (interval = 5ps)')
  plt.xlabel('Endpoint Slack')
  plt.ylabel('Number of Endpoints')
  filename = design + '.ephist.png'
  print("Saving as", filename, "...")
  plt.savefig(filename, dpi=200)
  plt.close()
  return


# Author: Deyuan Guo
def traverse_flows(flow1, stage1, legend1, flow2, stage2, legend2):
  if not os.path.exists(flow1) or not os.path.isdir(flow1):
    return
  if not os.path.exists(flow2) or not os.path.isdir(flow2):
    return

  for flow, designs, files in os.walk(flow1):
    designs.sort()
    for design in designs:
      print ("Processing", design, '...')

      design_path1 = os.path.join(flow1, design)
      endpoint_path1 = os.path.join(design_path1, ".prs.endpoints")
      if not os.path.exists(endpoint_path1):
        next

      design_path2 = os.path.join(flow2, design)
      endpoint_path2 = os.path.join(design_path2, ".prs.endpoints")
      if not os.path.exists(endpoint_path2):
        next

      ep_file_name = {'icp' : 'nwprpt_all', 'icc' : 'nwcrpt_all', 'icr' : 'nwrrpt_all', 'icf' : 'nwrpt_all'}
      fname1 = ep_file_name.get(stage1)
      fname2 = ep_file_name.get(stage2)
      if fname1 != None and fname2 != None:
        ep_path1 = os.path.join(endpoint_path1, fname1)
        ep_path2 = os.path.join(endpoint_path2, fname2)

      if os.path.exists(ep_path1) and os.path.exists(ep_path2):
        ep_d1 = read_endpoint_file(ep_path1)
        ep_d2 = read_endpoint_file(ep_path2)
        show_ep_hist_2(ep_d1, ep_d2, legend1, legend2, design)

    break
  return


# Author: Deyuan Guo
if __name__ == '__main__':
  if len(sys.argv) == 2:
    file1 = sys.argv[1]
    if os.path.exists(file1) and os.path.isfile(file1):
      ep_dict = read_endpoint_file(file1)
      show_ep_hist_1(ep_dict)
  elif len(sys.argv) == 3:
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    if os.path.exists(file1) and os.path.isfile(file1):
      if os.path.exists(file2) and os.path.isfile(file2):
        ep_dict1 = read_endpoint_file(file1)
        ep_dict2 = read_endpoint_file(file2)
        show_ep_hist_2(ep_dict1, ep_dict2, 'flow1', 'flow2', 'design')
  elif len(sys.argv) == 7:
    flow1 = sys.argv[1]
    stage1 = sys.argv[2]
    legend1 = sys.argv[3]
    flow2 = sys.argv[4]
    stage2 = sys.argv[5]
    legend2 = sys.argv[6]
    if os.path.exists(flow1) and os.path.isdir(flow1) and os.path.exists(flow2) and os.path.isdir(flow2):
      if stage1 == 'icp' or stage1 == 'icc' or stage1 == 'icr' or stage1 == 'icf':
        if stage2 == 'icp' or stage2 == 'icc' or stage2 == 'icr' or stage2 == 'icf':
          traverse_flows(flow1, stage1, legend1, flow2, stage2, legend2)
  else:
    print('ICC2 PRS Endpoint Histogram Generator. Deyuan Guo <dguo@synopsys.com>')
    print('Usage:')
    print('  gen_endpoint_histogram.py <flow1> <stage1> <legend1> <flow2> <stage2> <legend2>')
    print('    - flow: path to icc2 prs flow directory')
    print('    - stage: icp|icc|icr|icf')
    print('    - legend: name of the flow shown as legend in the graph')


