#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 00:42:04 2020

@author: jishnu
"""


# This is not a scientific forecast. For a sophisticated model, see:
# http://gabgoh.github.io/COVID/index.html -- which is explained at:
# https://medium.com/@tomaspueyo/coronavirus-the-hammer-and-the-dance-be9337092b56
# with a detailed exposition of the factors influencing projections.
# And for why such authentic epidemiological models simply can not
# exist yet because of too much uncertainty in a handful of such factors:
# https://fivethirtyeight.com/features/why-its-so-freaking-hard-to-make-a-good-covid-19-model/

# Detailed discussion: https://www.reddit.com/r/CoronavirusUS/comments/fqx8fn/ive_been_working_on_this_extrapolation_for_the/
# Animation: https://gl.speakclearly.info/static/covid.mp4
# Animation code: https://paste.pythondiscord.com/rajuzixoke.py

from pandas import read_csv, Timestamp, Timedelta, date_range
from numpy import log, exp, sqrt, clip, argmax, put
from scipy.special import erfc
from lmfit import Model
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import subplots
from matplotlib.ticker import StrMethodFormatter
from matplotlib.dates import ConciseDateFormatter, AutoDateLocator

#%%
def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def lognormal_c(x, s, mu, h): # x, sigma, mean, height
    return h * 0.5 * erfc(- (log(x) - mu) / (s * sqrt(2)))
    # https://en.wikipedia.org/wiki/Log-normal_distribution#Cumulative_distribution_function

#%%
def projection_plot(df):

    #lastday = df.index[-1] + Timedelta(30, 'd') # extrapolate 60 days

    lastday = pd.datetime(2020,11,1)

    plt.style.use('seaborn')
    fig, ax = subplots(figsize=(16,10))
    ax.set_title('India Covid Infections \n({})'.format(df.index[-1].date()),fontsize=18)

    nextday = df.index[-1] + Timedelta('1d')
    x = ((df.index - Timestamp('2020-01-01')) # independent
        // Timedelta('1d')).values # small day-of-year integers
    yi = df['Infected'].values # dependent
    yd = df['Dead'].values # dependent
    exrange = range((Timestamp(nextday)
        - Timestamp('2020-01-01')) // Timedelta('1d'),
        (Timestamp(lastday) + Timedelta('1d')
        - Timestamp('2020-01-01')) // Timedelta('1d')) # day-of-year ints
    indates = date_range(df.index[0], df.index[-1])
    exdates = date_range(nextday, lastday)

    ax.plot(indates, yi, 'C0', label='Infected : {:,.0f}'.format(df.Infected[-1]))
    ax.plot(indates, yd, 'C2', label='Dead     : {:,.0f}'.format(df.Dead[-1]))
    #ax.plot(indates, yi*0.0311, 'C4-o')

    im = Model(lognormal_c)
    iparams = im.make_params(s=0.3, mu=4.3, h=16.5)
    iparams['s'].min = 0; iparams['h'].min = 0
    iresult = im.fit(log(yi+1), iparams, x=x)
    print('---- Infections:\n' + iresult.fit_report())
    ax.plot(indates, exp(iresult.best_fit)-1, 'C0.', label='Infections fit')
    ipred = iresult.eval(x=exrange)
    ax.plot(exdates, exp(ipred)-1, 'C0--',
        label='Projected infections: {:,.0f}'.format(exp(ipred[-1])-1))
    iupred = iresult.eval_uncertainty(x=exrange, sigma=0.95) # 95% interval
    iintlow = clip(ipred-iupred, ipred[0], None)
    put(iintlow, range(argmax(iintlow), len(iintlow)), iintlow[argmax(iintlow)])
    ax.fill_between(exdates, exp(iintlow), exp(ipred+iupred), alpha=0.35, color='C0')

    dm = Model(lognormal_c)
    dparams = dm.make_params(s=0.2, mu=4, h=10) # initial guesses
    dparams['s'].min = 0; iparams['h'].min = 0
    dresult = dm.fit(log(yd+1), dparams, x=x)
    print('---- Deaths:\n' + dresult.fit_report())
    ax.plot(indates, exp(dresult.best_fit)-1, 'C2.', label='Deaths fit')
    dpred = dresult.eval(x=exrange)
    ax.plot(exdates, exp(dpred)-1, 'C2--',
        label='Projected deaths: {:,.0f}'.format(exp(dpred[-1])-1))
    dupred = dresult.eval_uncertainty(x=exrange, sigma=0.95) # 95% interval
    dintlow = clip(dpred-dupred, log(max(yd)+1), None)
    put(dintlow, range(argmax(dintlow), len(dintlow)), dintlow[argmax(dintlow)])
    ax.fill_between(exdates, exp(dintlow), exp(dpred+dupred), alpha=0.35, color='C2')
    #ax.fill_between(exdates, 0.029 * (exp(iintlow)), 0.029 * (exp(ipred+iupred)),
    #    alpha=0.35, color='g', label='Deaths from observed fatality rate')
    endDate = lastday
    ax.set_yscale('symlog') # semilog
    ax.set_ylim(10, 10**8)
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}')) # comma separators
    ax.set_ylabel('Numbers (in log scale)')
    ax.legend(loc="lower right",fontsize=14,ncol=3,frameon=True,fancybox=True,
              framealpha=.7,facecolor='white', borderpad=1)
    xtik = pd.date_range(start='2020-03-13',
                         end=endDate,
                         #end=pd.to_datetime('today')+pd.Timedelta('7 days'),
                         freq='15D')
    ax.set_xticks(xtik)
    ax.set_xticklabels(xtik.strftime('%B %d'))
    ax.set_xlim(df.index[0], endDate+Timedelta(1, 'd'))
    #ax.xaxis.set_major_formatter(ConciseDateFormatter(AutoDateLocator(), show_offset=False))
    ax.set_xlabel('95% prediction confidence intervals shaded')

    #fig.tight_layout()
    fig.savefig('t_plot/projection_{}.png'.format(df.index[-1].date()), bbox_inches='tight')

    print('Infections at end of period shown: {:,.0f}. Deaths: {:,.0f}.'.format(
        exp(ipred[-1])-1, exp(dpred[-1])-1))

    #plt.show()
    plt.clf()
    plt.close(fig)

#%%
df = read_csv('data/time_series.csv', parse_dates=['Date'], index_col='Date')

#%%
#db = df[21:]
#projection_plot(db)

#%%

df1 = df[21:]

for i in range(17,len(df1.index)+1):
    db = df1[:i]
    projection_plot(db)

#%%
os.system('convert -delay 100 t_plot/projection_* -delay 100 -loop 0 plots/prjct.gif')

#%%
#plt.plot(df.index,df['Dead'])
#plt.plot(df.index,df['Infected']*.033)
