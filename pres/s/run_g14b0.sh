for i in $M; do
	python gblurs.py $i -i f/x.png -o t/xg14b0_$i.npy -s 14 -b zero
done
