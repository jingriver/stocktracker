#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (c) Elvis Pf￼tzenreuter, INdT (Nokia Institute of Technology)
# All Rights Reserved
# This is free software under the LGPL license.

# Version: 0.01 (2007/09/12)

# TODO
# * Packaging

import math
from datetime import datetime
import time
import os

#import anydbm
#import gtk
#import gobject
#import pango
#
#is_hildon = 1
#try:
#    import hildon
#except ImportError:
#    is_hildon = 0

default_strikes = [49.58, 51.58, 53.58, 55.58, 57.58]
default_spot = 55.01
default_vola = 35.00
default_expiration = time.time()
default_interest = 11.25
#file = os.getenv("HOME", default="/home/user")+"/callculator.dbm"
#dbm = anydbm.open(file, 'c')
#try:
#    for i in range(0, len(default_strikes)):
#        default_strikes[i] = float(dbm["strike%d" % i])
#    default_spot = float(dbm["spot"])
#    default_vola = float(dbm["vola"])
#    default_expiration = float(dbm["expiration"])
#    default_interest = float(dbm["interest"])
#except KeyError:
#    pass
#dbm.close()

kd1 = 0.0498673470
kd3 = 0.0032776263
kd5 = 0.0000488906
kd2 = 0.0211410061
kd4 = 0.0000380036
kd6 = 0.0000053830

#strike_rows = []
strikes = []

def N(x):
    # cummulative distribution
    if x < 0:
        return 1 - N(-x)
    n = 1.0 - 0.5*(1 + kd1*x + kd2*x**2 + kd3*x**3 + kd4*x**4 + kd5*x**5 + kd6*x**6)**-16
    return n

def dN(x):
    # derivative of N(x)
    n = math.exp(-(x**2/2))
    n /= (2*math.pi)**0.5
    return n
    
def bs_call(spot, strike, interest, time, volatility):
    d1 = bs_d1(spot, strike, interest, time, volatility)
    nd1 = N(d1)
    d2 = bs_d2(spot, strike, interest, time, volatility)
    nd2 = N(d2)
    premium = nd1*spot - math.exp(-interest*time)*nd2*strike
    return premium
    
def bs_d1(spot, strike, interest, time, volatility):
    if volatility < 0.0000001:
        return 9999999999.9;
    x = math.log(spot/strike) + (interest + volatility**2/2) * time
    x /= volatility*(time**0.5)
    return x

def bs_d2(spot, strike, interest, time, volatility):
    x = bs_d1(spot, strike, interest, time, volatility) - volatility*time**0.5
    return x

def bs_delta(spot, strike, interest, time, volatility):
    x = N(bs_d1(spot, strike, interest, time, volatility))
    return x

def bs_gamma(spot, strike, interest, time, volatility):
    d1 = bs_d1(spot, strike, interest, time, volatility)
    x = dN(d1)
    x /= spot * volatility * time ** 0.5
    return x

def bs_vega(spot, strike, interest, time, volatility):
    d1 = bs_d1(spot, strike, interest, time, volatility)
    x = spot*(time**0.5)*dN(d1)
    return x

def bs_theta(spot, strike, interest, time, volatility):
    d1 = bs_d1(spot, strike, interest, time, volatility)
    d2 = bs_d2(spot, strike, interest, time, volatility)
    x = - spot*dN(d1)*volatility
    x /= 2*(time**0.5)
    x -= interest*strike*math.exp(-interest*time)*N(d2)
    return x

def bs_rho(spot, strike, interest, time, volatility):
    d2 = bs_d2(spot, strike, interest, time, volatility)
    x = strike*time*math.exp(-interest*time)*N(d2)
    return x


def calcular(spot, strike, vola, interest, today, expiration):
    time = (expiration - today).days
    time /= 365.0

    premium = bs_call(spot, strike, interest, time, vola)
    delta = bs_delta(spot, strike, interest, time, vola)
    gamma = bs_gamma(spot, strike, interest, time, vola)
    vega  =  bs_vega(spot, strike, interest, time, vola)
    theta = bs_theta(spot, strike, interest, time, vola)

    # normalize
    theta = (theta/premium)/365.0  # % of change in premium per day
    vega = ((vega/100.0)/premium) # normalize to premium%

    return dict(spot=spot, strike=strike, premium=premium, delta=delta*100, gamma=gamma*100, vega=vega*100, theta=theta*100)

