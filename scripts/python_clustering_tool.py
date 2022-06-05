# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:14:12 2022

@author: ku_sk
"""

import glob
import numpy as np
import os
import pandas as pd
import shutil

from tslearn.clustering import KShape
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

import matplotlib.pyplot as plt

class PythonClusteringTool:
    
    # data info
    directory = r'C:\Users\ku_sk\Documents\Python Scripts\data_clustering_tool\sample_data'
    target_col = 'data'
    skip_row = 0
    # clustering 
    cluster_num = 2
    method = 'DTW'
    
    dataset = []

    def __init__(self, setup=True):
        if setup:
            print('File Directory Path:')
            self.directory = input()
            print('Target Column Name:')
            self.target_col = input()
            print('Skip Row Num:')
            self.skip_row = int(input())
            print('Clustering Method:')
            self.method = input()
            print('Quantity of Data Type:')
            self.cluster_num = int(input())
        else:
            pass
    
    def check_file_exist(self) -> bool:
        num = len(glob.glob(self.directory + '\\*.csv'))
        if num == 0:
            return False
        else:
            return True

    def load_csv(self, path: str, skip=0) -> pd.DataFrame:
        df = pd.read_csv(path, index_col=None, header=0, skiprows=skip)
        return df

    def create_dataset(self, df_list: pd.DataFrame, target_column: str):
        
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
            return np.array(ts_list, dtype='float32')
        
        def transform_vector(ts_array: np.array) -> np.array:
            # Convert to vector
            stack_list = []
            for j in range(len(ts_array)):
                data = np.array(ts_array[j], dtype='float32')
                data = data.reshape((1, len(data))).T
                stack_list.append(data)
            #一次元配列にする
            stack_data = np.stack(stack_list, axis=0)
            return stack_data
        
        ts_array = convert_to_array(df_list, target_column)
        ts_vector = transform_vector(ts_array)
        return ts_vector

    def clustering_by_dtw(self, data: np.array, cluster: int, random_seed: int) -> list:
        km_dtw = TimeSeriesKMeans(n_clusters=cluster, random_state=random_seed, metric='dtw')
        y_pred = km_dtw.fit_predict(data.astype(np.float32))
        
        # matplotlib
        plt.figure(figsize=(16,9))
        for yi in range(cluster):
            plt.subplot(cluster, 1, 1 + yi)
            for xx in data[y_pred == yi]:
                plt.plot(xx.ravel(), 'k-', alpha=.2)
            plt.plot(km_dtw.cluster_centers_[yi].ravel(), 'r-')
            plt.title('Cluster {} (method: DTW)'.format(yi + 1))
        
        plt.tight_layout()
        plt.show()
        return y_pred

    def clustering_by_kshape(self, data: np.array, cluster: int, random_seed: int) -> list:
        ks = KShape(n_clusters=cluster, random_state=random_seed)
        # ks = KShape(n_clusters=cluster_num, n_init=10, verbose=True, random_state=random_seed)
        y_pred = ks.fit_predict(data)
        
        # matplotlib
        plt.figure(figsize=(16,9))
        for yi in range(cluster):
            plt.subplot(cluster, 1, 1 + yi)
            for xx in data[y_pred == yi]:
                plt.plot(xx.ravel(), 'k-', alpha=.2)
            plt.plot(ks.cluster_centers_[yi].ravel(), 'r-')
            plt.title('Cluster {} (method: K-Shape)'.format(yi + 1))
        
        plt.tight_layout()
        plt.show()
        return y_pred

    def estimate_cluster_num(self, data: np.array, random_seed: int, max_cluster: int):
        distortions = []
        
        #1~10クラスタまで計算 
        for i  in range(1,max_cluster+1):
            ks = KShape(n_clusters=i, n_init=10, verbose=True, random_state=random_seed)   #クラスタリングの計算を実行
            ks.fit(data)                                                        #ks.fitするとks.inertia_が得られる
            distortions.append(ks.inertia_)
            
        plt.plot(range(1,11), distortions, marker='o')
        plt.xlabel('Number of clusters')
        plt.ylabel('Distortion')
        plt.show()
    

if __name__ == '__main__':
    
    pct = PythonClusteringTool(False)
    
    # Create data set
    paths = sorted(glob.glob(pct.directory + '\\*.csv'))
    for path in paths:
        df = pct.load_csv(path, pct.skip_row)
        pct.dataset.append(df)
    pct.dataset = pct.create_dataset(pct.dataset, pct.target_col)
    
    # Ready for clustering
    seed = 0
    np.random.seed(seed)
    # Normalize to compute cross-correlation.
    pct.dataset = TimeSeriesScalerMeanVariance(mu=0.0, std=1.0).fit_transform(pct.dataset)
    
    # Clustering
    if pct.method == 'DTW':         # DTW(Dynamic Time Warping)
        result = pct.clustering_by_dtw(pct.dataset, pct.cluster_num, seed)
    elif pct.method == 'K-Shape':    # K-Shape
        result = pct.clustering_by_kshape(pct.dataset, pct.cluster_num, seed)
    
    # Move files based on clustering results.
    for index, path in enumerate(paths):
        file = path.replace(pct.directory, '')
        dirpath = {
            'from': pct.directory,
            'to':   pct.directory+'\\cluster{}'.format(result[index])
            }
        try:
            shutil.move(dirpath['from']+file, dirpath['to']+file)
        except FileNotFoundError:
            os.mkdir(dirpath['to'])
            shutil.move(dirpath['from']+file, dirpath['to']+file)
            