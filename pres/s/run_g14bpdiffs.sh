mkdir -p t/diffs_xg14bp
for i in $M; do
for j in $M; do
	echo plambda t/xg14bp_$i.npy t/xg14bp_$j.npy - -o t/diffs_xg14bp/d_${i}_${j}.npy
done
done | parallel -j 4
