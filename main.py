from tkinter import YES
from turtle import ycor
import yaml
from easydict import EasyDict as edict
import matplotlib.pyplot as plt
import dearpygui.dearpygui as dpg
import time as time__

from simulator.simulate import Simulator
from utils.type import State, ControlCommand

def save_callback():
    print("Save Clicked")

if __name__ == "__main__":
    with open('config/bot.yaml') as yamlfile:
        cfgs = yaml.load(yamlfile, Loader=yaml.FullLoader)
        cfgs = edict(cfgs)
    simulator = Simulator(cfgs)
    state = simulator.get_state()
    print(state.state())
    cmd = ControlCommand(10, 5)
    time = 0
    x = [state.x]
    y = [state.y]
    theta = [state.theta]
    time_ = [0]
    
    dpg.create_context()

    # Layout Define
    with dpg.window(tag="Primary Window", label="Very Good Simulator", height=900):
        # create a theme for the plot
        with dpg.theme(tag="plot_purplish_blue_scatter"):
            with dpg.theme_component(dpg.mvScatterSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (60, 150, 200), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 2, category=dpg.mvThemeCat_Plots)

        with dpg.theme(tag="plot_orange_scatter"):
            with dpg.theme_component(dpg.mvScatterSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 165, 0), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 2, category=dpg.mvThemeCat_Plots)

        with dpg.theme(tag="plot_red_scatter"):
            with dpg.theme_component(dpg.mvScatterSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 20, 0), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 3, category=dpg.mvThemeCat_Plots)

        with dpg.theme(tag="plot_blue_scatter"):
            with dpg.theme_component(dpg.mvScatterSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 20, 255), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 2, category=dpg.mvThemeCat_Plots)

        with dpg.theme(tag="plot_white_scatter"):
            with dpg.theme_component(dpg.mvScatterSeries):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 255, 255), category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_Marker, dpg.mvPlotMarker_Circle, category=dpg.mvThemeCat_Plots)
                dpg.add_theme_style(dpg.mvPlotStyleVar_MarkerSize, 4, category=dpg.mvThemeCat_Plots)

        with dpg.group(horizontal=True, width=0):
            with dpg.child_window(width=850, autosize_y=True):
                # Simulator button
                with dpg.child_window(autosize_x=True, height=40):
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Run", callback=simulator.begin, width=40, height=20)
                        dpg.add_button(label="Stop", callback=save_callback, width=40, height=20)
                        # dpg.add_button(label="Next Step", callback=save_callback, width=80, height=20)
                        # dpg.add_button(label="Print Graph", callback=save_callback, width=90, height=20)
                        # dpg.add_button(label="Save Graph", callback=save_callback, width=90, height=20)
                        # dpg.add_combo(simulation_manager.map_names, label="", default_value=simulation_manager.map_name, width=90,
                        #       callback=simulation_manager.dpg_set_map)
                        # dpg.add_combo(simulation_manager.model_names, label="", default_value=simulation_manager.model_name, width=90,
                        #       callback=simulation_manager.dpg_set_car_model)
                        # dpg.add_combo(simulation_manager.controller_names, label="", default_value=simulation_manager.controller_name, width=90,
                        #       callback=simulation_manager.dpg_set_controller)
                        dpg.add_text("Lap Info", tag="lap_info", color=(255, 40, 0))
                # Simulator plot
                with dpg.child_window(autosize_x=True, height=800):
                    with dpg.plot(label="Global View", height=-1, width=-1):
                        dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True, tag="full_track_xaxis")
                        with dpg.plot_axis(dpg.mvYAxis, label="", no_tick_labels=True, tag="full_track_yaxis"):
                            dpg.add_line_series([], [], label="Full Track", tag="full_track")
                            dpg.add_scatter_series([], [], label="Car Position", tag="car_position")
                            dpg.add_scatter_series([], [], label="Estimate Car Position", tag="estimate_car_position")
                            dpg.add_scatter_series([], [], label="truth_global", tag="truth_global")
                            dpg.add_scatter_series([], [], label="map_global", tag="map_global")
                            dpg.add_scatter_series([], [], label="observation_global", tag="observation_global")

                            dpg.bind_item_theme("map_global", "plot_red_scatter")
                            dpg.bind_item_theme("observation_global", "plot_blue_scatter")
                            dpg.bind_item_theme("truth_global", "plot_white_scatter")
                        dpg.set_axis_limits('full_track_xaxis', -100, 100)
                        dpg.set_axis_limits('full_track_yaxis', -100, 100)
                    # simulation_manager.update_full_track()

    dpg.create_viewport(title='Very Good Simulator', width=880, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    # dpg.show_metrics()

    while True:
        if time - time_[-1] > 0.1:
            time_.append(time)
            x.append(state.x)
            y.append(state.y)
            theta.append(state.theta)
            # print(x)
            dpg.set_value('full_track', [x, y])
            dpg.set_axis_limits('full_track_xaxis', min(x) - 0.04, max(x) + 0.04)
            dpg.set_axis_limits('full_track_yaxis', min(y) - 0.04, max(y) + 0.04)
            dpg.set_value('lap_info', f"Time: {simulator.get_sim_time():.2f}s")
            dpg.render_dearpygui_frame()
        # print(time)
        time += cfgs.step_time
        simulator.next_step(state, cmd)
        state = simulator.get_state()
        # print(state.state())
        if state.x == 5:
            cmd = ControlCommand(10,5)
        else:
            cmd = ControlCommand(0, 0)
        if time >= 1000:
            time__.sleep(1000)
            break
    
    # plt.plot(x,y)
    # plt.show()

        # break