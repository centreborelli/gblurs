#mkdir -p t/diffs_xg14bp
#for i in $M; do
#for j in $M; do
#	echo plambda t/xg14bp_$i.npy t/xg14bp_$j.npy - -o t/diffs_xg14bp/d_${i}_${j}.npy
#done
#done | parallel -j 4

D=t/diffs_xg14bp
for j in borelli torch opencv; do
	for i in $D/d_torch_*npy; do
		qauto -p 0 -i $i | downsa v 2 - ${i/npy/png}
	done
	cp $D/d_${j}_*png o
done
