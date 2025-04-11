plambda zero:1000x1000 randg -o r1000.npy
plambda zero:4000x4000 randg -o r4000.npy
rm -f stats_r1000_g3.txt; for i in $M; do /usr/bin/time -f "$i\t%e" -o stats_1000_g3.txt -a python gblurs.py $i -i r1000.npy -o r1000_g3_$i.npy -s 3 ; done
rm -f stats_r4000_g3.txt; for i in $M; do /usr/bin/time -f "$i\t%e" -o stats_4000_g3.txt -a python gblurs.py $i -i r4000.npy -o r4000_g3_$i.npy -s 3 ; done
rm -f stats_r1000_g30.txt; for i in $M; do /usr/bin/time -f "$i\t%e" -o stats_1000_g30.txt -a python gblurs.py $i -i r1000.npy -o r1000_g30_$i.npy -s 30 ; done
