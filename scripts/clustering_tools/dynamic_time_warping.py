# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:14:12 2022
@author: ku_sk
"""

import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

class DynamicTimeWarping:
    
    def __init__(self) -> None:
        pass
    
    def sort_by_dtw(self, data: np.array, cluster: int, random_seed: int) -> list:
        km_dtw = TimeSeriesKMeans(n_clusters=cluster, random_state=random_seed, metric='dtw')
        labels = km_dtw.fit_predict(data)
        return (labels, km_dtw)
    
    def sort_by_softdtw(self, data: np.array, cluster: int, random_seed: int) -> list:
        km_softdtw = TimeSeriesKMeans(n_clusters=cluster, random_state=random_seed, metric='softdtw')
        labels = km_softdtw.fit_predict(data)
        return (labels, km_softdtw)

if __name__ == '__main__':
    
    dtw = DynamicTimeWarping()
    
    # Create data set
    paths = sorted(glob.glob('C:\\Users\\ku_ge\\Documents\\GitHub\\python_clustering_tool\\sample_data\\small_data\\*.csv'))
    dataset = []
    for path in paths:
        df = pd.read_csv(path)
        dataset.append(df)
    
    def convert_to_array(dfs: list, col:str) -> np.array:
        # Convert from DataFrame list to a 2-dimensional list
        ts_list = []
        for i, df in enumerate(dfs):
            ts_list.append(df[col].values.tolist()[:])
        # Align the number of data
        len_max = 0
        for ts in ts_list:
            if len(ts) > len_max:
                len_max = len(ts)
        for i, ts in enumerate(ts_list):
            len_add = len_max - len(ts)
            ts_list[i] = ts + [ts[-1]] * len_add   # Fill in missing elements with last value.
        return np.array(ts_list)
    
    def transform_vector(ts_array: np.array) -> np.array:
        # Convert to vector
        stack_list = []
        for j in range(len(ts_array)):
            data = np.array(ts_array[j])
            data = data.reshape((1, len(data))).T
            stack_list.append(data)
        #一次元配列にする
        stack_data = np.stack(stack_list, axis=0)
        return stack_data
    
    dataset = convert_to_array(dataset, 'data')
    dataset = transform_vector(dataset)
    
    # Ready for clustering
    seed = 0
    np.random.seed(seed)
    # Normalize to compute cross-correlation.
    dataset = TimeSeriesScalerMeanVariance(mu=0.0, std=1.0).fit_transform(dataset)
    result = dtw.sort_by_dtw(dataset, 2, seed)
    print('end')
    
