from bokeh.plotting import figure
from bokeh.plotting import show
from bokeh.io import curdoc
from bokeh.io import output_file
from bokeh.models import Slider
from bokeh.models import ColumnDataSource
from bokeh.layouts import row
from bokeh.layouts import column
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path


def create_data(N, x, y, random_state=42):
    # the true parameters, but of course we do not see these values...
    lambda_1_true = 1
    lambda_2_true = 3
    
    #...we see the data generated, dependent on the above two values.
    data = np.concatenate([
        stats.poisson.rvs(lambda_1_true, size=(N, 1), random_state=random_state),
        stats.poisson.rvs(lambda_2_true, size=(N, 1), random_state=random_state)
    ], axis=1)
    # print("observed (2-dimensional,sample size = %d):" % N, data)
    
    # plotting details.
    likelihood_x = np.array([stats.poisson.pmf(data[:, 0], _x) for _x in x]).prod(axis=1)
    likelihood_y = np.array([stats.poisson.pmf(data[:, 1], _y) for _y in y]).prod(axis=1)
    L = np.dot(likelihood_x[:, None], likelihood_y[None, :])
    
    return L

L_dict = {}
x = y = np.linspace(.01, 5, 100)

for N in range(1,101):
    L_dict[N] = create_data(N, x, y)

uni_x = stats.uniform.pdf(x, loc=0, scale=5)
uni_y = stats.uniform.pdf(x, loc=0, scale=5)
uni_M = np.dot(uni_x[:, None], uni_y[None, :])
uni_post = L_dict[1] * uni_M

exp_x = stats.expon.pdf(x, loc=0, scale=3)
exp_y = stats.expon.pdf(x, loc=0, scale=10)
exp_M = np.dot(exp_x[:, None], exp_y[None, :])
exp_post = L_dict[1] * exp_M

# Start with N=1
uni_source = ColumnDataSource(data={'posterior': [L_dict[1] * uni_M]})
exp_source = ColumnDataSource(data={'posterior': [L_dict[1] * exp_M]})

uni_p = figure(title='Uniform Priors')
uni_p.x_range.range_padding = uni_p.y_range.range_padding = 0
uni_p.image(image='posterior', 
            x=0, 
            y=0, 
            dw=10, 
            dh=10, 
            palette="Magma256", 
            level="image",
            source=uni_source)

exp_p = figure(title='Exponential Priors')
exp_p.x_range.range_padding = exp_p.y_range.range_padding = 0
exp_p.image(image='posterior', 
            x=0, 
            y=0, 
            dw=10, 
            dh=10, 
            palette="Magma256", 
            level="image",
            source=exp_source)

slider = Slider(
    start=1,
    end=100,
    step=1,
    value=1
    )

def callback(attr, old, new):
    N = slider.value
    uni_source.data = {'posterior': [L_dict[N] * uni_M]}
    exp_source.data = {'posterior': [L_dict[N] * exp_M]}
    
slider.on_change('value', callback)

layout = column(slider, row(uni_p, exp_p))
output_path = Path.cwd().joinpath('priors_posteriors.html').as_posix()
output_file(output_path, title='Bayesian')
curdoc().add_root(layout)