def str2datetime(strdate, fmt="%Y/%m/%d"):
    dtuple = time.strptime(strdate, fmt)
    return datetime(dtuple[0], dtuple[1], dtuple[2], dtuple[3], dtuple[4], dtuple[5])

today = datetime.today()
expiration = str2datetime("2008/4/27")
c = calcular(spot=default_spot, strike=default_strikes[0], vola=default_vola, interest=default_interest/100, today=today, expiration=expiration)
print c

#def limpa():
#    for strk in strikes:
#        if len(strk) > 1:
#            for i in strk[1:]:
#                i.set_text("")

#def calc(widget, data=None):
#    for strk in strikes:
#        spot = spot_button.get_value()
#        strike = strk[0].get_value()
#        intrinsic = spot - strike
#        if intrinsic < 0:
#            intrinsic = 0
#        vola = vola_button.get_value()/100
#        interest = interest_button.get_value()/100
#
#        today = time.time()
#        today = (int(today/86400.0)) * 86400.0 + 1.0 # normalize to 00:01 AM
#        e = expiration_button.get_date()
#        expiration = time.mktime((e[0], e[1]+1, e[2], 0, 0, 1, 0, 0, 0)) + 2.0 # 00:02 AM
#
#        if int((expiration - today) / 86400) <= 0:
#            limpa()
#            return
#
#        if len(strk) <= 1:
#            return
#
#        c = calcular(spot=spot, strike=strike, vola=vola, interest=interest, today=today, expiration=expiration)
#        strk[1].set_text("%.2f (%.2f)" % (c["premium"], intrinsic))
#        strk[2].set_text("%.1f%% P/S" % c["delta"])
#        strk[3].set_text("%.1f%% ?/S" % c["gamma"])
#        strk[4].set_text("%.1f%% P/V" % c["vega"])
#        strk[5].set_text("%.1f%% P/t" % c["theta"])

