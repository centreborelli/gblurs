for i in $M; do
	python gblurs.py $i -i f/x.png -o t/xg14bp_$i.npy -s 14 -b periodic
done
