# -*- coding: utf-8 -*-
'''
Created on Fri Jun  3 19:02:53 2022
@author: ku_sk
TODO: Estimate the optimal number of clusters by Elbow method.
'''

import glob
import os
import shutil

import dearpygui.dearpygui as dpg
import pandas as pd
from clustering_tools.dynamic_time_warping import DynamicTimeWarping

import interface.utils

class DpgInterface(object):

    _ver = '0.0.1'

    _tool_tag = 'Tool'
    _tool_label = 'FileSortingTool'
    _tool_id = 0

    _terminate_flag = False
    _use_debug_print = False
    
    _file_list = {
        'src': [],
        'ok': [],
        'ng': []
    }
    
    _ref_data = []
    _ref_path = ''
    _dtw = DynamicTimeWarping()
    
    # 入力データ設定
    ref_file = ''
    directory_path = ''
    col_name = ''
    skip_row = 0
    
    # ソート設定
    distance_threshold = 30.0
    
    # 自動処理モード用設定
    

    def __init__(
        self,
        width=1280,
        height=720,
        use_debug_print=False
    ):
        # 各種初期化
        self._tool_id = 0
        self._use_debug_print = use_debug_print

        # ファイルダイアログ設定
        # ファイル用
        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            modal=False,
            height=int(height / 2),
            callback=self._callback_open_file,
            id='open_file',
        ):
            dpg.add_file_extension('.csv')
            dpg.add_file_extension('', color=(150, 255, 150, 255))
        # フォルダ用
        with dpg.file_dialog(
            directory_selector=True,
            show=False,
            modal=False,
            height=int(height / 2),
            callback=self._callback_open_directory,
            id='open_directory',
        ):
            pass

        # メインウィンドウ生成
        with dpg.window(
            tag=self._tool_tag + 'Window',
            label=self._tool_label,
            width=width,
            height=height,
            menubar=True,
            no_resize=True,
            no_scrollbar=True,
            on_close=self._callback_close_window,
        ):
            # メニューバー生成
            with dpg.menu_bar(label='MenuBar'):
                with dpg.menu(label='Configuration'):
                    dpg.add_menu_item(
                        tag='general_config',
                        label='General Settings',
                        callback=lambda: dpg.configure_item(
                            'general_settings',
                            show=True,
                        )
                    )
                    dpg.add_menu_item(
                        tag='sort_config',
                        label='File Sort Settings',
                        callback=lambda: dpg.configure_item(
                            'sort_settings',
                            show=True,
                        )
                    )
                    # dpg.add_menu_item(
                    #     tag='automate_config',
                    #     label='Automate Settings',
                    #     callback=lambda: dpg.configure_item(
                    #         'about_me',
                    #         show=True,
                    #     )
                    # )
                with dpg.menu(label='About'):
                    dpg.add_menu_item(
                        tag='About_Me',
                        label='Info',
                        callback=lambda: dpg.configure_item(
                            'information',
                            show=True,
                        )
                    )

            with dpg.group():
                with dpg.group(horizontal=True):
                    with dpg.child_window(label='Source Items',
                                          tag='src_items_window',
                                          width=width/2 - 10,
                                          height=height - 65):
                        dpg.add_text('Input Files:')
                        
                    with dpg.group():
                        with dpg.child_window(width=width/2 - 15,
                                            height=height/2 - 35):
                            dpg.add_text('Hit Items')
                            
                        with dpg.child_window(width=width/2 - 15,
                                            height=height/2 - 35):
                            dpg.add_text('Non Hit Items')
                            
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label='Run',
                        tag='run_button',
                        width=70,
                        callback=self._callback_push_run
                    )
                    dpg.add_progress_bar(
                        label='Progress Bar',
                        tag='progress_bar',
                        width=580,
                        default_value=0.0,
                        overlay='0%'
                    )

            ## 隠しておくウィンドウ
            with dpg.window(
                label='General Settings',
                modal=False,
                show=False,
                id='general_settings',
                no_title_bar=False,
                no_resize=True,
                pos=[52,52],
                width=500,
                height=200
            ):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Reference File:'
                        )
                        dpg.add_button(
                            label='Open',
                            callback=lambda: dpg.configure_item(
                                'open_file',
                                show=True,
                            )
                        )
                    dpg.add_text(
                        '-> ' + self.ref_file,
                        tag='show_ref_file'
                    )
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Directory Path:'
                        )
                        dpg.add_button(
                            label='Open',
                            callback=lambda: dpg.configure_item(
                                'open_directory',
                                show=True,
                            )
                        )
                    dpg.add_text(
                        '-> ' + self.directory_path,
                        tag='show_directory_path'
                    )
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Target Column Name:'
                        )
                        dpg.add_combo(
                            tag='col_list',
                            default_value=self.col_name,
                            width=100,
                            callback=lambda sender, data: setattr(self, 'col_name', data)
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Skip Row Num:'
                        )
                        dpg.add_input_int(
                            tag='skip_row',
                            default_value=self.skip_row,
                            width=100,
                            callback=lambda sender, data: setattr(self, 'skip_row', data)
                        )
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label='Save',
                        callback=self._callback_save_general_configuration
                    )
                    
            with dpg.window(
                label='Sort Settings',
                modal=False,
                show=False,
                id='sort_settings',
                no_title_bar=False,
                no_resize=True,
                pos=[52,52],
                width=500,
                height=200
            ):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Distance Threshold:'
                        )
                        dpg.add_input_float(
                            default_value=self.distance_threshold,
                            width=100,
                            callback=lambda sender, data: setattr(self, 'distance_threshold', data)
                        )
                    
            with dpg.window(
                label='Info',
                modal=True,
                show=False,
                id='information',
                no_title_bar=False,
                pos=[52,52]
            ):
                dpg.add_text(
                    'FileSortingTool is a tool for sorting CSV files \nbased on the clustering results of timeseries data.',
                )
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label='OK',
                        width=375,
                        callback=lambda: dpg.configure_item(
                            'information',
                            show=False,
                        ),
                    )

            # インポート制限事項ポップアップ
            #TODO: データ量が大きすぎたら出す
            with dpg.window(
                label='Delete Files',
                modal=True,
                show=False,
                id='import_caution',
                no_title_bar=True,
                pos=[52, 52],
            ):
                dpg.add_text(
                    'Sorry. In the current implementation, \nfile import works only before adding a node.',
                )
                dpg.add_separator()
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label='OK',
                        width=375,
                        callback=lambda: dpg.configure_item(
                            'import_caution',
                            show=False,
                        ),
                    )
                    
        dpg.set_primary_window(
            self._tool_tag + 'Window',
            True
        )

    def _callback_close_window(self, sender):
        dpg.delete_item(sender)

    def _callback_open_file(self, sender, data):
        if data['file_name'] != '.':
            # CSVファイルから読み込み
            df = pd.read_csv(
                data['file_path_name'],
                index_col=None,
                header=0, 
                skiprows=self.skip_row
            )
            self.ref_file = data['file_name']
            self._ref_path = data['file_path_name']
            # col_listを更新
            cols = list(df)
            dpg.configure_item(
                'col_list',
                items=cols,
                default_value=cols[0]
            )
            dpg.configure_item(
                'show_ref_file',
                default_value='-> ' + data['file_name']
            )
            # # データサイズが大きい場合は警告
            # dpg.configure_item('import_caution', show=True)

        if self._use_debug_print:
            print('**** _callback_open_file ****')
            print('- sender:    ' + str(sender))
            print('- data:      ' + str(data))
            print('- loaded:    ')
            print(self._ref_path)
            print()
            
    def _callback_open_directory(self, sender, data):
        if data['file_name'] != '.':
            self.directory_path = data['file_path_name']
            dpg.configure_item(
                'show_directory_path',
                default_value='-> ' + self.directory_path
            )

        if self._use_debug_print:
            print('**** _callback_open_directory ****')
            print('- sender:    ' + str(sender))
            print('- data:      ' + str(data))
            print('- loaded:    ')
            print(self.directory_path)
            print()

    def _callback_save_general_configuration(self, sender, data):
        if os.path.exists(self._ref_path):
            df = pd.read_csv(
                self._ref_path,
                index_col=None,
                header=0, 
                skiprows=self.skip_row
            )
            self._ref_data = df[self.col_name].to_list()
        dpg.configure_item(
            'general_settings',
            show=False,
        )
        
        if self._use_debug_print:
            print('**** General Configuration ****')
            print('- ref_data:       {} datas'.format(len(self._ref_data)))
            print('- directory_path: {} files'.format(self.directory_path))
            print('- col_name:       {}'.format(self.col_name))
            print('- skip_row:       {}'.format(self.skip_row))
            print()
    
    def _callback_push_run(self, sender, data):
        self._sort_files()
    
    def _sort_files(self):
        self._file_list['src'] = sorted(glob.glob(self.directory_path + '\\*.csv'))
        self._file_list['ok'].clear()
        self._file_list['ng'].clear()
        
        tmp = self._file_list['src'].copy()
        file_num = len(tmp)
        for index, file in enumerate(tmp):
            target = pd.read_csv(file)[self.col_name].to_list()       
            dist = self._dtw.get_distance(self._ref_data, target, False)
            print('{} -> dist: {}'.format(index, dist))
            if dist < self.distance_threshold:
                self._file_list['ok'].append(file)
                # interface.utils.move_file(
                #     src=file,
                #     dst=file.replace(
                #         self.directory_path,
                #         self.directory_path + '\\hits'
                #     )
                # )
            else:
                self._file_list['ng'].append(file)
                # interface.utils.move_file(
                #     src=file,
                #     dst=file.replace(
                #         self.directory_path,
                #         self.directory_path + '\\outlier'
                #     )
                # )
            self._file_list['src'].remove(file)
            progress = float((index+1)/file_num)
            dpg.configure_item(
                'progress_bar',
                default_value=progress,
                overlay='{}%'.format(progress*100)
            )
    