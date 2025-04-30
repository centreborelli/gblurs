M=`python -c 'import gblurs;print(" ".join(gblurs.gblurs))'`
S=14.0
plambda x.png ":i 0 = :j 0 = and"|fftshift > y.npy
for S in 0.6 3.6 14.6 ; do
for i in $M; do
	python gblurs.py $i -i x.png -s $S -o ox_${i}_$S.npy
	python gblurs.py $i -i y.npy -s $S -o oy_${i}_$S.npy
done
done
