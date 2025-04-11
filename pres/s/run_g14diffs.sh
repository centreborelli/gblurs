mkdir -p t/diffs_xg14
for i in $M; do
for j in $M; do
	echo plambda t/xg14_$i.npy t/xg14_$j.npy - -o t/diffs_xg14/d_${i}_${j}.npy
done
done | parallel -j 4
