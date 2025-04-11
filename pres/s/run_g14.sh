for i in $M; do
	python gblurs.py $i -i f/x.png -o t/xg14_$i.npy -s 14
done
