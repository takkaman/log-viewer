
# ICC2 tcl script
# Utilities to adjust clock uncertainty
# Deyuan Guo
# Nov. 2017
# Last updated: 11/14/2017
#
# Usage:
#   source this script
#   show_clock_uncertainty                              # show summary of clock uncertainty
#   show_clock_uncertainty -verbose                     # show details of clock uncertainty
#   adjust_clock_uncertainty 0.01                       # adjust all clock uncertainty by +10ps
#   adjust_clock_uncertainty -0.01                      # adjust all clock uncertainty by -10ps (clock uncertainty is removed once it reduces to 0)
#   adjust_clock_uncertainty 0.01 -verbose              # show detailes while adjusting clock uncertainty
#   adjust_clock_uncertainty 0.01 "" [-clk|-c2c|-pin]   # adjust a specific category of clock uncertainty
#
# Note:
#   Clock uncertainty is obtained from the output of 'report_clock -skew -mode [all_modes] -sig 4 -nosplit'
#       Each (scenario,clock) may have a unique clock uncertainty
#       Each (scenario,clock pin) may have a unique clock uncertainty
#       Each (scenario,clock-to-clock pair,rr/rf/fr/ff) may have a unique clock uncertainty
#   Adjust by delta:
#       For clocks, add delta to existing values. Existing values can be 0
#       For clock-to-clock pairs and clock pins, add delta to existing values. Existing values cannot be 0
#

# Internal: Get current clock uncertainty from report_clock command
proc _get_curr_uncertainty {} {
  set orig_output_time_unit [get_user_unit -output -type time]
  set_user_unit -output -type time -value 1ns

  array unset setup_clk_uncert
  array unset hold_clk_uncert
  array unset setup_c2c_uncert
  array unset hold_c2c_uncert

  # record current uncertainty into arrays
  redirect -variable log {report_clock -skew -mode [all_modes] -sig 4 -nosplit}

  set curr_section 0
  set next_section 0
  foreach line [split $log \n] {

    # section transition
    set m1 [regexp "^-+$" $line match]
    set m2 [regexp "^\\*+$" $line match]
    if { $m1 == "1" || $m2 == "1" } {
      set curr_section $next_section
      set next_section 0
      continue
    }

    # determine next section: 1 - clock uncertainty; 2 - clock-to-clock uncertainty
    set m [regexp "^Object\\s+Delay\\s+Delay\\s+Delay\\s+Delay\\s+Uncertainty\\s+Uncertainty\\s+Clock\\s+Scenario.*$" $line match]
    if { $m == "1" } {
      set next_section 1
      continue
    }
    set m [regexp "^Clock\\s+Clock\\s+Uncertainty\\s+Uncertainty\\s+Scenario.*$" $line match]
    if { $m == "1" } {
      set next_section 2
      continue
    }

    # clock uncertainty section - including clocks and clock pins
    if { $curr_section == 1 } {
      set m [regexp "^\(\\S+\)\\s+\\S+\\s+\\S+\\s+\\S+\\s+\\S+\\s+\(\\S+\)\\s+\(\\S+\)\\s+\\S+\\s+\(\\S+\).*$" $line match clk hcu scu scn]
      if { $m == "1" } {
        if { $scu != "-" && ![ info exists setup_clk_uncert($scn,$clk) ] } {
          set setup_clk_uncert($scn,$clk) $scu
        }
        if { $hcu != "-" && ![ info exists hold_clk_uncert($scn,$clk) ] } {
          set hold_clk_uncert($scn,$clk) $hcu
        }
      }
    }

    # clock-to-clock uncertainty section
    if { $curr_section == 2 } {
      set m [regexp "^\(\\S+\)\\s+\(\\S+\)\\s+\(\\S+\)\\s+\(\\S+\)\\s+\(\\S+\)\\s+\(\\S+\)\\s+\(\\S+\).*$" $line match from_clk from_edge to_clk to_edge hcu scu scn]
      if { $m == "1" } {
        if { $from_edge == "(r)"} { set from_edge r }
        if { $from_edge == "(f)"} { set from_edge f }
        if { $to_edge == "(r)" } { set to_edge r }
        if { $to_edge == "(f)" } { set to_edge f }
        if { $scu != "-" && ![ info exists setup_c2c_uncert($scn,$from_clk,$from_edge,$to_clk,$to_edge) ] } {
          set setup_c2c_uncert($scn,$from_clk,$from_edge,$to_clk,$to_edge) $scu
        }
        if { $hcu != "-" && ![ info exists hold_c2c_uncert($scn,$from_clk,$from_edge,$to_clk,$to_edge) ] } {
          set hold_c2c_uncert($scn,$from_clk,$from_edge,$to_clk,$to_edge) $hcu
        }
      }

    }
  }

  set_user_unit -output -type time -value $orig_output_time_unit
  return [list [array get setup_clk_uncert] [array get hold_clk_uncert] [array get setup_c2c_uncert] [array get hold_c2c_uncert]]
}
define_proc_attributes -hide_body -hidden -dont_abbrev _get_curr_uncertainty


