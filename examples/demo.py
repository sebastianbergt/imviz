"""
Inspired by the imgui/implot demo files this file demonstrates the usage of
imviz by example.
"""

import sys
import time
import numpy as np
import pandas as pd

import imviz as viz


class SlotClass:

    __slots__ = ('a', 'b')

    def __init__(self):

        self.a = 0
        self.b = "1"


def test_func():

    for i in range(10):
        time.sleep(1)
        print(i)

    return 42


class Demo:

    def __init__(self):

        # window state

        self.show_overlay = True
        self.show_demo = True

        # input values

        self.input_string = "This is a test"
        self.input_int = 0
        self.input_float = 0.0

        self.range = (0.0, 10.0)

        self.checkbox = False

        self.color_rgb = [1.0, 1.0, 0.0]
        self.color_rgba = [1.0, 1.0, 0.0, 0.0]

        self.file_path = "/"
        self.file_path2 = "/"

        self.test_dict = dict(a="alkjadf", b=1.0, c=[1.0, 2.0, 3.0])

        self.test_list = [1.0, 2.0, 3.0]

        # selection

        self.items = ["mars", "venus", "apollo", "zeus", "hera"]
        self.selection = 0
        self.multi_selection = []

        self.sel_idx = 0

        # dataframes

        self.xs = np.arange(0.0, 100.0, 0.1)
        self.ys = np.random.rand(1000)

        self.frame_selection = []
        self.frame = pd.DataFrame({"xs": self.xs, "ys": self.ys})

        # plotting

        self.img = np.random.rand(240, 320, 3).astype("float32")
        self.img_double = np.random.rand(240, 320, 3)
        self.img_bool = np.random.rand(240, 320) > 0.5

        self.target_pos = (0.0, 0.0)

        self.drag_point = (0, 1)
        self.drag_vline = 2.0
        self.drag_hline = 2.0

        self.drag_rect = [0.0, 0.0, 1.0, 1.0]

        self.drag_dots = []

        self.popup_open = False
        self.popup_plot_pos = (0.0, 0.0)

        self.perf_xs = np.random.rand(64, 3600).reshape((-1,))
        self.perf_ys = np.random.rand(64, 3600).reshape((-1,))

        self.blab = 5

        self.slotted_obj = SlotClass()

        # for plot modifier test

        self.mod_position = (10, 10)
        self.mod_rotation = np.pi/4
        self.mod_scale = (1, 1)

        # selection test

        self.selection_test = viz.Selection(["A", "B", "C"])

    def __autogui__(s, **kwargs):

        if not viz.wait():
            sys.exit()

        icon = np.zeros((17, 17, 4)) * 255
        icon[::2, ::2, 0] = 255
        icon[::2, ::2, 1] = 255
        icon[::2, ::2, 3] = 255
        viz.set_main_window_icon(icon)

        viz.set_main_window_title("Demo")
        viz.show_imgui_demo(True)
        viz.show_implot_demo(True)

        for e in viz.get_key_events():
            if e.key == viz.KEY_K:
                if e.action == viz.PRESS and e.mod == viz.MOD_CONTROL:
                    print("Pressed Ctrl+K")

        if viz.button("Enter Fullscreen"):
            viz.enter_fullscreen()

        viz.same_line()

        if viz.button("Leave Fullscreen"):
            viz.leave_fullscreen()

        if viz.button("Start Task"):
            viz.task.update("test_task", test_func)

        if res := viz.task.result("test_task"):
            print(res)

        viz.text(viz.task.active("test_task"))

        viz.latex(r"$\sum_i^T \alpha, \textrm{in} [m/s] \beta, \gamma$")

        # menus

        if viz.begin_main_menu_bar():

            if viz.begin_menu("File"):

                if viz.menu_item("Reset"):
                    s = Demo()

                viz.end_menu()

            if viz.begin_menu("Show"):

                if viz.menu_item("Show overlay",
                                 selected=s.show_overlay):
                    s.show_overlay = not s.show_overlay
                if viz.menu_item("Show demo",
                                 selected=s.show_demo):
                    s.show_demo = not s.show_demo
                viz.menu_item("Disabled demo", enabled=False)
                viz.menu_item("Shortcut demo", shortcut="Ctrl+Z")

                viz.end_menu()

            viz.end_main_menu_bar()

        # window options

        if s.show_overlay:

            if viz.begin_window("Overlay",
                                s.show_overlay,
                                position=(6, 32),
                                size=(100, 100),
                                title_bar=False,
                                move=False,
                                resize=False):

                viz.text("Overlay")

            viz.end_window()

        # widgets

        if viz.begin_window("Demo"):

            viz.button("source")

            if viz.begin_drag_drop_source():
                array = np.zeros((10, ))
                viz.set_drag_drop_payload("state", array)
                viz.text(array)
                viz.end_drag_drop_source()

            viz.button("Target 2")

            if viz.begin_drag_drop_target():
                if (res := viz.accept_drag_drop_payload("state")) is not None:
                    print("Got drag and drop:", res)
                viz.end_drag_drop_target()

            viz.autogui(s.__dict__, "State Autogui")

            if viz.tree_node("Input"):

                s.input_string = viz.input("input string", s.input_string)
                s.input_int = viz.input("input int", s.input_int)
                s.input_float = viz.input("input float", s.input_float)

                s.checkbox = viz.checkbox("checkbox", s.checkbox)

                s.input_float = viz.slider("slider",
                                           s.input_float,
                                           0.0,
                                           1000)

                s.input_int = viz.drag("drag int",
                                       s.input_int,
                                       0.1,
                                       1,
                                       1000)

                s.input_float = viz.drag("drag float",
                                         s.input_float,
                                         0.01,
                                         0.0,
                                         1000)

                s.color_rgb = viz.color_edit("color rgb", s.color_rgb)
                s.color_rgba = viz.color_edit("color rgba", s.color_rgba)

                s.range = viz.range("range", s.range)

                if viz.button(f"B: {s.file_path}"):
                    viz.open_popup("File Selection")

                s.file_path = viz.file_dialog_popup("File Selection", s.file_path)

                if viz.button(f"A: {s.file_path2}"):
                    viz.open_popup("File Selection 2")

                s.file_path2 = viz.file_dialog_popup("File Selection 2", s.file_path2)

                viz.tree_pop()

            if viz.tree_node("Selection"):

                s.selection = viz.combo("combo", s.items, s.selection)

                s.multi_selection = viz.multiselect("multiselect",
                                                    s.items,
                                                    s.multi_selection)

                viz.tree_pop()

            if viz.tree_node("Dataframe"):

                viz.dataframe(s.frame, "dataframe", s.frame_selection)

                viz.tree_pop()

            if viz.tree_node("Plotting"):

                sc = viz.get_pixels(0, 0, 300, 300)
                viz.image("test_image", sc)

                if viz.begin_plot("Plot"):

                    viz.setup_axis(viz.Axis.X1, "x")
                    viz.setup_axis(viz.Axis.Y1, "y")

                    if viz.plot_selection_ended():
                        viz.hard_cancel_plot_selection()

                    viz.plot_circle(10, 10, 5,
                            label="circle",
                            color=(1.0, 0.0, 0.0),
                            line_weight=2)

                    viz.plot_image("image",
                                   s.img,
                                   x=0, y=0,
                                   width=1, height=1)

                    viz.plot([1, 2, 3],
                             [1, 2, 3],
                             shade=[2, 1, 3],
                             fmt="-o",
                             label="line_with_dots")

                    viz.plot(np.array([1, 2, 3]) * 2,
                             fmt="*",
                             label="big stars",
                             marker_size=6,
                             marker_weight=2)

                    viz.plot([1, 2, 3],
                             np.array([1, 2, 3])**2,
                             line_weight=3,
                             fmt="-s",
                             label="small_squares")

                    viz.plot([], line_weight=3, fmt="-s", label="zero len array")

                    s.drag_point = viz.drag_point("draggable",
                                                  s.drag_point,
                                                  color=(1.0, 0.0, 0.0),
                                                  radius=10)

                    s.drag_vline = viz.drag_vline("vline",
                                                  s.drag_vline,
                                                  color=(0.0, 1.0, 0.0),
                                                  width=2)

                    s.drag_hline = viz.drag_hline("hline",
                                                  s.drag_hline,
                                                  color=(0.0, 1.0, 0.0),
                                                  width=2)

                    s.drag_rect = viz.drag_rect("rect",
                                                s.drag_rect,
                                                color=(0.0, 1.0, 1.0))

                    viz.plot_annotation(5, 5, "foo")
                    viz.plot_annotation(8, 5, "foo blue", color=(0.0, 0.2, 1.0))

                    viz.push_override_id(viz.get_plot_id())

                    if viz.begin_popup("##PlotContext"):
                        if not s.popup_open:
                            s.popup_plot_pos = viz.get_plot_mouse_pos()
                        s.popup_open = True
                        if viz.begin_menu("Create"):
                            if viz.menu_item("Drag Dot"):
                                s.drag_dots.append((1, 1))
                            viz.end_menu()
                        if viz.menu_item("Print mouse pos"):
                            print(s.popup_plot_pos)
                        if viz.menu_item("Print plot limits"):
                            print(viz.get_plot_limits())
                        viz.end_popup()
                    else:
                        s.popup_open = False

                    viz.pop_id()

                    for i in range(len(s.drag_dots)):
                        s.drag_dots[i] = viz.drag_point(f"dot_#{i}",
                                                        s.drag_dots[i],
                                                        color=(1.0, 0.0, 0.0),
                                                        radius=4)

                        if not viz.plot_contains(s.drag_dots[i]):
                            continue

                        if viz.begin_popup_context_item(f"dot_#{i}"):
                            if viz.menu_item("Delete"):
                                print(f"deleting {i}")
                            viz.end_popup()

                    viz.plot_vlines("hlines", [1, 4, 6, 8], width=2)
                    viz.plot_hlines("vlines", [1, 4, 6, 8], width=1)

                    viz.plot_bars([[1, 2, 3, 4], [2, 2, 3, 3]], width=0.8)

                    viz.end_plot()

                viz.tree_pop()

            if viz.tree_node("Images"):

                viz.image("color image float", s.img)
                viz.image("color image double", s.img_double)
                viz.image("image bool", s.img_bool)

                viz.tree_pop()

            if viz.tree_node("Many Images"):

                for i in range(100):

                    if i == s.sel_idx:
                        tint = [0.6, 0.6, 0.6, 1.0]
                    else:
                        tint = [1, 1, 1, 1]

                    viz.text(f"image {i}")

                    viz.image("color image float", s.img, tint=tint)

                    if viz.is_item_clicked():
                        s.sel_idx = i

                viz.tree_pop()

            if viz.tree_node("Modal popup"):

                if viz.button("open popup"):
                    viz.open_popup("Modal Test")

                viz.set_next_window_pos(viz.get_viewport_center(), pivot=(0.5, 0.5))

                if viz.begin_popup_modal("Modal Test"):

                    viz.text("This is a modal popup!")

                    viz.separator()

                    if viz.button("close"):
                        viz.close_current_popup()

                    viz.end_popup()

                viz.tree_pop()

            if viz.tree_node("Plot Performance Test"):

                if viz.begin_plot("Test Plot"):

                    viz.setup_finish()

                    dl = viz.get_plot_drawlist()

                    viz.push_plot_clip_rect(0.0)
                    dl.add_line((0.0, 0.0), (1000.0, 1000.0), (1.0, 0.0, 0.0, 1.0), 2.0)
                    viz.pop_plot_clip_rect()

                    viz.plot(s.perf_xs, s.perf_ys, fmt="o", label="dots", marker_size=1)

                    viz.end_plot()

                viz.tree_pop()

            if viz.tree_node("Column Test"):

                viz.text("(?)")

                if viz.is_item_hovered():
                    viz.begin_tooltip()
                    viz.text("What did you expect?")
                    viz.end_tooltip()

                if viz.button("test svg"):
                    viz.begin_svg()

                viz.style_colors_light()

                if viz.begin_plot("Deschd Plot", size=(400, 300)):
                    viz.setup_axes(r"$\theta$ $v[\frac{m}{s}]$", "")
                    viz.plot([1, 2, 3], [4, 5, 6], fmt="-o", label="line", line_weight=3, marker_size=5)
                    viz.plot([1, 2, 3], [8, 2, 5], fmt="-o", label="g.t.", line_weight=3, marker_size=5)
                    viz.end_plot()

                viz.style_colors_dark()

                if svg := viz.end_svg():
                    with open("test.svg", "w+") as fd:
                        fd.write(svg)

                w, h = viz.get_content_region_avail()

                for i in range(10):
                    for j in range(10):
                        viz.set_next_item_width((w / 10) - 8)
                        viz.drag(f"###{i},{j}", 0.0)
                        if j < 9:
                            viz.same_line()

                viz.tree_pop()


            if viz.tree_node("Plot Modifer Test"):

                img = np.random.rand(10, 10)

                if viz.begin_plot("test_plot", size=(500, 500)):

                    viz.setup_finish()

                    viz.begin_rotation(s.mod_rotation)
                    viz.plot_image("img", img, x=s.mod_position[0]-s.mod_scale[0]/2, y=s.mod_position[1]-s.mod_scale[1]/2, width=s.mod_scale[0], height=s.mod_scale[1])
                    viz.end_rotation()

                    s.mod_position = viz.drag_point("pos_drag", s.mod_position)

                    viz.end_plot()

                viz.tree_pop()

        viz.end_window()


def main():

    viz.dev.launch(Demo, "__autogui__")


if __name__ == "__main__":
    main()
