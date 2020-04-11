#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 09:42:50 2020

@author: jishnu
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

#%%
here = os.getcwd()


#git clone "https://github.com/datameet/covid19"

#os.system('../covid19/') # going into the data directory
#os.system('git fetch')  # updating the data (fteching updates from the source repo)
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
data_ind = pd.read_json('../covid19/data/all_totals.json', orient='records')

#data_ind = pd.io.json.json_normalize(data_ind['rows'])
#with open('../covid19/data/all_totals.json', 'r') as f:
#    data = json.load(f)
#df = pd.DataFrame(data)
#%%

states = list(set(df['value.state']))

# setting up full names of states
state_dict  = {
'ut':"Uttarakhand",
'ct':"Chhattisgarh",
'tr':"Tripura",
'pb':"Punjab",
'jh':"Jharkhand",
'or':"Odisha",
'ka':"Karnataka",
'mh':"Maharashtra",
'tn':"Tamil Nadu",
'as':"Assam",
'jk':"Jammu and Kashmir",
'mz':"Mizoram",
'rj':"Rajasthan",
'tg':"Telangana",
'wb':"West Bengal",
'up':"Uttar Pradesh",
'hr':"Haryana",
'br':"Bihar",
'py':"Puducherry",
'gj':"Gujarat",
'ar':"Arunachal Pradesh",
'la':"Ladakh",
'kl':"Kerala",
'ch':"Chandigarh",
'mp':"Madhya Pradesh",
'an':"Andaman and Nicobar Islands",
'ga':"Goa",
'dl':"Delhi",
'hp':"Himachal Pradesh",
'mn':"Manipur",
'ap':"Andhra Pradesh",
}

#%%

class State:
    """This class provides functions to filter, organise and visualize statewise data for Covid-19"""

    def __init__(self, df, state, db=None, st_abbr=None, time=None,
                 conf=None, cure=None, deth=None, conf_count=None,
                 cure_count=None, deth_count=None, fatality_rate=None,
                 daily_conf=None, daily_cure=None, daily_death=None):

        '''Initializing the values'''

        self.st_abbr = state
        self.state   = state_dict[state]

        Filter = df[(df['value.state'] == self.st_abbr)]

        self.db = Filter.loc[Filter.groupby(lambda x: Filter['value.report_time'][x].day)['value.report_time'].idxmax()]
        self.db = self.db.sort_values(['value.report_time'])

        del Filter

        self.time          = self.db['value.report_time']
        self.conf          = list(self.db['value.confirmed'])
        self.cure          = list(self.db['value.cured'])
        self.deth          = list(self.db['value.death'])

        self.conf_count    = max(self.conf)
        self.cure_count    = max(self.cure)
        self.deth_count    = max(self.deth)

        self.fatality_rate = self.deth_count*100/self.conf_count
        self.daily_conf    = [0]+[self.conf[i]-self.conf[i-1] for i in range(1,len(self.conf))]
        self.daily_cure    = [0]+[self.cure[i]-self.cure[i-1] for i in range(1,len(self.cure))]
        self.daily_death   = [0]+[self.deth[i]-self.deth[i-1] for i in range(1,len(self.deth))]


    def get_details(self):


        details = {'State':self.state,
                   'confirmed':self.conf_count,
                   'cured':self.cure_count,
                   'deaths':self.deth_count,
                   'fatality_rate':self.fatality_rate
                    }
        return details

#%%

def plot_summary(state):

    Filter = df[(df['value.state'] == state)]
    st = state
    state  = state_dict[state] # getting the full form

    fl = Filter.loc[Filter.groupby(lambda x: Filter['value.report_time'][x].day)['value.report_time'].idxmax()]
    fl = fl.sort_values(['value.report_time'])

    time = fl['value.report_time']
    conf = fl['value.confirmed']
    cure = fl['value.cured']
    deth = fl['value.death']

    confirm = conf.max()
    cured_c = cure.max()
    deaths  = deth.max()
    fatality_rate = deaths*100/confirm

    lst = list(conf)
    daily_conf = [0]+[lst[i]-lst[i-1] for i in range(1,len(lst))]

    lst = list(cure)
    daily_cure = [0]+[lst[i]-lst[i-1] for i in range(1,len(lst))]

    lst = list(deth)
    daily_deth = [0]+[lst[i]-lst[i-1] for i in range(1,len(lst))]

    try:
        growthrate = ((lst[-1]/lst[-2]) - 1)*100
#        growthrate = ((daily_conf[-1]/daily_conf[-3])**.33 - 1)*100
    except:
        growthrate = 0


    plt.style.use('seaborn')
    fig, ax = plt.subplots(3, 1,figsize=(8,8),sharex=True,
                           gridspec_kw={'height_ratios': [2.1, 2.4, 1]})

    ax[0].set_title(state.upper(),fontsize=20)

    ax[0].plot(time, conf, 'C0-o',lw=5,ms=10,
               label='confirmed cases ({})'.format(confirm))

    ax[0].plot(time, cure,'C1-p',lw=4,ms=10,
               label='recovered cases ({})'.format(cured_c))

    ax[0].plot(time, deth,'C2-v',alpha=.6,
               label='deaths ({})'.format(deaths))

    ax[0].fill_between(time,cure,deth,facecolor='C1',alpha=0.2)

    ax[0].fill_between(time,deth,facecolor='C2',alpha=0.2,
                       label='fatality rate ({:0.2f}%)'.format(fatality_rate))

    ax[0].fill_between(time,conf,cure,facecolor='C0',alpha=0.1,
                       label='Growth rate ({:.2f}%)'.format(growthrate))

