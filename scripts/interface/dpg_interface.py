# -*- coding: utf-8 -*-
'''
Created on Fri Jun  3 19:02:53 2022
@author: ku_sk
TODO: Estimate the optimal number of clusters by Elbow method.
'''

import glob
from dataclasses import dataclass

import dearpygui.dearpygui as dpg
import pandas as pd
from clustering_tools.dynamic_time_warping import DynamicTimeWarping

import interface.utils


@dataclass
class TimeSeriesData:
    file: str
    path: str
    data: list

class DpgInterface(object):

    _ver = '0.0.1'

    _tool_tag = 'file_sort_tool'
    _tool_label = 'FileSortingTool'

    _terminate_flag = False
    _use_debug_print = False
    
    _ref_data_ = TimeSeriesData(
        file='',
        path='',
        data=[]
    )
    _target_dir_path_ = ''
    _target_data_dict_ = {}
    _match_data_dict_ = {}
    _mismatch_data_dict_ = {}
    
    _dtw = DynamicTimeWarping()
    
    # 入力データ設定
    _col_name = ''
    _skip_row = 0
    
    # ソート設定
    _distance_threshold = 30.0
    
    # 自動処理モード用設定
    

    def __init__(
        self,
        width=1280,
        height=720,
        use_debug_print=False
    ):
        # 各種初期化
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
            tag=self._tool_tag + '_window',
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
                with dpg.menu(label='Menu'):
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
                    
            with dpg.group():
                with dpg.group(horizontal=True):
                    with dpg.child_window(
                        width=width/2 - 10,
                        height=height - 85
                    ):
                        dpg.add_text('Target Items:')
                        dpg.add_listbox(
                            items=[self._target_data_dict_[key].file for key in self._target_data_dict_.keys()],
                            tag='target_item_list',
                            width=width/2 - 30,
                            num_items=20
                        )
                            
                    with dpg.group():
                        with dpg.child_window(width=width/2 - 15,
                                              height=height/2 - 45):
                            dpg.add_text('Match Items')
                            dpg.add_listbox(
                                items=[self._match_data_dict_[key].file for key in self._match_data_dict_.keys()],
                                tag='match_item_list',
                                width=width/2 - 30,
                                num_items=8
                            )
                        with dpg.child_window(width=width/2 - 15,
                                              height=height/2 - 45):
                            dpg.add_text('Mismatch Items')
                            dpg.add_listbox(
                                items=[self._mismatch_data_dict_[key].file for key in self._mismatch_data_dict_.keys()],
                                tag='mismatch_item_list',
                                width=width/2 - 30,
                                num_items=8
                            )
                
                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label='Run',
                        tag='run_button',
                        width=70,
                        height=42,
                        callback=self._callback_push_run
                    )
                    with dpg.group():
                        dpg.add_progress_bar(
                            tag='individual_progress',
                            width=583,
                            default_value=0.0,
                            overlay='0.0%: '
                        )
                        dpg.add_progress_bar(
                            tag='overall_progress',
                            width=583,
                            default_value=0.0,
                            overlay='0.0%'
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
                        '-> ' + self._ref_data_.file,
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
                        '-> ' + self._target_dir_path_,
                        tag='show_directory_path'
                    )
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Target Column Name:'
                        )
                        dpg.add_combo(
                            tag='col_list',
                            default_value=self._col_name,
                            width=100,
                            callback=lambda sender, data: setattr(self, '_col_name', data)
                        )
                    with dpg.group(horizontal=True):
                        dpg.add_text(
                            'Skip Row Num:'
                        )
                        dpg.add_input_int(
                            tag='skip_row',
                            default_value=self._skip_row,
                            width=100,
                            callback=lambda sender, data: setattr(self, '_skip_row', data)
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
                            default_value=self._distance_threshold,
                            width=100,
                            callback=lambda sender, data: setattr(self, '_distance_threshold', data)
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
            self._tool_tag + '_window',
            True
        )

    def _callback_close_window(self, sender, app_data):
        dpg.delete_item(sender)

    def _callback_open_file(self, sender, app_data):
        if app_data['file_name'] != '.':
            
            # ファイル情報を保存
            self._ref_data_.file = app_data['file_name']
            self._ref_data_.path = app_data['file_path_name']
            
            # CSVファイルのデータから列名リストを取り出してcol_listを更新
            df = pd.read_csv(
                app_data['file_path_name'],
                index_col=None,
                header=0,
                skiprows=self._skip_row
            )
            cols = list(df)
            dpg.configure_item(
                'col_list',
                items=cols,
                default_value=cols[0]
            )
            dpg.configure_item(
                'show_ref_file',
                default_value='-> ' + self._ref_data_.file
            )
            # # データサイズが大きい場合は警告
            # dpg.configure_item('import_caution', show=True)

        if self._use_debug_print:
            print('**** _callback_open_file ****')
            print('- sender:    ' + str(sender))
            print('- data:      ' + str(app_data))
            print('- loaded:    ')
            print(df.describe())
            print()
            
    def _callback_open_directory(self, sender, app_data):
        if app_data['file_name'] != '.':
            self._target_dir_path_ = app_data['file_path_name']
            item = sorted(glob.glob(self._target_dir_path_ + '\\*.csv'))
            dpg.configure_item(
                'show_directory_path',
                default_value='-> {} files exist.'.format(len(item))
            )

        if self._use_debug_print:
            print('**** _callback_open_directory ****')
            print('- sender:    ' + str(sender))
            print('- data:      ' + str(app_data))
            print('- loaded:    ')
            print(self._target_dir_path_)
            print()

    def _callback_save_general_configuration(self, sender, app_data):
        
        # Referenceデータを読込
        df = pd.read_csv(
            self._ref_data_.path,
            index_col=None,
            header=0, 
            skiprows=self._skip_row
        )
        self._ref_data_.data = df[self._col_name].to_list().copy()
        
        # Targetデータを読込
        file_path_list = sorted(glob.glob(self._target_dir_path_ + '\\*.csv'))
        for file_path in file_path_list:
            df = pd.read_csv(
                file_path,
                index_col=None,
                header=0, 
                skiprows=self._skip_row
            )
            data = TimeSeriesData(
                file=file_path.replace(self._target_dir_path_ + '\\', ''),
                path=file_path,
                data=df[self._col_name].to_list()
            )
            self._target_data_dict_[data.file.lower().replace('.csv', '')] = data
        
        # Window上のlistboxを更新
        self._update_item_listbox()
        
        # 設定画面を閉じる
        dpg.configure_item(
            'general_settings',
            show=False,
        )
        
        if self._use_debug_print:
            print('**** General Configuration ****')
            print('- ref_data:       {} datas'.format(len(self._ref_data_.file)))
            print('- Target File: {} files exist.'.format(len(self._target_data_dict_.keys())))
            print('- col_name:       {}'.format(self._col_name))
            print('- skip_row:       {}'.format(self._skip_row))
            print()
            
    def _callback_push_run(self, sender, app_data):
        self._sort_file()
    
    def _update_item_listbox(self):
        dpg.configure_item(
            'target_item_list',
            items=[self._target_data_dict_[key].file for key in self._target_data_dict_.keys()]
        )
        dpg.configure_item(
            'match_item_list',
            items=[self._match_data_dict_[key].file for key in self._match_data_dict_.keys()]
        )
        dpg.configure_item(
            'mismatch_item_list',
            items=[self._mismatch_data_dict_[key].file for key in self._mismatch_data_dict_.keys()]
        )
        pass
    
    def _sort_file(self):
        
        def individual_progress(progress:float, message:str=''):
            dpg.configure_item(
                'individual_progress',
                default_value=progress,
                overlay='{:.1f}%: {}'.format(progress*100, message)
            )
        
        # progress表示用
        individual_progress(0.0)
        overall_step = len(self._target_data_dict_)
        individual_step = 4
        
        # 作業用dictコピー
        individual_progress(
            progress=float(1/individual_step),
            message='load data'
        )
        tmp = self._target_data_dict_.copy()
        
        # Referenceデータとの類似度評価 -> 閾値以下ならmatch_item
        for key in tmp.keys():
            individual_progress(
                progress=float(2/individual_step),
                message='check distance'
            )
            dist = self._dtw.get_distance(
                ref=self._ref_data_.data,
                data=tmp[key].data,
                plot=False
            )
            if self._use_debug_print:
                print('file: {}, dist: {}'.format(tmp[key].file, dist))
            
            individual_progress(
                progress=float(3/individual_step),
                message='move file'
            )
            if dist <= self._distance_threshold:
                self._match_data_dict_[key] = self._target_data_dict_.pop(key)
                interface.utils.move_file(
                    src=self._match_data_dict_[key].path,
                    dst=self._match_data_dict_[key].path.replace(
                        self._target_dir_path_,
                        self._target_dir_path_ + '\\match_files'
                    )
                )
            else:
                self._mismatch_data_dict_[key] = self._target_data_dict_.pop(key)
                interface.utils.move_file(
                    src=self._mismatch_data_dict_[key].path,
                    dst=self._mismatch_data_dict_[key].path.replace(
                        self._target_dir_path_,
                        self._target_dir_path_ + '\\mismatch_files'
                    )
                )
            self._update_item_listbox()
            
            individual_progress(
                progress=float(4/individual_step),
                message='done'
            )
            overall_progress = float((overall_step - len(self._target_data_dict_))/overall_step)
            dpg.configure_item(
                'overall_progress',
                default_value=overall_progress,
                overlay='{:.1f}%'.format(overall_progress*100)
            )
        