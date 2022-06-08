# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:14:12 2022
@author: ku_sk
"""

import dearpygui.dearpygui as dpg

from interface.file_sort_ui import FileSortUI

def main():
    
    # DearPyGui準備(コンテキスト生成、セットアップ、ビューポート生成)
    dpg_width = 700
    dpg_height = 600

    print('**** DearPyGui Setup ****')
    dpg.create_context()
    dpg.setup_dearpygui()
    dpg.create_viewport(
        title="File Sort Tool",
        width=dpg_width,
        height=dpg_height,
    )

    # デフォルトフォント変更
    with dpg.font_registry():
        with dpg.font(
            'scripts/interface/font/YasashisaAntiqueFont/07YasashisaAntique.otf',
            13,
        ) as default_font:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
    dpg.bind_font(default_font)
    
    window = FileSortUI(
        width=dpg_width - 15,
        height=dpg_height - 40,
        use_debug_print=True,
    )
    
    # ビューポート表示
    dpg.show_viewport()

    # メインループ
    print('**** Start Main Event Loop ****')
    dpg.start_dearpygui()
    # while dpg.is_dearpygui_running():
    #     # 処理内容
    #     dpg.render_dearpygui_frame()

    # 終了処理
    print('**** Terminate process ****')
    # DearPyGuiコンテキスト破棄
    print('**** Destroy DearPyGui Context ****')
    dpg.destroy_context()

if __name__ == '__main__':
    main()