#    ax[0].set_xlabel('Date')
    ax[0].set_ylabel('Numbers')
    #ax[0].set_ylim(0, 800)
    ax[0].set_xticks(['2020-03-15','2020-03-30','2020-04-14'])
    ax[0].set_xlim('2020-03-08 12:00:00+0530','2020-04-13')

    ax[0].legend(loc=2,fontsize=15,frameon=True,fancybox=True,
                 framealpha=.7,facecolor='white', borderpad=1)


    ax[1].set_title("Log scale")

    ax[1].plot(time,conf,'C0-o',lw=5,ms=10,
               label='confirmed cases ({})'.format(confirm))

    ax[1].plot(time,cure,'C1-p',lw=4,ms=10,
               label='recovered cases ({})'.format(cured_c))

    ax[1].plot(time,deth,'C2-v',alpha=.6,
               label='deaths ({})'.format(deaths))

    ax[1].fill_between(time,conf,cure,facecolor='C0',alpha=0.1)
    ax[1].fill_between(time,cure,deth,facecolor='C1',alpha=0.2)
    ax[1].fill_between(time,deth,facecolor='C2',alpha=0.2)

#    ax[1].set_xlabel('Date')
    ax[1].set_ylabel('Numbers')
    ax[1].set_yscale('symlog')
    ax[1].set_yticks([10**i for i in range(4)])
    ax[1].set_yticklabels(['{:2d}'.format(10**i) for i in range(4)])
    ax[1].set_ylim(0,10**4)

    ax[1].set_xticks(['2020-03-15','2020-03-30','2020-04-14'])
    ax[1].set_xlim('2020-03-08 12:00:00+0530','2020-04-14')


    ax[2].set_title('Daily Cases')
    ax[2].bar(time, daily_conf)#,daily_cure,daily_deth)
    ax[2].set_xticks(['2020-03-15','2020-03-30','2020-04-14'])
    ax[2].set_xticklabels(['15 March','30 March','14 April'])
    ax[2].set_xlim('2020-03-08 12:00:00+0530','2020-04-14')
    ax[2].set_xlabel('Date')

    fig.tight_layout()
    plt.savefig(f'plots/{st}.png',dpi=150)
#    plt.show()
    plt.close()

#%%
#plot_summary('kl')

#%%
with open('Intro.md','r') as intro:
    with open('README.md','w') as outfile:
        outfile.write(intro.read())
        for state in states:
            plot_summary(state)
            st     = state
            state  = state_dict[state]
            outfile.write(f'# {state} \n\n\centering\n\n![](plots/{st}.png){{width=70%}}\n\n\n')
#            outfile.write(f'# {state} \n\n\n![](plots/{st}.png)\n\n\n')
#        os.system('pandoc README.md -t beamer -o report.pdf')

#%%
details = []
for st in states:
    state_obj = State(df,st)
    details.append(state_obj.get_details())

db = pd.DataFrame(details)
db = db.sort_values(['confirmed'])
db['Total'] = db.confirmed+db.cured+db.deaths

#kerala = State(df,'kl')
#kerala.get_details()

#%%
cases  = list(db.confirmed)
cured  = list(db.cured)
death  = list(db.deaths)
tot = list(db.Total)

ax = db[['State','deaths', 'confirmed', 'cured']].plot(kind='barh',
                                   figsize=(10,16), width=.5, fontsize=13,
                                   colors=['C2', 'C0', 'C1'], stacked=True,
                                   align='center')
for i in range(len(tot)):
    ax.text(tot[i]+5,i-.15,'{:<4d}'.format(cases[i]), fontsize=12)
    ax.text(tot[i]+120,i+.05,'{}'.format(cured[i]), fontsize=10, color='g')
    ax.text(tot[i]+120,i-.4,'{}'.format(death[i]), fontsize=9, color='r')

ax.set_title('Statewise cases')
ax.set_xlim(0,max(tot)+400)
ax.set_alpha(0.8)
ax.set_yticklabels(list(db.State))

# create a list to collect the plt.patches data
#patch = [(i.get_width(),i.get_y()) for i in ax.patches]

#for i in range(len(tot)):
#    if tot[i] >= 100:
#        ax.text(death[i]+2,i-.15,death[i], fontsize=12, color='white')
##        ax.text(death[i]+2,i,death[i], fontsize=11, color='white')
##        ax.text(tot[i]+5,i,cases[i], fontsize=11)
#    else:
#        ax.text(tot[i]+5,i-.15,cases[i], fontsize=11)


#for v in db.Total:
#    # get_width pulls left or right; get_y pushes up or down
#    ax.text(i.get_width()+4, i.get_y(), i.get_width(), fontsize=10.5)

ax.legend(loc=5,fontsize=12,frameon=True,fancybox=True,
         framealpha=.7,facecolor='white', borderpad=1)

plt.savefig(f'plots/summary.png',dpi=150)
plt.show()
plt.close()

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

