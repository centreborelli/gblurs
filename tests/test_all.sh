M=`python -c 'import gblurs;print(" ".join(gblurs.gblurs))'`
S=14.0
for i in $M; do
	python gblurs.py $i -i x.png -s 7.77 -o ox_${i}_$S.npy
done
