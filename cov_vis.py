#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 09:42:50 2020

@author: jishnu
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%%
here = os.getcwd()


#git clone "https://github.com/datameet/covid19"

os.system('../covid19/') # going into the data directory
os.system('git fetch')  # updating the data (fteching updates from the source repo)
#https://github.com/datameet/covid19

os.chdir(here)
#%%

f = '../covid19/data/mohfw.json'

#with open(f,'r') as file:
#    data = '\n'.join([line for line in itertools.islice(file, 1, None)])

data = pd.read_json(f) # reading the json file

df = pd.io.json.json_normalize(data['rows']) # getting data from the json file
# i know its a little convolutedted here (found the solution after 40 minutes of searching :P)

df['value.report_time'] = pd.to_datetime(df['value.report_time'])

#%%

states = list(set(df['value.state']))
#%%
def plot_state_data(state):

    Filter = df[(df['value.state'] == state)]

    fl = Filter.loc[Filter.groupby(lambda x: Filter['value.report_time'][x].day)['value.report_time'].idxmax()]
    fl = fl.sort_values(['value.report_time'])

    time = fl['value.report_time']
    conf = fl['value.confirmed']
    cure = fl['value.cured']
    deth = fl['value.death']

    plt.style.use('seaborn')
    plt.figure(figsize=(10,6))
    plt.title(state.upper(),fontsize=20)
    plt.plot(time,conf,'C0-o',lw=5,ms=10,
             label='confirmed cases ({})'.format(conf.max()))
    plt.plot(time,cure,'C1-p',lw=4,ms=10,
             label='recovered cases ({})'.format(cure.max()))
    plt.plot(time,deth,'C2-v',alpha=.6,
             label='deaths ({})'.format(deth.max()))
    plt.fill_between(time,conf,cure,facecolor='C0',alpha=0.1)
    plt.fill_between(time,cure,deth,facecolor='C1',alpha=0.2)
    plt.fill_between(time,deth,facecolor='C2',alpha=0.2,
                     label='fatality rate ({:0.2f})'.format(deth.max()*100/conf.max()))
    plt.xlabel('Date')
    plt.ylabel('Numbers')
    plt.xticks(['2020-03-15','2020-03-30','2020-04-14','2020-04-29'])
    plt.xlim('2020-03-08','2020-04-14')
    plt.yscale('symlog')
    plt.ylim(0,10**4)
    plt.legend(loc=2,fontsize=15)
    plt.savefig(f'plots/{state}.png',dpi=120)
    plt.show()
    plt.close()

#%%

def plot_summary(state):

    Filter = df[(df['value.state'] == state)]

    fl = Filter.loc[Filter.groupby(lambda x: Filter['value.report_time'][x].day)['value.report_time'].idxmax()]
    fl = fl.sort_values(['value.report_time'])

    time = fl['value.report_time']
    conf = fl['value.confirmed']
    cure = fl['value.cured']
    deth = fl['value.death']
    fatality_rate = deth.max()*100/conf.max()

    lst = list(conf)
    daily_conf = [0]+[lst[i]-lst[i-1] for i in range(1,len(lst))]


#    lst = list(cure)
#    daily_cure = [0]+[lst[i]-lst[i-1] for i in range(1,len(lst))]
#
#    lst = list(deth)
#    daily_deth = [0]+[lst[i]-lst[i-1] for i in range(1,len(lst))]

    plt.style.use('seaborn')
    fig, ax = plt.subplots(3, 1,figsize=(8,8),sharex=True,
                           gridspec_kw={'height_ratios': [2, 2.5, 1]})

    ax[0].set_title(state.upper(),fontsize=20)
    ax[0].plot(time,conf,'C0-o',lw=5,ms=10,
               label='confirmed cases ({})'.format(conf.max()))
    ax[0].plot(time,cure,'C1-p',lw=4,ms=10,
               label='recovered cases ({})'.format(cure.max()))
    ax[0].plot(time,deth,'C2-v',alpha=.6,
               label='deaths ({})'.format(deth.max()))
    ax[0].fill_between(time,conf,cure,facecolor='C0',alpha=0.1)
    ax[0].fill_between(time,cure,deth,facecolor='C1',alpha=0.2)
    ax[0].fill_between(time,deth,facecolor='C2',alpha=0.2,
                       label='fatality rate ({:0.2f}%)'.format(fatality_rate))
#    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Numbers')
    ax[0].set_ylim(0,800)
    ax[0].set_xticks(['2020-03-15','2020-03-30','2020-04-14'])
    ax[0].set_xlim('2020-03-08 12:00:00+0530','2020-04-10 12:00:00+0530')
    ax[0].legend(loc=2,fontsize=15,frameon=True,fancybox=True,
                 framealpha=.7,facecolor='white', borderpad=1)

    ax[1].set_title("Log scale")
    ax[1].plot(time,conf,'C0-o',lw=5,ms=10,
               label='confirmed cases ({})'.format(conf.max()))
    ax[1].plot(time,cure,'C1-p',lw=4,ms=10,
               label='recovered cases ({})'.format(cure.max()))
    ax[1].plot(time,deth,'C2-v',alpha=.6,
               label='deaths ({})'.format(deth.max()))
    ax[1].fill_between(time,conf,cure,facecolor='C0',alpha=0.1)
    ax[1].fill_between(time,cure,deth,facecolor='C1',alpha=0.2)
    ax[1].fill_between(time,deth,facecolor='C2',alpha=0.2,
                       label='fatality rate ({:0.2f})'.format(deth.max()*100/conf.max()))