# Internal: Show stats
proc _show_uncertainty_stats {s_clk h_clk s_c2c h_c2c} {
  echo "Summary:"

  array set setup_clk_uncert $s_clk
  array set hold_clk_uncert $h_clk
  array set setup_c2c_uncert $s_c2c
  array set hold_c2c_uncert $h_c2c

  set cnt_clk_setup 0
  set min_clk_setup 0
  set max_clk_setup 0
  set tot_clk_setup 0
  set avg_clk_setup 0

  set cnt_clk_hold 0
  set min_clk_hold 0
  set max_clk_hold 0
  set tot_clk_hold 0
  set avg_clk_hold 0

  set cnt_c2c_setup 0
  set min_c2c_setup 0
  set max_c2c_setup 0
  set tot_c2c_setup 0
  set avg_c2c_setup 0

  set cnt_c2c_hold 0
  set min_c2c_hold 0
  set max_c2c_hold 0
  set tot_c2c_hold 0
  set avg_c2c_hold 0

  # all uncertainty values are larger than 0
  foreach {key value} [array get setup_clk_uncert] {
    set cnt_clk_setup [expr $cnt_clk_setup + 1]
    if { [expr $min_clk_setup == 0] || [expr $min_clk_setup > $value] } { set min_clk_setup $value }
    if { [expr $max_clk_setup == 0] || [expr $max_clk_setup < $value] } { set max_clk_setup $value }
    set tot_clk_setup [expr $tot_clk_setup + $value]
  }
  if { [expr $cnt_clk_setup != 0] } { set avg_clk_setup [expr $tot_clk_setup / $cnt_clk_setup] }

  foreach {key value} [array get hold_clk_uncert] {
    set cnt_clk_hold [expr $cnt_clk_hold + 1]
    if { [expr $min_clk_hold == 0] || [expr $min_clk_hold > $value] } { set min_clk_hold $value }
    if { [expr $max_clk_hold == 0] || [expr $max_clk_hold < $value] } { set max_clk_hold $value }
    set tot_clk_hold [expr $tot_clk_hold + $value]
  }
  if { [expr $cnt_clk_hold != 0] } { set avg_clk_hold [expr $tot_clk_hold / $cnt_clk_hold] }

  foreach {key value} [array get setup_c2c_uncert] {
    set cnt_c2c_setup [expr $cnt_c2c_setup + 1]
    if { [expr $min_c2c_setup == 0] || [expr $min_c2c_setup > $value] } { set min_c2c_setup $value }
    if { [expr $max_c2c_setup == 0] || [expr $max_c2c_setup < $value] } { set max_c2c_setup $value }
    set tot_c2c_setup [expr $tot_c2c_setup + $value]
  }
  if { [expr $cnt_c2c_setup != 0] } { set avg_c2c_setup [expr $tot_c2c_setup / $cnt_c2c_setup] }

  foreach {key value} [array get hold_c2c_uncert] {
    set cnt_c2c_hold [expr $cnt_c2c_hold + 1]
    if { [expr $min_c2c_hold == 0] || [expr $min_c2c_hold > $value] } { set min_c2c_hold $value }
    if { [expr $max_c2c_hold == 0] || [expr $max_c2c_hold < $value] } { set max_c2c_hold $value }
    set tot_c2c_hold [expr $tot_c2c_hold + $value]
  }
  if { [expr $cnt_c2c_hold != 0] } { set avg_c2c_hold [expr $tot_c2c_hold / $cnt_c2c_hold] }

  # count clocks and clock pins
  set cnt_setup_clk_only 0
  set cnt_hold_clk_only 0
  set orig_scn [current_scenario]
  foreach_in_collection scn_obj [ all_scenarios ] {
    set scn [get_attribute $scn_obj full_name]
    current_scenario $scn

    set num_clocks [sizeof_collection [all_clocks]]
    echo "  $num_clocks clocks in scenario $scn"

    foreach_in_collection clk_obj [ all_clocks ] {
      set clk [get_attribute $clk_obj full_name]
      if { [ info exists setup_clk_uncert($scn,$clk) ] } {
        set cnt_setup_clk_only [expr $cnt_setup_clk_only + 1]
      }
      if { [ info exists hold_clk_uncert($scn,$clk) ] } {
        set cnt_hold_clk_only [expr $cnt_hold_clk_only + 1]
      }
    }
  }
  current_scenario $orig_scn
  set cnt_setup_clk_pin [expr $cnt_clk_setup - $cnt_setup_clk_only]
  set cnt_hold_clk_pin [expr $cnt_clk_hold - $cnt_hold_clk_only]

  echo "  Setup clk uncertainty: cnt=$cnt_clk_setup (clk=$cnt_setup_clk_only, pin=$cnt_setup_clk_pin), min=$min_clk_setup, max=$max_clk_setup, avg=$avg_clk_setup"
  echo "  Hold  clk uncertainty: cnt=$cnt_clk_hold (clk=$cnt_hold_clk_only, pin=$cnt_hold_clk_pin), min=$min_clk_hold, max=$max_clk_hold, avg=$avg_clk_hold"
  echo "  Setup c2c uncertainty: cnt=$cnt_c2c_setup, min=$min_c2c_setup, max=$max_c2c_setup, avg=$avg_c2c_setup"
  echo "  Hold  c2c uncertainty: cnt=$cnt_c2c_hold, min=$min_c2c_hold, max=$max_c2c_hold, avg=$avg_c2c_hold"

}
define_proc_attributes -hide_body -hidden -dont_abbrev _show_uncertainty_stats