#def destroy(widget, data=None):
#    dbm = anydbm.open(file, 'c')
#    for i in range(0, len(default_strikes)):
#        dbm["strike%d" % i] = "%.2f" % strikes[i][0].get_value()
#    dbm["vola"] = "%.2f" % vola_button.get_value()
#    dbm["spot"] = "%.2f" % spot_button.get_value()
#    dbm["interest"] = "%.2f" % interest_button.get_value()
#    e = expiration_button.get_date()
#    dbm["expiration"] = "%f" % (time.mktime((e[0], e[1]+1, e[2], 0, 0, 1, 0, 0, 0)))
#    dbm.close()
#    gtk.main_quit()
#
#if is_hildon:
#    app = hildon.Program()
#    window = hildon.Window()
#    gtk.set_application_name("")
#    font = pango.FontDescription("Nokia Sans 12")
#    smallfont = pango.FontDescription("Nokia Sans 13")
#
#else:
#    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
#    window.set_border_width(5)
#    font = smallfont = None
#            
#window.set_title("Black-Scholes calculator")
#window.connect("destroy", destroy)
#main_layout = gtk.VBox()
#header = gtk.HBox()
#subheader = gtk.VBox()
#
#spot_box = gtk.HBox()
#spot_button = gtk.SpinButton(adjustment=gtk.Adjustment(value=default_spot, lower=0.0, upper=999.9, step_incr=0.01, page_incr=0.1, page_size=0.1), climb_rate=0.01, digits=2)
#spot_button.connect("value-changed", calc)
## spot_button.set_value(default_spot)
#spot_button.show()
#spot_label = gtk.Label()
#spot_label.set_text("Spot price (S) ")
#spot_label.show()
#spot_box.pack_start(spot_label)
#spot_box.pack_start(spot_button)
#spot_box.show_all()
#subheader.pack_start(spot_box)
#
#vola_box = gtk.HBox()
#vola_button = gtk.SpinButton(adjustment=gtk.Adjustment(value=default_vola, lower=0.0, upper=999.9, step_incr=0.1, page_incr=1.0, page_size=0.1), climb_rate=0.1, digits=2)
#vola_button.connect("value-changed", calc)
## vola_button.set_value(default_vola)
#vola_button.show()
#vola_label = gtk.Label()
#vola_label.set_text("Volatility %/year (V) ")
#vola_label.show()
#vola_box.pack_start(vola_label)
#vola_box.pack_start(vola_button)
#vola_box.show_all()
#subheader.pack_start(vola_box)
#
#interest_box = gtk.HBox()
#interest_button = gtk.SpinButton(adjustment=gtk.Adjustment(value=default_interest, lower=0.0, upper=99.00, step_incr=.25, page_incr=.25, page_size=.25), climb_rate=0.25, digits=2)
#interest_button.connect("value-changed", calc)
## interest_button.set_value(default_interest)
#interest_button.show()
#interest_label = gtk.Label()
#interest_label.set_text("Interest %/year ")
#interest_label.show()
#interest_box.pack_start(interest_label)
#interest_box.pack_start(interest_button)
#interest_box.show_all()
#subheader.pack_start(interest_box)
#
#expiration_box = gtk.HBox()
#expiration_button = gtk.Calendar()
#if font:
#    expiration_button.modify_font(font)
#expiration_button.connect("day-selected", calc)
## expiration_button.set_value(30)
#expiration_button.show()
## expiration_label = gtk.Label()
## expiration_label.set_text("Expiration (days) ")
## expiration_label.show()
## expiration_box.pack_start(expiration_label)
#t = time.gmtime(default_expiration)
#expiration_button.select_day(t[2])
#expiration_button.select_month(t[1]-1, t[0])
#expiration_box.pack_start(expiration_button)
#expiration_box.show_all()
#
#for K in default_strikes:
#    option_pack = gtk.HBox()
#    strike_rows.append(option_pack)
#    strike = []
#    strikes.append(strike)
#    strike_box = gtk.HBox()
#    strike_button = gtk.SpinButton(adjustment=gtk.Adjustment(value=K, lower=0.0, upper=999.9, step_incr=0.01, page_incr=0.1, page_size=0.1), climb_rate=0.01, digits=2)
#    strike.append(strike_button)
#    strike_button.connect("value-changed", calc)
#    # strike_button.set_value(K)
#    strike_button.show()
#    strike_box.pack_start(strike_button)
#    strike_box.show_all()
#    premium_entry = gtk.Entry()
#    delta_entry = gtk.Entry()
#    gamma_entry = gtk.Entry()
#    vega_entry = gtk.Entry()
#    theta_entry = gtk.Entry()
#    strike.append(premium_entry)
#    strike.append(delta_entry)
#    strike.append(gamma_entry)
#    strike.append(vega_entry)
#    strike.append(theta_entry)
#    if smallfont:
#        for w in strike[1:]:
#            w.modify_font(smallfont)
#            w.set_alignment(1)
#    option_pack.pack_start(strike_box)
#    option_pack.pack_start(premium_entry)
#    option_pack.pack_start(delta_entry)
#    option_pack.pack_start(gamma_entry)
#    option_pack.pack_start(vega_entry)
#    option_pack.pack_start(theta_entry)
#
#
#for s in strikes:
#    for ss in s[1:]:
#        ss.set_property("width-chars", 10)
#
#sp = gtk.Label()
#sp.set_text("   ")
#
#header.pack_start(subheader)
#header.pack_start(sp)
#header.pack_start(expiration_box)
#
#sp = gtk.Label()
#sp.set_text("   ")
#
#main_layout.pack_start(header)
#main_layout.pack_start(sp)
#rows = gtk.VBox()
#for p in strike_rows:
#    rows.pack_start(p)
#main_layout.pack_start(rows)
#
#window.add(main_layout)
#window.show_all()
#
#calc(None)
#
#gtk.main()
