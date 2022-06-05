![messageImage_1654395019679](https://user-images.githubusercontent.com/26988372/172039328-ac3a83a1-4783-4481-b53a-a0ef0576bae6.jpg)

## Overview
Py-CT(Python Clustering Tool)は時系列データのクラスタリングツールです。  
フォルダ内の時系列データ（.csv）をクラスタリング結果に基づいて自動分別するツールを目指しています。

Py-CT (Python Clustering Tool) is a time series data clustering tool.  
I'm aiming for a tool that automatically sorts time-series data (.csv) in folders based on clustering results.

## Features

### Clustering method

時系列データのクラスタリング手法として下記２つを実装しています。

1. [DTW (Dynamic Time Warping)](https://zenn.dev/kinonotofu/articles/a7cb8038bb2433#dynamic-time-warping%EF%BC%88dtw%E3%80%81%E5%8B%95%E7%9A%84%E6%99%82%E9%96%93%E4%BC%B8%E7%B8%AE%E6%B3%95%EF%BC%89)
2. [K-Shape](https://tslearn.readthedocs.io/en/stable/auto_examples/clustering/plot_kshape.html?highlight=KShape)

### Estimate number of cluster

クラスタ数がいくつあるのかわからないときに推定してくれる手法として[エルボー法](https://en.wikipedia.org/wiki/Elbow_method_(clustering))を実装しています。

### Results for Sample Data
- [small_data](https://github.com/qoopen0815/python_clustering_tool/tree/main/sample_data/small_data)
<img src="https://user-images.githubusercontent.com/26988372/172048017-8c19fe3d-7e52-4272-b542-249a902d0ab1.png" width="50%"/>

## Reference

- [telearnを使って気象データをクラスタリングしてみる](https://zenn.dev/kinonotofu/articles/a7cb8038bb2433#dynamic-time-warping%EF%BC%88dtw%E3%80%81%E5%8B%95%E7%9A%84%E6%99%82%E9%96%93%E4%BC%B8%E7%B8%AE%E6%B3%95%EF%BC%89)
- [Pythonの機械学習ライブラリtslearnを使った時系列データのクラスタリング](https://blog.brains-tech.co.jp/tslearn-time-series-clustering)
