for i in $M; do
	echo python gblurs.py $i -i f/x.png -s 3 -o o/g_3_$i.npy
	echo python gblurs.py $i -i f/x.png -s 4 -o o/g_4_$i.npy
	echo python gblurs.py $i -i f/x.png -s 5 -o o/g_5_$i.npy
	echo python gblurs.py $i -i f/x.png -s 12 -o o/g_12_$i.npy
	echo python gblurs.py $i -i f/x.png -s 13 -o o/g_13_$i.npy
done | parallel -j 4

for i in $M; do
	echo python gblurs.py $i -i o/g_3_$i.npy -s 4 -o o/g_3_4_$i.npy
	echo python gblurs.py $i -i o/g_5_$i.npy -s 12 -o o/g_5_12_$i.npy
done | parallel -j 4

for i in $M; do
	echo plambda o/g_3_4_$i.npy o/g_5_$i.npy - -o o/gd_3_4_5_$i.npy
	echo plambda o/g_5_12_$i.npy o/g_13_$i.npy - -o o/gd_5_12_13_$i.npy
done | parallel -j 4

for i in o/gd*npy; do
	echo qeasy {-,}0.007 $i \|downsa v 2 - ${i/npy/png}
done | parallel -j 4
