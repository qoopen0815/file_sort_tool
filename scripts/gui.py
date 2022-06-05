# -*- coding: utf-8 -*-
'''
Created on Fri Jun  3 19:02:53 2022
@author: ku_sk
TODO: Estimate the optimal number of clusters by Elbow method.
'''

import dearpygui.dearpygui as dpg
import glob
import webbrowser

def _help(message):
    last_item = dpg.last_item()
    group = dpg.add_group(horizontal=True)
    dpg.move_item(last_item, parent=group)
    dpg.capture_next_item(lambda s: dpg.move_item(s, parent=group))
    t = dpg.add_text('(?)', color=[0, 255, 0])
    with dpg.tooltip(t):
        dpg.add_text(message)

def _hyperlink(text, address):
    b = dpg.add_button(label=text, callback=lambda:webbrowser.open(address))
    dpg.bind_item_theme(b, '__demo_hyperlinkTheme')    
    
def _hsv_to_rgb(h, s, v):
    if s == 0.0: return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
    if i == 0: return (255*v, 255*t, 255*p)
    if i == 1: return (255*q, 255*v, 255*p)
    if i == 2: return (255*p, 255*v, 255*t)
    if i == 3: return (255*p, 255*q, 255*v)
    if i == 4: return (255*t, 255*p, 255*v)
    if i == 5: return (255*v, 255*p, 255*q)


if __name__ == '__main__':
    
    # Callback
    def _input_directory(sender, keyword):
        pct.directory = keyword
        num = len(glob.glob(pct.directory + '\\*.csv'))
        dpg.set_value('state_of_dirpath', '{} csv files exist.'.format(num))
    def _input_colname(sender, keyword):
        pct.target_col = keyword
    def _input_cluster_num(sender, keyword):
        pct.cluster_num = keyword
    def _input_skip_num(sender, keyword):
        pct.skip_row = keyword
    def _input_method(sender, keyword):
        pct.method = keyword
    def _press_run():
        with dpg.popup(dpg.last_item(), modal=True, mousebutton=dpg.mvMouseButton_Left, tag='_process_popup'):
            with dpg.group(horizontal=True):
                dpg.add_loading_indicator(circle_count=6)
                with dpg.group():
                    dpg.add_text('', tag='process_message')
                    dpg.add_text('')
                    dpg.add_button(label="OK", tag='ok_button', width=75, callback=lambda: dpg.configure_item("_process_popup", show=False))
        
        print('start process')
        dpg.configure_item('ok_button', show=False)
        
        
        # Process finish
        dpg.set_value('process_message', 'Done!')
        dpg.configure_item('ok_button', show=True)
                
    
    pct = PythonClusteringTool()
    
    ## Application Section
    dpg.create_context()
    dpg.create_viewport(title='Python Clustering Tool', width=600, height=250)
    
    # Show Application GUI
    with dpg.window(tag='Primary Window'):
        
        ## Body
        with dpg.group():
            
            # description
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text('About Me:')
                    _help(
                        'Py-CT(PythonClusteringTool) is a tool for sorting CSV files\n'
                        'based on the clustering results of timeseries data.')
                    dpg.add_text('')
                    
            with dpg.group():
                
                dpg.add_text('Settings:')
                with dpg.group(horizontal=True):
                    dpg.add_text('File Directory Path:   ', bullet=True, indent=20)
                    dpg.add_input_text(default_value=pct.directory, width=200, callback=_input_directory)
                    dpg.add_text('0 csv files exist.', tag='state_of_dirpath')
                with dpg.group(horizontal=True):
                    dpg.add_text('Target Column Name:    ', bullet=True, indent=20)
                    dpg.add_input_text(default_value=pct.target_col, width=100, callback=_input_colname)
                with dpg.group(horizontal=True):
                    dpg.add_text('Skip Row Num:          ', bullet=True, indent=20)
                    dpg.add_input_int(default_value=pct.skip_row, tag='skip_num', width=100, callback=_input_skip_num)
                    # dpg.add_input_int(default_value=skip_row, tag='skip_num', width=100, callback=_input_skip_num)
                with dpg.group(horizontal=True):
                    dpg.add_text('Clustering Method:     ', bullet=True, indent=20)
                    dpg.add_combo(('DTW', 'K-Shape'), default_value=pct.method, width=100, callback=_input_method)
                with dpg.group(horizontal=True):
                    dpg.add_text('Quantity of Data Type: ', bullet=True, indent=20)
                    dpg.add_input_int(default_value=pct.cluster_num, tag='cluster_num', width=100, callback=_input_cluster_num) 
                
                dpg.add_button(label='Run', tag='run_button', callback=_press_run)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window('Primary Window', True)
    dpg.start_dearpygui()
    dpg.destroy_context()
