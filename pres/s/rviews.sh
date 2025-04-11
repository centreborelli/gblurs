for i in r1000_g100_*npy; do echo downsa v 4 $i \|qeasy {-,}0.01 - o/${i/npy/png} ; done|sh
for i in r1000_g3_*npy; do echo downsa v 4 $i \|qeasy {-,}0.35 - o/${i/npy/png} ; done|sh
for i in r1000_g30_*npy; do echo downsa v 4 $i \|qeasy {-,}0.035 - o/${i/npy/png} ; done|sh
