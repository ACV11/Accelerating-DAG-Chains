# Accelerating-DAG-Chains
This repository attempts to reproduce the tangle tip selection and random walk, and parallelise it. 

## Dependencies
* Numpy
* Matplotlib
* PyMP
* Numba
* Networkx

## Installation
```
pip install numpy
pip install matplotlib
pip install pymp-pypi
pip install numba
pip install networkx
```

## Execution steps

* To check the plots for transcations less than 20000, we have to execute test_parallel_1000.py
```
python3 test_parallel_1000.py
```
* To check the plots for transaction count above 20000, we have to execute test_parallel_20000.py
```
python3 test_parallel_20000.py
```
