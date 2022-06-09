# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:14:12 2022

@author: ku_sk
"""

import os
import shutil

def move_file(src: str, dst:str):
    try:
        shutil.move(src, dst)
    except FileNotFoundError:
        os.mkdir(dst)
        shutil.move(src, dst)
