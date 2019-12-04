#!/usr/bin/env python
import ipywidgets as widgets
from ipywidgets import HBox, VBox, Layout, Box

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display, clear_output

#### ----- fem widgets
fem_header = widgets.HTML(value="<h4>Simulation parameters</h4>")

wl_box = widgets.FloatText(value=1.0, description="Wavelengh:")

pola_dropdown = widgets.Dropdown(
    options=["TE", "TM"], value="TE", description="Polarization:", disabled=False
)

run_button = widgets.Button(description="Run", icon="fa-play", button_style="danger")

angle_slider = widgets.FloatSlider(
    value=0, min=0, max=360.0, step=1, description="Angle:", readout_format=".1f"
)

mesh_slider = widgets.IntSlider(
    value=3, min=2, max=10, step=1, description="Mesh level:"
)


hx_box = widgets.FloatText(value=1.0, step=0.01, description="Design width:")

hy_box = widgets.FloatText(value=1.0, step=0.01, description="Design length:")


target_x_box = widgets.FloatText(value=0, step=0.01, description="Target $x$:")

target_y_box = widgets.FloatText(value=-1.1, step=0.01, description="Target $y$:")

epsmin_re_box = widgets.FloatText(value=1, step=0.01, description="Re $\epsilon_1$:")
epsmin_im_box = widgets.FloatText(value=0, step=0.01, description="Im $\epsilon_1$:")


epsmax_re_box = widgets.FloatText(value=6, step=0.01, description="Re $\epsilon_2$:")
epsmax_im_box = widgets.FloatText(value=0, step=0.01, description="Im $\epsilon_2$:")

#### ----- optim widgets


opt_header = widgets.HTML(value="<h4>Optimization parameters</h4>")


maxeval_slider = widgets.IntSlider(
    value=2, min=10, max=50, step=1, description="Max iter:"
)

Nitmax_slider = widgets.IntSlider(
    value=1, min=1, max=7, step=1, description="Max restart:"
)

rfilt_box = widgets.FloatText(value=0.01, step=0.001, description="Filter radius:")

starting_dropdown = widgets.Dropdown(
    options=["constant", "random"], value="constant", description="Init type:"
)

p0_slider = widgets.FloatSlider(
    value=0.5, min=0, max=1, step=0.01, description="Init density:"
)


#### -----
sep = widgets.HTML(value="<h4></h4>")


fem_par = params = VBox(
    children=[
        fem_header,
        wl_box,
        pola_dropdown,
        angle_slider,
        mesh_slider,
        hx_box,
        hy_box,
        target_x_box,
        target_y_box,
        epsmin_re_box,
        epsmin_im_box,
        epsmax_re_box,
        epsmax_im_box,
        ## -------
        opt_header,
        maxeval_slider,
        Nitmax_slider,
        rfilt_box,
        starting_dropdown,
        p0_slider,
        ## -------
        sep,
        run_button,
    ]
)

conv_plt = go.FigureWidget()
conv_plt.add_scatter(fill="tozeroy")
s = conv_plt.data[0]

s.marker.color = "firebrick"
# dict(color='firebrick', width=4)
conv_plt.layout.template = "plotly_white"
conv_plt.layout.title = "Convergence"
conv_plt.layout.xaxis.title = "iterations"
conv_plt.layout.yaxis.title = "objective"
# conv_plt = widgets.Output(layout=Layout(height='300px', width = '400px'))
# eps_map = widgets.Output()
eps_map = go.FigureWidget()
eps_map.add_heatmap(colorscale="amp")
eps_map.layout = dict(
    plot_bgcolor="rgba(0, 0, 0, 0)",
    # paper_bgcolor= "rgba(0, 0, 0, 0)",
    title="Permittivity",
    yaxis=dict(scaleanchor="x", scaleratio=1),
)

field_map = go.FigureWidget()
field_map.add_contour(colorscale="Geyser")
field_map.layout = dict(
    plot_bgcolor="rgba(0, 0, 0, 0)",
    # paper_bgcolor= "rgba(0, 0, 0, 0)",
    title="Field",
    yaxis=dict(scaleanchor="x", scaleratio=1),
)

design = go.layout.Shape(type="rect", x0=0, y0=0, x1=1, y1=1, line=dict(color="white"))

field_map.add_shape(design)
plots = VBox(children=[conv_plt, eps_map, field_map])
