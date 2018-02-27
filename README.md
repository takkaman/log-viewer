# log-viewer
extract log info and well compare/display python utility

Print out help message:
icc2_log_comparator.csh

Compare setup timing and DRC between two logs: 
icc2_log_comparator.csh <log1> <log2>

Compare at most two of the following QoR categories (does not support more than 2 due to window width):
-s, -setup    compare (S)etup timing (default)
-h, -hold     compare (H)old timing
-a, -area     compare (A)rea and inst count
-d, -drc      compare (D)RC (default)
-b, -buf      compare (B)uffer and inverter count
-p, -power    compare (P)ower: leakage and lvth
-r, -runtime  compare (R)untime and peak memory
