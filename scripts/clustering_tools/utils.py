# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:14:12 2022

@author: ku_sk
"""

import pandas as pd
from typing import Tuple
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

def align_dataset_length(dataset: list) -> Tuple:
    len_max = 0
    for data in dataset:
        if len(data) > len_max:
            len_max = len(data)
    for i, data in enumerate(dataset):
        len_add = len_max - len(data)
        dataset[i] = data + [data[-1]] * len_add
    pass
