# This script shows the effect of thinning on autocorrelation variables

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import Slider
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
from bokeh.layouts import row
import numpy as np


def autocorr(x, zero_pad: int = 0):
    # from http://tinyurl.com/afz57c4
    result = np.correlate(x, x, mode='full')
    result = result / np.max(result)
    result = result[result.size // 2:]
    if zero_pad > len(result):
        result = np.pad(result, 
                        (0, zero_pad-len(result)), 
                        'constant', 
                        constant_values=(0,0))
    return result

num_samples = 2000
t = [*range(0, num_samples)]
x_t = np.random.normal(0, 1, num_samples)
x_t[0] = 0
y_t = np.zeros(num_samples)
for i in range(1, num_samples):
    y_t[i] = np.random.normal(y_t[i - 1], 1)
    
# Using single lines
source_var = ColumnDataSource(
    data={'t': t,
          'x_t': x_t,
          'y_t': y_t}
    )

p_x_y_t = figure(x_axis_label='time',
                 y_axis_label='variable values',
                 title='Autocorrelated vs Non-autocorrelated')

p_x_y_t.line(x='t',
             y='x_t',
             legend_label='x_t',
             line_color='blue',
             source=source_var)
p_x_y_t.line(x='t',
             y='y_t',
             legend_label='y_t',
             line_color='orange',
             source=source_var)

# AUTOCORRELATIONS
p_autocorr = figure(x_axis_label='k (lag)',
                    y_axis_label='measured correlation',
                    title='Autocorrelation Values')

x_corr = autocorr(x_t)[1:]
y_corr = autocorr(y_t)[1:]
source_corr = ColumnDataSource(
    data={'t': t[1:],
          'x_corr': x_corr,
          'y_corr': y_corr})

p_autocorr.vbar(x='t', 
                top='y_corr', 
                width=1, 
                color='orange',
                source=source_corr,
                legend_label='y_t')
p_autocorr.vbar(x='t', 
                top='x_corr', 
                width=1, 
                color='blue',
                source=source_corr,
                legend_label='x_t')

# THINNING
thin_dict = {}
thinning_range = range(1, 11)
lag_upper_bound = 100
for i in thinning_range:
    thin_dict[i] = autocorr(y_t[::i], zero_pad=200)

# Start with no thinning
source_thinning = ColumnDataSource(
    data={'t': t,
          'y_corr': thin_dict[1]}
    )

p_thinning = figure(x_axis_label='k (lag)',
                    y_axis_label='measured correlation',
                    title='Autocorrelation of y_t',
                    y_range=(min(thin_dict[1])*1.1, 1))

p_thinning.vbar(x='t', 
                top='y_corr', 
                width=1, 
                color='orange',
                source=source_thinning,
                legend_label='y_t')

slider_thinning = Slider(
    start=min(thinning_range),
    end=max(thinning_range),
    step=1,
    value=1,
    title='Thinning'
    )

def callback_thinning(attr, old, new):
    thinning_value = slider_thinning.value
    source_thinning.data = {'t': t,
                            'y_corr': thin_dict[thinning_value]}
    p_thinning.title.text = f'Autocorrelation of y_t keeping every {thinning_value} sample'

slider_thinning.on_change('value', callback_thinning)

layout_thinning = column(slider_thinning,
                         p_thinning)

# show(p_x_y_t)
layout = column(
    row(p_x_y_t, p_autocorr),
    layout_thinning
    )

curdoc().add_root(layout)
