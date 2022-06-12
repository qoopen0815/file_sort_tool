# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:14:12 2022
@author: ku_sk
"""

import matplotlib.pyplot as plt
import numpy as np

from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

class KShape:
    
    def __init__(self) -> None:
        pass
    
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

    def estimate_cluster_num(self, data: np.array, random_seed: int, max_cluster: int) -> int:
        distortions = []
        for i  in range(1,max_cluster+1):
            ks = KShape(n_clusters=i, n_init=10, verbose=True, random_state=random_seed)   #クラスタリングの計算を実行
            ks.fit(data)    #ks.fitするとks.inertia_が得られる
            distortions.append(ks.inertia_)
            
        plt.plot(range(1,max_cluster+1), distortions, marker='o')
        plt.xlabel('Number of clusters')
        plt.ylabel('Distortion')
        plt.show()
    
