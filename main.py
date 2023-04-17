import yaml
from easydict import EasyDict as edict
import dearpygui.dearpygui as dpg
import time as time__

from simulator.simulate import Simulator
from controller.control import PurePursuit, MPC
from utils.type import State, ControlCommand

def init_gui(simulator):
    dpg.create_context()
    # Layout Define
    with dpg.window(tag="Primary Window", label="Very Good Simulator", autosize=True):
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
            with dpg.child_window(width=800, height=900):
                # Simulator button
                with dpg.child_window(autosize_x=True, height=40):
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Run", callback=simulator.begin, width=40, height=20)
                        dpg.add_button(label="Stop", callback=simulator.stop, width=40, height=20)
                        dpg.add_text("Lap Info", tag="lap_info", color=(255, 40, 0))
                # Simulator plot
                with dpg.plot(tag="plot", label="MPC Predicted and Reference Path", height=-1, width=-1):
                    # optionally create legend
                    dpg.add_plot_legend()

                    # REQUIRED: create x and y axes
                    dpg.add_plot_axis(dpg.mvXAxis, label="x", tag='xaxis')
                    dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="yaxis")
                    dpg.set_axis_limits('xaxis', -15, 15)
                    dpg.set_axis_limits('yaxis', 0, 30)

                    # # series belong to a y axis
                    dpg.add_scatter_series([], [], label="Predicted Path", parent="yaxis", tag="pre_path")
                    dpg.add_scatter_series([], [], label="Reference Path", parent="yaxis", tag="ref_path")
                    dpg.add_scatter_series([], [], label="Car Position", parent="yaxis", tag="car_position_part")

                    # # apply theme to series
                    dpg.bind_item_theme("pre_path", "plot_purplish_blue_scatter")
                    dpg.bind_item_theme("ref_path", "plot_orange_scatter")
                    
            with dpg.child_window(width=300, autosize_y=True):
                dpg.add_text("Real-Time MPC results", color=(255, 255, 255))
                dpg.add_slider_float(tag="vr", label="vr", default_value=0, min_value=0, max_value=10, width=120)
                dpg.add_slider_float(tag="vl", label="vl", default_value=0, min_value=0, max_value=10, width=120)
                dpg.add_slider_float(tag="theta", label="theta", default_value=0, min_value=-4, max_value=4, width=120)
                dpg.add_slider_float(tag="r", label="r", default_value=0, min_value=-1, max_value=1, width=120)
                
                # full map
                with dpg.child_window(width=300, height=300):
                    with dpg.plot(label="Full Map", height=-1, width=-1):
                        dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True, tag="full_track_x")
                        with dpg.plot_axis(dpg.mvYAxis, label="", no_tick_labels=True, tag="full_track_y"):
                            dpg.add_line_series([], [], label="Full Track_", tag="full_map")
                            dpg.add_scatter_series([], [], label="Car Position", tag="car_position")
                        dpg.set_axis_limits('full_track_x', -100, 100)
                        dpg.set_axis_limits('full_track_y', -100, 100)

    dpg.create_viewport(title='Very Good Simulator', width=1200, height=900)
    dpg.setup_dearpygui()
    dpg.show_viewport()

def run(cfgs=None):
    simulator = Simulator(cfgs)
    if cfgs.controller == 'purepursuit':
        controller = PurePursuit(cfgs)
    elif cfgs.controller == 'mpc':
        controller = MPC(cfgs)
    else:
        raise Exception("controller empty!")
    state = simulator.get_state()
    cmd = ControlCommand(0, 0)
    time = 0
    time_ = [0]
    if cfgs.visual:
        init_gui(simulator=simulator)
        full_path_x, full_path_y = simulator.get_full_path()
        dpg.set_value('full_map', [full_path_x, full_path_y])
        dpg.set_axis_limits('full_track_x', min(full_path_x) - 1, max(full_path_x) + 1)
        dpg.set_axis_limits('full_track_y', min(full_path_y) - 1, max(full_path_y) + 1)
    while True and not simulator.is_finished():
        time_1 = time__.time()
        time += cfgs.step_time
        simulator.next_step(state, cmd)
        print(cmd.u_l, cmd.u_r)
        state = simulator.get_state()
        path = simulator.get_path()
        controller.set_path(path)
        controller.set_state(state)
        cmd = controller.get_cmd()
        ref_x = []
        ref_y = []
        ref_theta = []
        for i in path:
            ref_y.append(i[0])
            ref_x.append(-i[1])
            ref_theta.append(i[2])
        if cfgs.controller == 'mpc':
            pre_path = controller.get_pre_path()
            pre_x = []
            pre_y = []
            for i in pre_path:
                pre_y.append(i[0])
                pre_x.append(-i[1])
            if cfgs.visual:
                dpg.set_value('pre_path', [pre_x, pre_y])
        v_l = state.v - cfgs.model.L * state.omega / 2
        v_r = state.v + cfgs.model.L * state.omega / 2
        if cfgs.visual:
            dpg.set_value('car_position', [[state.x], [state.y]])
            dpg.set_value('car_position_part', [[0], [0]])
            dpg.set_value('ref_path', [ref_x, ref_y])
            dpg.set_axis_limits('xaxis', min(ref_x) - 0.4, max(ref_x) + 0.4)
            dpg.set_axis_limits('yaxis',- 0.1, max(ref_y) + 0.1)
            dpg.set_value('lap_info', f"Time: {simulator.get_sim_time():.2f}s")
            dpg.set_value('theta', state.theta)
            dpg.set_value('vl', v_l)
            dpg.set_value('vr', v_r)
            dpg.set_value('r', state.omega)
            dpg.render_dearpygui_frame()
            time_2 = time__.time()
            if cfgs.step_time > time_2 - time_1:
                time__.sleep(cfgs.step_time - time_2 + time_1)
        # break
        if time >= 1000:
            break
    
    time__.sleep(10)

if __name__ == "__main__":
    with open('config/bot.yaml') as yamlfile:
        cfgs = yaml.load(yamlfile, Loader=yaml.FullLoader)
        cfgs = edict(cfgs)
    run(cfgs)