D=t/diffs_xg14bp
for i in $M; do
for j in $M; do
	f=$D/d_${i}_${j}.npy
	imprintf "%e %r %v %i %m %a $f\n" $f
done
done > $D/summary.txt
