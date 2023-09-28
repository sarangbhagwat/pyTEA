# -*- coding: utf-8 -*-
# pyTEA: A tool to enable techno-economic analysis (TEA) in Python.
# Copyright (C) 2023-2024, Sarang S. Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/sarangbhagwat/pyTEA/LICENSE.txt
# for license details.
"""
@author: sarangbhagwat
"""
from pyTEA import TEA

#%% Create simple example design basis equations

def get_reactor_purchase_cost(V):
    C = 1
    # !!! Write code here
    
    #
    return C

def get_power_required(V):
    P = 1
    # !!! Write code here
    
    #
    return P

def get_hourly_variable_operating_cost(A_flow, A_price,
                                       B_flow, B_price,
                                       electricity_flow, electricity_price):
    hourly_VOC = 1
    # !!! Write code here
    
    #
    return hourly_VOC

#%% Use example design basis equations

t = 6 # h
A_flow = 250 # kg/h
B_flow = 250 # kg/h
C_flow = 300 # kg/h
D_flow = 200 # kg/h

constant_density = 1000 # kg/m3
Q = (C_flow + D_flow) / constant_density
V = t * Q
power_required = get_power_required(V=V)

A_price = 1.5 # $/kg
B_price = 1.2 # $/kg
C_price = 4.2 # $/kg
D_price = 1.1 # $/kg

electricity_price = 0.07 # $/kWh

hourly_variable_operating_cost = get_hourly_variable_operating_cost(
                                       A_flow=A_flow, A_price=A_price,
                                       B_flow=B_flow, B_price=B_price,
                                       electricity_flow=power_required, 
                                       electricity_price=electricity_price)

reactor_purchase_cost = get_reactor_purchase_cost(V=V)

#%% Initialize TEA

example_TEA = TEA(
    IRR = 0.10, 
    project_duration = 40, 
    
    purchase_cost = reactor_purchase_cost,
    hourly_variable_operating_cost = hourly_variable_operating_cost,
    
    hourly_product_flows = [C_flow, D_flow],
    product_prices = [C_price, D_price],
    
    depreciation_schedule = 'Linear', 
    
    annual_operating_hours = 0.9 * 365 * 24,
               
    income_tax = 0.15,
    incentives = 0,
    
    lang_factor = 1.5, 
    construction_schedule = [0.5, 0.25, 0.25,],
    
    startup_months = 6, 
    startup_FOC_frac = 0.1, 
    startup_VOC_frac =  0.1,
    startup_sales_frac = 0.1, 
    WC_over_FCI = 0.05,  
    
    finance_interest = 0.05,
    finance_years = 8, 
    finance_fraction = 0.2,
    
    property_tax = 0.05,
    property_insurance = 0.02,
    maintenance = 0.04,
    administration = 0.01,
    
    labor_cost = 10 * 140_000,
    fringe_benefits = 0.40,
    supplies = 0.20,
    )

#%% Solve TEA

IRR_at_NPV_0 = example_TEA.get_IRR_given_NPV(0)
print(f'IRR at NPV 0 and product A price of $4.2/kg is {round(100*IRR_at_NPV_0, 2)}%.')
example_TEA.get_cashflow_report('cashflow_report_solved_IRR_at_price_4.2.xlsx')

MPSP_at_IRR_15 = example_TEA.get_MPSP_given_IRR(0.15, product_index=0)
print(f'Minimum selling price of product A at NPV 0 is ${round(100*MPSP_at_IRR_15, 2)}/kg.')
example_TEA.get_cashflow_report('cashflow_report_solved_MPSP_at_IRR_0.15.xlsx')