#    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Numbers')
    ax[1].set_yscale('symlog')
    ax[1].set_ylim(0,10**4)
    ax[1].set_xticks(['2020-03-15','2020-03-30','2020-04-14'])
    ax[1].set_xlim('2020-03-08 12:00:00+0530','2020-04-10 12:00:00+0530')

    ax[2].set_title('Daily Cases')
    ax[2].bar(time, daily_conf)#,daily_cure,daily_deth)
    ax[2].set_xticks(['2020-03-15','2020-03-30','2020-04-14'])
    ax[2].set_xticklabels(['15 March','30 March','14 April'])
    ax[2].set_xlim('2020-03-08 12:00:00+0530','2020-04-10 12:00:00+0530')
    ax[2].set_xlabel('Date')

    fig.tight_layout()
    plt.savefig(f'plots/{state}.png',dpi=120)
    plt.show()
    plt.close()
#%%
with open('Intro.md','r') as intro:
    with open('ReadMe.md','w') as outfile:
        outfile.write(intro.read())
        for state in states:
#            plot_summary(state)
            outfile.write(f'## {state} \n![{state}](plots/{state}.png)\n\n')


#%%

#%%
plot_summary('kl')
#%%
'''test code'''
#state = 'kl'
#Filter = df[(df['value.state'] == state)]
#
#fl = Filter.loc[Filter.groupby(lambda x: Filter['value.report_time'][x].day)['value.report_time'].idxmax()]
#fl = fl.sort_values(['value.report_time'])
##plt.style.use('seaborn')
##plt.figure(figsize=(12,8))
##plt.title(state.upper(),fontsize=20)
##plt.plot(fl['value.report_time'],fl['value.confirmed'],'-o')
##plt.xlim('2020-03-08 12:00:00+0530','2020-04-10 12:00:00+0530')
##plt.show()
##plt.close()
#
#lst = list(fl['value.confirmed'])
#daily_cases = [0]+[lst[i]-lst[i-1] for i in range(1,len(lst))]
#
#time = fl['value.report_time']
#conf = fl['value.confirmed']
#cure = fl['value.cured']
#deth = fl['value.death']


#%%
#plt.style.use('seaborn')
#plt.figure(figsize=(10,10))
#plt.title(state.upper(),fontsize=20)
#plt.plot(time,conf,'C0-o',lw=5,ms=10,
#         label='confirmed cases ({})'.format(conf.max()))
#plt.plot(time,cure,'C1-p',lw=4,ms=10,
#         label='recovered cases ({})'.format(cure.max()))
#plt.plot(time,deth,'C2-v',alpha=.6,
#         label='deaths ({})'.format(deth.max()))
#plt.fill_between(time,conf,cure,facecolor='C0',alpha=0.1)
#plt.fill_between(time,cure,deth,facecolor='C1',alpha=0.2)
#plt.fill_between(time,deth,facecolor='C2',alpha=0.2,
#                 label='fatality rate ({:0.2f})'.format(deth.max()*100/conf.max()))
#plt.xlabel('Date')
#plt.ylabel('Numbers')
#plt.ylim(0,800)
##plt.plot(time,daily_cases,'-o')
##plt.bar(time, daily_cases)
#plt.xticks(['2020-03-15','2020-03-30','2020-04-14'],fontsize=13)
#plt.xlim('2020-03-08 12:00:00+0530','2020-04-10 12:00:00+0530')
#plt.legend(loc=2,fontsize=15)
##plt.sharex(True)
#
#plt.subplot(212)
#plt.title("Log scale")
#plt.plot(time,conf,'C0-o',lw=5,ms=10,
#         label='confirmed cases ({})'.format(conf.max()))
#plt.plot(time,cure,'C1-p',lw=4,ms=10,
#         label='recovered cases ({})'.format(cure.max()))
#plt.plot(time,deth,'C2-v',alpha=.6,
#         label='deaths ({})'.format(deth.max()))
#plt.fill_between(time,conf,cure,facecolor='C0',alpha=0.1)
#plt.fill_between(time,cure,deth,facecolor='C1',alpha=0.2)
#plt.fill_between(time,deth,facecolor='C2',alpha=0.2,
#                 label='fatality rate ({:0.2f})'.format(deth.max()*100/conf.max()))
#plt.xlabel('Date')
#plt.ylabel('Numbers')
#plt.yscale('symlog')
#plt.ylim(0,10**4)
#plt.xticks(['2020-03-15','2020-03-30','2020-04-14'])
#plt.xlim('2020-03-08 12:00:00+0530','2020-04-10 12:00:00+0530')
##plt.legend(loc=2,fontsize=15)
##plt.sharex(True)
#
#plt.tight_layout()
#plt.show()
#plt.close()

