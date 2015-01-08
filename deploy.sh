#!/bin/bash
rsync -avz modules 192.168.1.2:/srvdata/ipython/data/notebooks/AboutSPDY/
rsync -avz data 192.168.1.2:/srvdata/ipython/data/notebooks/AboutSPDY/
rsync -avz 192.168.1.2:/srvdata/ipython/data/notebooks/AboutSPDY/WhatDifferenceSPDYMakes.ipynb .
rsync -avz 192.168.1.2:/srvdata/ipython/data/notebooks/AboutSPDY/ExploreHarFiles.ipynb .
