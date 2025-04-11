 (echo 18 18 1 1;cat t/diffs_xg14/summary.txt|cut -d' ' -f2)|ntiply 20|plambda "log dup dup rgb"|qeasy -16 2.5|fontu puts 10x20 0 0 "`echo $M|sed 's/ /\\n/g'`" -c h0h |ntiply 4 - summary_bdef.png
(echo 18 18 1 1;cat t/diffs_xg14bp/summary.txt|cut -d' ' -f2)|ntiply 20|plambda "log dup dup rgb"|qeasy -16 2.5|fontu puts 10x20 0 0 "`echo $M|sed 's/ /\\n/g'`" -c h0h |ntiply 4 - summary_bp.png
