# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:14:12 2022
@author: ku_sk
"""

import glob
from importlib.resources import path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fastdtw import fastdtw
from sklearn.metrics import r2_score
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

class DynamicTimeWarping:
    
    def __init__(self) -> None:
        pass
    
    def get_distance(self, ref: list, data: list, plot=False):
        distance, path = fastdtw(ref, data)
        
        if plot:
            plt.plot(ref, label="ref_data")
            plt.plot(data, label="input_data")
            for ref_x, input_x in path:
                plt.plot(
                    [ref_x, input_x],
                    [ref[ref_x], data[input_x]],
                    color='gray',
                    linestyle='dotted',
                    linewidth=1
                )
            plt.legend()
            plt.show()
        
        return distance
    
    def get_sort_result(self, dataset: np.array, cluster: int,
                        seed=0, metric='dtw') -> list:
        km_dtw = TimeSeriesKMeans(n_clusters=cluster, random_state=seed, 
                                  metric=metric)
        labels = km_dtw.fit_predict(dataset)
        return (labels, km_dtw)


def main():
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


def main2():
    dtw = DynamicTimeWarping()
    paths = sorted(glob.glob('C:\\Users\\ku_ge\\Documents\\GitHub\\python_clustering_tool\\sample_data\\small_data\\*.csv'))
    ref = pd.read_csv(paths[0])['data'].to_list()
    data = pd.read_csv(paths[3])['data'].to_list()
    dist = dtw.get_distance(ref, data, True)
    print(dist)
    

if __name__ == '__main__':
    main2()
