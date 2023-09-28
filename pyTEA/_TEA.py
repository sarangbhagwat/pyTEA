# -*- coding: utf-8 -*-
# pyTEA: A tool to enable techno-economic analysis (TEA) in Python.
# Copyright (C) 2023-2024, Sarang S. Bhagwat <sarangb2@illinois.edu>
# 
# This module is under the MIT open-source license. See 
# github.com/sarangbhagwat/pyTEA/LICENSE.txt
# for license details.
"""
@author: sarangbhagwat
The input arguments for the TEA class are based largely on BioSTEAM's _tea.py module.
(https://github.com/BioSTEAMDevelopmentGroup/biosteam)
"""
import numpy as np
import scipy
import pandas as pd
brentq = scipy.optimize.brentq

class TEA():
    
    def __init__(
                self, 
                
                IRR: float, 
                project_duration, 
                
                purchase_cost,
                hourly_variable_operating_cost,
                
                hourly_product_flows,
                product_prices,
                
                other_costs_across_project_duration = None,
                
                hourly_fixed_operating_cost = None,
                
                inflation_rate = 0.,
                
                depreciation_schedule = 'Linear', 
                
                annual_operating_hours = 0.9 * 365 * 24,
                           
                income_tax = 0.35,
                incentives = 0., # annual amount
                
                lang_factor = 1.,
                construction_schedule = [1.,],
                
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
                
                labor_cost = 10 * 100_000,
                fringe_benefits = 0.40,
                supplies = 0.20,
                
                ):
        #: Project duration (years).
        self.project_duration = project_duration
        
        #: Depreciation schedule ('Linear' or user-specified schedule as a list of capital cost fractions across project duration).
        self.depreciation_schedule = depreciation_schedule
        
        #: Construction schedule (list as capital cost fractions each year; length may be less than the project duration).
        self.construction_schedule = construction_schedule
        
        #: Time during which the facility is starting up (months).
        self.startup_months = startup_months
        
        #: Total purchase cost of all equipment.
        self.purchase_cost = purchase_cost
        
        #: Hourly operating cost from the facility's input material and energy balance flows.
        self.hourly_variable_operating_cost = hourly_variable_operating_cost
        
        #: Hourly fixed operating cost; if not specified, this will be estimated based on self.FOC
        self.hourly_fixed_operating_cost = hourly_fixed_operating_cost
        
        #: Any other costs incurred over the project duration (list of costs across project duration).
        self._other_costs_across_project_duration = other_costs_across_project_duration
        
        #: Hours of operation per year.
        self.annual_operating_hours = annual_operating_hours
        
        #: Product flow (list of hourly mass, energy, or other flows).
        self.hourly_product_flows = hourly_product_flows
        
        #: Product selling prices (list of prices per numerator of the hourly_product_flows units; same order as hourly_product_flows)
        self.product_prices = product_prices
        
        #: Inflation rate (fraction).
        self.inflation_rate: float = inflation_rate
        
        #: Internal rate of return (fraction).
        self.IRR: float = IRR
        
        #: Combined federal and state income tax rate (fraction).
        self.income_tax: float = income_tax
        
        #: Annual incentives ($)
        self.incentives = incentives
        
        #: Lang factor (purchase cost multiplied by the Lang factor gives fixed capital investment).
        self.lang_factor: float = lang_factor
        
        #: Fraction of fixed operating costs incurred during startup.
        self.startup_FOC_frac: float = startup_FOC_frac
        
        #: Fraction of variable operating costs incurred during startup.
        self.startup_VOC_frac: float = startup_VOC_frac
        
        #: Fraction of sales achieved during startup.
        self.startup_sales_frac: float = startup_sales_frac
        
        #: Working capital as a fraction of fixed capital investment.
        self.WC_over_FCI: float = WC_over_FCI
        
        #: Yearly interest of capital cost financing as a fraction.
        self.finance_interest: float = finance_interest
        
        #: Number of years the loan is paid for.
        self.finance_years: int = finance_years
        
        #: Fraction of capital cost that needs to be financed.
        self.finance_fraction: float = finance_fraction
        
        #: Property tax rate (fraction of capital cost).
        self.property_tax: float = property_tax
        
        #: Property insurance annual cost (fraction of capital cost).
        self.property_insurance: float = property_insurance
        
        #: Property maintenance annual cost (fraction of capital cost).
        self.maintenance: float = maintenance
        
        #: Property administration annual cost (fraction of capital cost).
        self.administration: float = administration
        
        #: Labor cost.
        self.labor_cost = labor_cost
        
        #: Cost of fringe benefits (fraction of labor cost).
        self.fringe_benefits = fringe_benefits
        
        #: Cost of supplies (fraction of labor cost).
        self.supplies = supplies

    def get_initial_cashflow_array(self):
        return np.array([0 for i in range(self.project_duration)])
    
    def get_cashflow_array(self):
        """Get the cash flow in current dollars."""
        project_duration = self.project_duration
        
        # estimate depreciation
        depreciation = self.get_depreciation_flow()
        
        # estimate taxable cashflow
        taxable_cashflow = self.get_initial_cashflow_array()
        # !!! Here, add code to estimate the taxable cashflow
        
        #
        self.taxable_cashflow = taxable_cashflow
        
        # estimate tax
        tax_flow=np.zeros(project_duration)
        tax_indices = taxable_cashflow > 0
        tax_flow[tax_indices] = self.income_tax * taxable_cashflow[tax_indices]
        self.tax_flow = tax_flow
        
        # estimate net earnings
        self.net_earnings = net_earnings = taxable_cashflow + self.get_incentives_flow() - tax_flow
        
        # estimate nontaxable cashflow
        nontaxable_cashflow = self.get_initial_cashflow_array()
        # !!! Here, add code to estimate the nontaxable cashflow
        
        #
        self.nontaxable_cashflow = nontaxable_cashflow
        
        # total cashflow
        total_cashflow = net_earnings + nontaxable_cashflow
    
        return total_cashflow
    
    @property
    def discount_rate(self):
        """Get the inflation-adjusted discount rate."""
        return (1.+self.IRR)/(1.+self.inflation_rate) - 1.
    
    @property
    def P_over_F_factor_array(self):
        """Get an array (across the project duration) of P/F factors."""
        return 1/(1.+self.discount_rate)**np.array([i for i in range(self.project_duration)])
    
    def get_NPV_given_IRR(self, IRR):
        """Get NPV at a given IRR."""
        self.IRR = IRR
        # get total casfhlow as present value
        self.present_value_cashflow = present_value_cashflow =\
            self.get_cashflow_array() * self.P_over_F_factor_array
        # get net present value
        NPV = present_value_cashflow.sum()
        return NPV
    
    def get_IRR_given_NPV(self, 
                          NPV, 
                          IRR_lb=0., 
                          IRR_ub=10.):
        """Get IRR for a given NPV."""
        objective_func = lambda x: self.get_NPV_given_IRR(IRR=x) - NPV
        try: 
            self.IRR = IRR = brentq(objective_func, IRR_lb, IRR_ub, xtol=1e-5)
            return IRR
        except ValueError:
            raise ValueError(f'Cannot solve IRR; objective function for NPV = {NPV} at IRR bounds {IRR_lb} and {IRR_ub} does not have opposite signs ({objective_func(IRR_lb)} and {objective_func(IRR_ub)}).')
        
    
    def get_MPSP_given_IRR(self,
                            IRR,
                            product_index=0,
                            desired_NPV=0,
                            MPSP_lb=0.,
                            MPSP_ub=100.):
        """Get MPSP for a given IRR."""
        get_NPV_given_IRR = self.get_NPV_given_IRR
        def objective_func(product_selling_price, 
                           product_index=product_index, 
                           IRR=IRR, 
                           desired_NPV=desired_NPV):
            self.product_prices[product_index] = product_selling_price
            return get_NPV_given_IRR(IRR) - desired_NPV
        try: 
            MPSP = brentq(objective_func, MPSP_lb, MPSP_ub, xtol=1e-5)
            return MPSP
        except ValueError:
            raise ValueError(f'Cannot solve MPSP; objective function for NPV = {desired_NPV} at MPSP bounds {MPSP_lb} and {MPSP_ub} does not have opposite signs ({objective_func(MPSP_lb)} and {objective_func(MPSP_ub)}).')
    
    @property
    def FCI(self):
        """Get the fixed capital investment."""
        return self.purchase_cost * self.lang_factor
    
    def get_FCI_flow(self):
        """Get the cash flow of fixed capital investment throughout the project duration."""
        FCI = self.FCI
        project_duration = self.project_duration
        construction_schedule = np.array(list(self.construction_schedule) +
                                         [0 for i in range(project_duration - len(self.construction_schedule))]
                                         )
        return FCI*construction_schedule
    
    @property
    def FOC(self):
        """Get the annual fixed operating cost."""
        if self.hourly_fixed_operating_cost:
            return self.hourly_fixed_operating_cost * self.annual_operating_hours
        return (self.FCI*(self.property_tax + self.property_insurance
                     + self.maintenance + self.administration)
                + self.labor_cost*(1+self.fringe_benefits+self.supplies))
    
    def get_FOC_flow(self):
        """Get the cash flow of fixed operating costs throughout the project duration."""
        FOC = self.FOC
        startup_months, startup_FOC_frac = self.startup_months, self.startup_FOC_frac
        startup_year = len(self.construction_schedule) - 1
        FOC_flow = self.get_initial_cashflow_array()
        FOC_flow = FOC_flow + FOC
        
        FOC_flow = list(FOC_flow)
        startup_year_startup_portion = startup_months/12
        startup_year_FOC_factor = (startup_year_startup_portion * startup_FOC_frac
                       + (1-startup_year_startup_portion) * 1)
            
        FOC_flow[startup_year+1] = startup_year_FOC_factor * FOC
        for i in range(startup_year+1):
            FOC_flow[i] = 0
        return np.array(FOC_flow)
    
    @property
    def VOC(self):
        """Get the annual variable operating cost."""
        VOC = 0.
        # !!! Write code here
        
        #
        return VOC
    
    def get_VOC_flow(self):
        """Get the cash flow of variable operating costs throughout the project duration."""
        VOC = self.VOC
        startup_months, startup_VOC_frac = self.startup_months, self.startup_VOC_frac
        startup_year = len(self.construction_schedule) - 1
        VOC_flow = self.get_initial_cashflow_array()
        VOC_flow = VOC_flow + VOC
        
        VOC_flow = list(VOC_flow)
        startup_year_startup_portion = startup_months/12
        startup_year_VOC_factor = (startup_year_startup_portion * startup_VOC_frac
                       + (1-startup_year_startup_portion) * 1)
            
        VOC_flow[startup_year+1] = startup_year_VOC_factor * VOC
        for i in range(startup_year+1):
            VOC_flow[i] = 0
        return np.array(VOC_flow)
    
    @property
    def sales(self):
        """Get annual sales."""
        return np.array(self.product_prices) * np.array(self.hourly_product_flows) *\
            self.annual_operating_hours
    
    def get_sales_flow(self):
        """Get the cash flow of sales throughout the project duration."""
        sales = sum(self.sales)
        startup_months, startup_sales_frac = self.startup_months, self.startup_sales_frac
        startup_year = len(self.construction_schedule) - 1
        sales_flow = self.get_initial_cashflow_array()
        sales_flow = sales_flow + sales
        sales_flow = list(sales_flow)
        startup_year_startup_portion = startup_months/12
        startup_year_sales_factor = (startup_year_startup_portion * startup_sales_frac
                       + (1-startup_year_startup_portion) * 1)
            
        sales_flow[startup_year+1] = startup_year_sales_factor * sales
        for i in range(startup_year+1):
            sales_flow[i] = 0
        return np.array(sales_flow)
 
    def get_depreciation_flow(self):
        """Get the cash flow of depreciation throughout the project duration."""
        depreciation_schedule = self.depreciation_schedule
        total_depreciable_capital = self.FCI
        if depreciation_schedule == 'Linear':
            project_duration = self.project_duration
            annual_depreciation_fraction = 1/project_duration
            return annual_depreciation_fraction * total_depreciable_capital *\
                np.ones(project_duration)
        elif type(depreciation_schedule) == list:
            return np.array([i*total_depreciable_capital for i in depreciation_schedule])
    
    @property
    def loan_principal(self):
        return self.finance_fraction * self.FCI
    
    def get_loan_principal_flow(self):
        """Get the cash flow of loan principal revenue throughout the project duration."""
        return self.loan_principal *\
            np.array(
                    list(self.construction_schedule) +
                    [0 for i in range(self.project_duration-len(self.construction_schedule))]
                    )
    
    def get_loan_interest_only_payments_flow(self):
        """Get the cash flow of loan interest-only payments throughout the project duration."""
        self.loan_payment_start_year = years = min(len(self.construction_schedule), self.finance_years)
        loan_principal_flow = self.get_loan_principal_flow()
        interest_rate = self.finance_interest
        flow = [0 for i in range(self.project_duration)]
        current_loan_principal = 0
        for y in range(years):
            current_loan_principal += loan_principal_flow[y]
            flow[y] = interest_rate*current_loan_principal
        return np.array(flow)
    
    def get_loan_payments_flow(self):
        """Get the cash flow of loan payments throughout the project duration."""
        finance_interest, finance_years, finance_fraction =\
            self.finance_interest, self.finance_years, self.finance_fraction
        loan_amount = finance_fraction * self.FCI
        
        loan_payment_start_year = self.loan_payment_start_year
        
        yearly_loan_payment = get_annualized_value(loan_amount, 
                                                   finance_years-loan_payment_start_year, 
                                                   finance_interest)
        
        flow = [0 for i in range(self.project_duration)]
    
        for y in range(loan_payment_start_year, finance_years):
            flow[y] = yearly_loan_payment
        
        return flow
    
    def get_incentives_flow(self):
        """Get the cash flow of tax incentives throughout the project duration."""
        incentives = self.incentives
        return incentives* np.ones(self.project_duration)
    
    def get_working_capital_flow(self):
        """Get the cash flow of working capital throughout the project duration."""
        flow = list(self.get_initial_cashflow_array())
        flow[0] = self.WC_over_FCI * self.FCI
        return np.array(flow)
    
    @property
    def other_costs_across_project_duration(self):
        if self._other_costs_across_project_duration:
            return self._other_costs_across_project_duration
        return np.zeros(self.project_duration)
    
    def get_other_costs_across_project_duration_flow(self):
        """Get the cash flow of other user-specified costs throughout the project duration."""
        return np.array(self.other_costs_across_project_duration)
        
    def get_cashflow_report(self, filename='cashflow_report.xlsx'):
        """Get a full report for cash flow across the project duration."""
        VOC_flow = self.get_VOC_flow()
        FOC_flow = self.get_FOC_flow()
        sales_flow =  self.get_sales_flow()
        
        other_costs_flow = self.get_other_costs_across_project_duration_flow()
        
        tax_flow = self.tax_flow
        incentives_flow = self.get_incentives_flow()
        
        loan_principal_flow = self.get_loan_principal_flow()
        loan_interest_only_payments_flow = self.get_loan_interest_only_payments_flow()
        loan_payments_flow = self.get_loan_payments_flow()
        
        FCI_flow =  self.get_FCI_flow()
        WC_flow = self.get_working_capital_flow()
        
        net_earnings = self.net_earnings
        cash_flow = self.get_cashflow_array()
        
        discount_factor_array = self.P_over_F_factor_array
        
        present_value_flow = self.present_value_cashflow
        
        cumulative_present_value_flow = present_value_flow.cumsum()
        
        cashflow_dict = {
            'Fixed capital investment': FCI_flow,
            'Working capital': WC_flow,
            'Fixed operating cost': FOC_flow,
            'Variable operating cost': VOC_flow,
            'Other costs': other_costs_flow,
            'Loan': loan_principal_flow,
            'Loan interest-only payment': loan_interest_only_payments_flow,
            'Loan payment': loan_payments_flow,
            'Tax': tax_flow,
            'Incentives': incentives_flow,
            'Sales': sales_flow,
            'Net earnings': net_earnings,
            'Cash flow': cash_flow,
            'Discount factor': discount_factor_array,
            'Net present value': present_value_flow,
            'Cumulative net present value': cumulative_present_value_flow,
            }
        
        cashflow_df = pd.DataFrame(cashflow_dict)
        cashflow_df.to_excel(filename)
        
        return cashflow_df
    
#%% Value conversion functions

def get_present_value(future_value, year, interest_rate):
    """Get the present value given a future value, 
    number of years from the present, and interest rate."""
    present_value = 1
    # !!! Write code here
    
    #
    return present_value

def get_future_value(present_value, year, interest_rate):
    """Get the future value given a present value, 
    number of years from the present, and interest rate."""
    future_value = 1
    # !!! Write code here
    
    #
    return future_value

def get_annualized_value(present_value, years, interest_rate):
    """Get the annualized value given a present value, 
    number of years from the present, and interest rate."""
    annualized_value = 1
    # !!! Write code here
    
    #
    return annualized_value