# Show current clock uncertainty
proc show_clock_uncertainty { {opt ""} } {
  echo "Time unit: ns"
  set rpt [ _get_curr_uncertainty ]
  array set setup_clk_uncert [lindex $rpt 0]
  array set hold_clk_uncert [lindex $rpt 1]
  array set setup_c2c_uncert [lindex $rpt 2]
  array set hold_c2c_uncert [lindex $rpt 3]
  if { $opt == "-verbose" } {
    redirect -variable s_clk { parray setup_clk_uncert }
    redirect -variable h_clk { parray hold_clk_uncert }
    redirect -variable s_c2c { parray setup_c2c_uncert }
    redirect -variable h_c2c { parray hold_c2c_uncert }
    echo $s_clk
    echo $h_clk
    echo $s_c2c
    echo $h_c2c
  }
  _show_uncertainty_stats [array get setup_clk_uncert] [array get hold_clk_uncert] [array get setup_c2c_uncert] [array get hold_c2c_uncert]
}


# Adjust clock uncertainty by delta for all scenarios, clocks and clock-to-clock pairs
proc adjust_clock_uncertainty { delta {opt1 ""} {opt2 ""} } {

  echo ""
  echo "========================================"
  echo "Adjust Clock Uncertainty by $delta ns"
  echo "========================================"
  echo "* Before:"
  echo "Time unit: ns"
  set rpt [ _get_curr_uncertainty ]
  array set setup_clk_uncert [lindex $rpt 0]
  array set hold_clk_uncert [lindex $rpt 1]
  array set setup_c2c_uncert [lindex $rpt 2]
  array set hold_c2c_uncert [lindex $rpt 3]
  if { $opt1 == "-verbose" } {
    redirect -variable s_clk { parray setup_clk_uncert }
    redirect -variable h_clk { parray hold_clk_uncert }
    redirect -variable s_c2c { parray setup_c2c_uncert }
    redirect -variable h_c2c { parray hold_c2c_uncert }
    echo $s_clk
    echo $h_clk
    echo $s_c2c
    echo $h_c2c
  }
  _show_uncertainty_stats [array get setup_clk_uncert] [array get hold_clk_uncert] [array get setup_c2c_uncert] [array get hold_c2c_uncert]

  echo "----------"
  echo "* Adjust:"
  set orig_input_time_unit [get_user_unit -input -type time]
  set_user_unit -input -type time -value 1ns
  set orig_scn [current_scenario]

  # adjust uncertainty for all clocks by delta
  set cnt_clk 0
  if { $opt2 != "-c2c" && $opt2 != "-pin" } {
    foreach_in_collection scn_obj [ all_scenarios ] {
      set scn [get_attribute $scn_obj full_name]
      current_scenario $scn

      # clock uncertainty
      foreach_in_collection clk_obj [ all_clocks ] {
        set clk [get_attribute $clk_obj full_name]

        if { [ info exists setup_clk_uncert($scn,$clk) ] } {
          set old_scu $setup_clk_uncert($scn,$clk)
          set new_scu [expr $old_scu + $delta]
        } else {
          set old_scu "None"
          set new_scu $delta
        }
        if { [ info exists hold_clk_uncert($scn,$clk) ] } {
          set old_hcu $hold_clk_uncert($scn,$clk)
          set new_hcu [expr $old_hcu + $delta]
        } else {
          set old_hcu "None"
          set new_hcu $delta
        }
        if { [expr $new_scu <= 0.0] } { set new_scu "None" }
        if { [expr $new_hcu <= 0.0] } { set new_hcu "None" }

        if { $opt1 == "-verbose" } {
          echo "setup $old_scu -> $new_scu, hold $old_hcu -> $new_hcu : $clk : $scn"
        }

        if { $new_scu == "None" } {
          if { $old_scu != "None"} {
            remove_clock_uncertainty -setup -scenario $scn $clk
          }
        } else {
          set_clock_uncertainty -setup $new_scu -scenario $scn $clk
        }
        if { $new_hcu == "None" } {
          if { $old_hcu != "None" } {
            remove_clock_uncertainty -hold -scenario $scn $clk
          }
        } else {
          set_clock_uncertainty -hold $new_hcu -scenario $scn $clk
        }

        set cnt_clk [expr $cnt_clk + 1]
      }
    }
  }
  echo "  $cnt_clk adjusted clocks"

  # adjust uncertainty for clock-to-clock pairs by delta, only if uncertainty exists
  set cnt_c2c 0
  set cnt_c2c_adjusted 0
  if { $opt2 != "-clk" && $opt2 != "-pin" } {
    foreach_in_collection scn_obj [ all_scenarios ] {
      set scn [get_attribute $scn_obj full_name]
      current_scenario $scn

      # clock-to-clock uncertainty - n-square behavior
      foreach_in_collection clk_obj1 [ all_clocks ] {
        set clk1 [get_attribute $clk_obj1 full_name]
        foreach_in_collection clk_obj2 [ all_clocks ] {
          set clk2 [get_attribute $clk_obj2 full_name]

          # setup
          if { [ info exists setup_c2c_uncert($scn,$clk1,r,$clk2,r) ] } {
            set old_scu_rr $setup_c2c_uncert($scn,$clk1,r,$clk2,r)
            set new_scu_rr [expr $old_scu_rr + $delta]
          } else {
            set old_scu_rr "None"
            set new_scu_rr 0
          }
          if { [ info exists setup_c2c_uncert($scn,$clk1,r,$clk2,f) ] } {
            set old_scu_rf $setup_c2c_uncert($scn,$clk1,r,$clk2,f)
            set new_scu_rf [expr $old_scu_rf + $delta]
          } else {
            set old_scu_rf "None"
            set new_scu_rf 0
          }
          if { [ info exists setup_c2c_uncert($scn,$clk1,f,$clk2,r) ] } {
            set old_scu_fr $setup_c2c_uncert($scn,$clk1,f,$clk2,r)
            set new_scu_fr [expr $old_scu_fr + $delta]
          } else {
            set old_scu_fr "None"
            set new_scu_fr 0
          }
          if { [ info exists setup_c2c_uncert($scn,$clk1,f,$clk2,f) ] } {
            set old_scu_ff $setup_c2c_uncert($scn,$clk1,f,$clk2,f)
            set new_scu_ff [expr $old_scu_ff + $delta]
          } else {
            set old_scu_ff "None"
            set new_scu_ff 0
          }

          # hold
          if { [ info exists hold_c2c_uncert($scn,$clk1,r,$clk2,r) ] } {
            set old_hcu_rr $hold_c2c_uncert($scn,$clk1,r,$clk2,r)
            set new_hcu_rr [expr $old_hcu_rr + $delta]
          } else {
            set old_hcu_rr "None"
            set new_hcu_rr 0
          }
          if { [ info exists hold_c2c_uncert($scn,$clk1,r,$clk2,f) ] } {
            set old_hcu_rf $hold_c2c_uncert($scn,$clk1,r,$clk2,f)
            set new_hcu_rf [expr $old_hcu_rf + $delta]
          } else {
            set old_hcu_rf "None"
            set new_hcu_rf 0
          }
          if { [ info exists hold_c2c_uncert($scn,$clk1,f,$clk2,r) ] } {
            set old_hcu_fr $hold_c2c_uncert($scn,$clk1,f,$clk2,r)
            set new_hcu_fr [expr $old_hcu_fr + $delta]
          } else {
            set old_hcu_fr "None"
            set new_hcu_fr 0
          }
          if { [ info exists hold_c2c_uncert($scn,$clk1,f,$clk2,f) ] } {
            set old_hcu_ff $hold_c2c_uncert($scn,$clk1,f,$clk2,f)
            set new_hcu_ff [expr $old_hcu_ff + $delta]
          } else {
            set old_hcu_ff "None"
            set new_hcu_ff 0
          }

          if { [expr $new_scu_rr <= 0.0] } { set new_scu_rr "None" }
          if { [expr $new_scu_rf <= 0.0] } { set new_scu_rf "None" }
          if { [expr $new_scu_fr <= 0.0] } { set new_scu_fr "None" }
          if { [expr $new_scu_ff <= 0.0] } { set new_scu_ff "None" }
          if { [expr $new_hcu_rr <= 0.0] } { set new_hcu_rr "None" }
          if { [expr $new_hcu_rf <= 0.0] } { set new_hcu_rf "None" }
          if { [expr $new_hcu_fr <= 0.0] } { set new_hcu_fr "None" }
          if { [expr $new_hcu_ff <= 0.0] } { set new_hcu_ff "None" }

          if { $opt1 == "-verbose" } {
            echo "setup rr $old_scu_rr -> $new_scu_rr, rf $old_scu_rf -> $new_scu_rf, fr $old_scu_fr -> $new_scu_fr, ff $old_scu_ff -> $new_scu_ff : $clk1 -> $clk2: $scn"
            echo "hold rr $old_hcu_rr -> $new_hcu_rr, rf $old_hcu_rf -> $new_hcu_rf, fr $old_hcu_fr -> $new_hcu_fr, ff $old_hcu_ff -> $new_hcu_ff : $clk1 -> $clk2: $scn"
          }

          # setup
          if { $new_scu_rr == "None" } {
            if { $old_scu_rr != "None" } {
              remove_clock_uncertainty -setup -scenario $scn -rise_from $clk1 -rise_to $clk2
            }
          } else {
            set_clock_uncertainty -setup -scenario $scn -rise_from $clk1 -rise_to $clk2 $new_scu_rr
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }
          if { $new_scu_rf == "None" } {
            if { $old_scu_rf != "None" } {
              remove_clock_uncertainty -setup -scenario $scn -rise_from $clk1 -fall_to $clk2
            }
          } else {
            set_clock_uncertainty -setup -scenario $scn -rise_from $clk1 -fall_to $clk2 $new_scu_rf
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }
          if { $new_scu_fr == "None" } {
            if { $old_scu_fr != "None" } {
              remove_clock_uncertainty -setup -scenario $scn -fall_from $clk1 -rise_to $clk2
            }
          } else {
            set_clock_uncertainty -setup -scenario $scn -fall_from $clk1 -rise_to $clk2 $new_scu_fr
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }
          if { $new_scu_ff == "None" } {
            if { $old_scu_ff != "None" } {
              remove_clock_uncertainty -setup -scenario $scn -fall_from $clk1 -fall_to $clk2
            }
          } else {
            set_clock_uncertainty -setup -scenario $scn -fall_from $clk1 -fall_to $clk2 $new_scu_ff
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }

          # hold
          if { $new_hcu_rr == "None" } {
            if { $old_hcu_rr != "None" } {
              remove_clock_uncertainty -hold -scenario $scn -rise_from $clk1 -rise_to $clk2
            }
          } else {
            set_clock_uncertainty -hold -scenario $scn -rise_from $clk1 -rise_to $clk2 $new_hcu_rr
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }
          if { $new_hcu_rf == "None" } {
            if { $old_hcu_rf != "None" } {
              remove_clock_uncertainty -hold -scenario $scn -rise_from $clk1 -fall_to $clk2
            }
          } else {
            set_clock_uncertainty -hold -scenario $scn -rise_from $clk1 -fall_to $clk2 $new_hcu_rf
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }
          if { $new_hcu_fr == "None" } {
            if { $old_hcu_fr != "None" } {
              remove_clock_uncertainty -hold -scenario $scn -fall_from $clk1 -rise_to $clk2
            }
          } else {
            set_clock_uncertainty -hold -scenario $scn -fall_from $clk1 -rise_to $clk2 $new_hcu_fr
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }
          if { $new_hcu_ff == "None" } {
            if { $old_hcu_ff != "None" } {
              remove_clock_uncertainty -hold -scenario $scn -fall_from $clk1 -fall_to $clk2
            }
          } else {
            set_clock_uncertainty -hold -scenario $scn -fall_from $clk1 -fall_to $clk2 $new_hcu_ff
            set cnt_c2c_adjusted [expr $cnt_c2c_adjusted + 1]
          }

          set cnt_c2c [expr $cnt_c2c + 1]
        }
      }
    }
  }
  echo "  $cnt_c2c_adjusted adjusted clock-to-clock pairs ([expr $cnt_c2c * 4] possible pairs for setup/hold and rr/rf/fr/ff)"

  # adjust uncertainty for clock pins by delta, only if uncertainty exists
  # remove clocks from arrays and keep clock pins only
  foreach_in_collection scn_obj [ all_scenarios ] {
    set scn [get_attribute $scn_obj full_name]
    current_scenario $scn
    foreach_in_collection clk_obj [ all_clocks ] {
      set clk [get_attribute $clk_obj full_name]
      if { [ info exists setup_clk_uncert($scn,$clk) ] } {
        unset setup_clk_uncert($scn,$clk)
      }
      if { [ info exists hold_clk_uncert($scn,$clk) ] } {
        unset hold_clk_uncert($scn,$clk)
      }
    }
  }
  # adjust remaining items
  set cnt_pin 0
  if { $opt2 != "-clk" && $opt2 != "-c2c" } {
    # setup
    foreach {key value} [array get setup_clk_uncert] {
      set scn [lindex [split $key {,}] 0]
      set pin [lindex [split $key {,}] 1]
      set old_scu $value
      set new_scu [expr $old_scu + $delta]
      if { [expr $new_scu <= 0.0] } { set new_scu "None" }
      if { $opt1 == "-verbose" } {
        echo "setup uncertainty $old_scu -> $new_scu : PIN $pin : $scn"
      }
      if { $new_scu == "None" } {
        remove_clock_uncertainty -setup -scenario $scn $pin
      } else {
        set_clock_uncertainty -setup $new_scu -scenario $scn $pin
      }
      set cnt_pin [expr $cnt_pin + 1]
    }
    # hold
    foreach {key value} [array get hold_clk_uncert] {
      set scn [lindex [split $key {,}] 0]
      set pin [lindex [split $key {,}] 1]
      set old_hcu $value
      set new_hcu [expr $old_hcu + $delta]
      if { [expr $new_hcu <= 0.0] } { set new_hcu "None" }
      if { $opt1 == "-verbose" } {
        echo "hold uncertainty $old_hcu -> $new_hcu : PIN $pin : $scn"
      }
      if { $new_hcu == "None" } {
        remove_clock_uncertainty -hold -scenario $scn $pin
      } else {
        set_clock_uncertainty -hold $new_hcu -scenario $scn $pin
      }
      set cnt_pin [expr $cnt_pin + 1]
    }
  }
  echo "  $cnt_pin adjusted clock pins"

  current_scenario $orig_scn
  set_user_unit -input -type time -value $orig_input_time_unit

  echo "----------"
  echo "* After:"
  show_clock_uncertainty $opt1
  echo ""
}


