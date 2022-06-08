# -*- coding: utf-8 -*-
'''
Created on Fri Jun  3 19:02:53 2022
@author: ku_sk
TODO: Estimate the optimal number of clusters by Elbow method.
'''

import dearpygui.dearpygui as dpg
import glob
import pandas as pd

from collections import OrderedDict

import clustering_tools.python_clustering_tool as pyct

class FileSortUI(object):

    _ver = '0.0.1'

    _tool_tag = 'Tool'
    _tool_label = 'FileSortingTool'
    _tool_id = 0

    _terminate_flag = False
    _use_debug_print = False
    
    # file import
    ref_data = pd.DataFrame
    directory_path = str
    col_name = ''
    skip_row = 0

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
                on_close=self._callback_close_window,
        ):
            # メニューバー生成
            with dpg.menu_bar(label='MenuBar'):
                with dpg.menu(label='Configuration'):
                    dpg.add_menu_item(
                        tag='general_config',
                        label='General',
                        callback=lambda: dpg.configure_item(
                            'general_settings',
                            show=True,
                        )
                    )
                    dpg.add_menu_item(
                        tag='sort_config',
                        label='SortMethod',
                        callback=lambda: dpg.configure_item(
                            'sort_settings',
                            show=True,
                        )
                    )
                    dpg.add_menu_item(
                        tag='automate_config',
                        label='Automate',
                        callback=lambda: dpg.configure_item(
                            'about_me',
                            show=True,
                        )
                    )
                with dpg.menu(label='About'):
                    dpg.add_menu_item(
                        tag='About_Me',
                        label='Info',
                        callback=lambda: dpg.configure_item(
                            'information',
                            show=True,
                        )
                    )
 
            dpg.add_button(label='Run', tag='run_button')

            with dpg.window(
                label='General Settings',
                modal=False,
                show=False,
                id='general_settings',
                no_title_bar=False,
                pos=[52,52],
                width=500,
                height=200,
                no_resize=True
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
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Target Column Name:'
                        )
                        dpg.add_combo(
                            tag='col_list',
                            default_value='',
                            width=100,
                            callback=lambda sender, data: setattr(self, 'col_name', data)
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Skip Row Num:'
                        )
                        dpg.add_input_int(
                            default_value=0,
                            width=100,
                            callback=lambda sender, data: setattr(self, 'skip_row', data)
                        )
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label='Save',
                        callback=self._callback_save_general_configuration
                    )
                    
            with dpg.window(
                label='Sort Method Settings',
                modal=True,
                show=False,
                id='sort_settings',
                no_title_bar=False,
                pos=[52,52]
            ):
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Clustering Method:'
                        )
                        dpg.add_combo(
                            ('DynamicTimeWarping', 'K-Shape'),
                            default_value='DynamicTimeWarping',
                            width=100
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
                            'about_me',
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
                    
        dpg.set_primary_window(self._tool_tag + 'Window', True)

    def _callback_close_window(self, sender):
        dpg.delete_item(sender)

    def _callback_open_file(self, sender, data):
        if data['file_name'] != '.':
            # CSVファイルから読み込み
            df = pd.read_csv(
                data['file_path_name'],
                skiprows=self.skip_row
            )
            self.ref_data = df
            #　col_listを更新
            cols = list(self.ref_data)
            dpg.configure_item(
                'col_list',
                items=cols,
                default_value=cols[0]
            )
            # # データサイズが大きい場合は警告
            # dpg.configure_item('import_caution', show=True)

        if self._use_debug_print:
            print('**** _callback_open_file ****')
            print('- sender:    ' + str(sender))
            print('- data:      ' + str(data))
            print('- loaded:    ')
            print(self.ref_data.describe())
            print()
            
    def _callback_open_directory(self, sender, data):
        if data['file_name'] != '.':
            self.directory_path = data['file_path_name']

        if self._use_debug_print:
            print('**** _callback_open_directory ****')
            print('- sender:    ' + str(sender))
            print('- data:      ' + str(data))
            print('- loaded:    ')
            print(self.directory_path)
            print()

    def _callback_save_general_configuration(self):
        dpg.configure_item(
            'general_settings',
            show=False,
        )
        
        if self._use_debug_print:
            print('**** General Configuration ****')
            print('- ref_data:')
            print(self.ref_data.describe())
            print('- directory_path: ' + self.directory_path)
            print('- col_name: ' + str(self.col_name))
            print('- skip_row: ' + str(self.skip_row))
            print()
    