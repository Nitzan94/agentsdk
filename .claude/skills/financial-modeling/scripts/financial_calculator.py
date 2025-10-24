#!/usr/bin/env python3
"""
ABOUTME: Core financial calculations module
ABOUTME: Provides IRR, NPV, FCF, and valuation computations

Financial calculator for DCF, NPV, IRR, and related financial metrics.
Handles both single calculations and array-based operations.
"""

from typing import List, Tuple, Union, Dict
from decimal import Decimal
import numpy as np
from scipy.optimize import fsolve


def calculate_irr(cash_flows: List[float], periods: List[int] = None, guess: float = 0.1) -> float:
    """
    Calculate Internal Rate of Return (IRR) for a series of cash flows.
    
    Args:
        cash_flows: List of cash flows (first is typically negative investment)
        periods: Optional list of period numbers (default: 0, 1, 2, ...)
        guess: Initial guess for IRR (default: 0.1 or 10%)
    
    Returns:
        IRR as decimal (e.g., 0.15 for 15%)
    
    Raises:
        ValueError: If cash flows are all same sign or calculation fails
    """
    if periods is None:
        periods = list(range(len(cash_flows)))
    
    if len(cash_flows) != len(periods):
        raise ValueError("cash_flows and periods must have same length")
    
    # Check if we have both positive and negative cash flows
    has_positive = any(cf > 0 for cf in cash_flows)
    has_negative = any(cf < 0 for cf in cash_flows)
    
    if not (has_positive and has_negative):
        raise ValueError("IRR requires both positive and negative cash flows")
    
    # Define NPV function where we solve for rate where NPV = 0
    def npv_at_rate(rate: float) -> float:
        return sum(cf / (1 + rate) ** period for cf, period in zip(cash_flows, periods))
    
    try:
        irr = fsolve(npv_at_rate, guess)[0]
        # Validate the result
        if abs(npv_at_rate(irr)) > 0.01:  # Within 1 cent
            raise ValueError(f"IRR calculation did not converge properly")
        return float(irr)
    except Exception as e:
        raise ValueError(f"Failed to calculate IRR: {str(e)}")


def calculate_npv(cash_flows: List[float], discount_rate: float, periods: List[int] = None) -> float:
    """
    Calculate Net Present Value (NPV) of a series of cash flows.
    
    Args:
        cash_flows: List of cash flows
        discount_rate: Discount rate as decimal (e.g., 0.1 for 10%)
        periods: Optional list of period numbers (default: 0, 1, 2, ...)
    
    Returns:
        NPV as float
    """
    if periods is None:
        periods = list(range(len(cash_flows)))
    
    if len(cash_flows) != len(periods):
        raise ValueError("cash_flows and periods must have same length")
    
    npv = sum(cf / (1 + discount_rate) ** period for cf, period in zip(cash_flows, periods))
    return float(npv)


def calculate_fcf(
    ebit: float,
    tax_rate: float,
    depreciation: float = 0,
    capex: float = 0,
    change_in_nwc: float = 0
) -> float:
    """
    Calculate Free Cash Flow (FCF).
    
    FCF = EBIT(1 - Tax Rate) + D&A - Capex - Change in NWC
    
    Args:
        ebit: Earnings Before Interest and Taxes
        tax_rate: Tax rate as decimal (e.g., 0.21 for 21%)
        depreciation: Depreciation & Amortization
        capex: Capital Expenditures
        change_in_nwc: Change in Net Working Capital
    
    Returns:
        Free Cash Flow as float
    """
    nopat = ebit * (1 - tax_rate)
    fcf = nopat + depreciation - capex - change_in_nwc
    return float(fcf)


def calculate_terminal_value_perpetuity(
    final_year_fcf: float,
    wacc: float,
    perpetuity_growth: float
) -> float:
    """
    Calculate Terminal Value using perpetuity growth method.
    
    TV = Final Year FCF × (1 + Growth Rate) / (WACC - Growth Rate)
    
    Args:
        final_year_fcf: FCF in final explicit forecast year
        wacc: Weighted Average Cost of Capital as decimal
        perpetuity_growth: Long-term growth rate as decimal
    
    Returns:
        Terminal Value as float
    
    Raises:
        ValueError: If WACC <= growth rate (division by zero/negative)
    """
    if wacc <= perpetuity_growth:
        raise ValueError(f"WACC ({wacc}) must be greater than perpetuity growth ({perpetuity_growth})")
    
    tv = final_year_fcf * (1 + perpetuity_growth) / (wacc - perpetuity_growth)
    return float(tv)


def calculate_terminal_value_multiple(
    final_year_metric: float,
    exit_multiple: float
) -> float:
    """
    Calculate Terminal Value using exit multiple method.
    
    TV = Final Year Metric × Exit Multiple
    
    Args:
        final_year_metric: Final year EBITDA, Revenue, or other metric
        exit_multiple: Exit multiple (e.g., 8.5 for 8.5x EBITDA)
    
    Returns:
        Terminal Value as float
    """
    tv = final_year_metric * exit_multiple
    return float(tv)


def calculate_payback_period(
    initial_investment: float,
    cash_flows: List[float],
    discounted: bool = False,
    discount_rate: float = 0.0
) -> float:
    """
    Calculate Payback Period (simple or discounted).
    
    Args:
        initial_investment: Initial investment (positive value)
        cash_flows: List of annual cash flows
        discounted: If True, calculate discounted payback period
        discount_rate: Discount rate for discounted payback
    
    Returns:
        Payback period in years as float
    
    Raises:
        ValueError: If payback never occurs
    """
    remaining = initial_investment
    
    for year, cf in enumerate(cash_flows, start=1):
        if discounted:
            pv_cf = cf / (1 + discount_rate) ** year
        else:
            pv_cf = cf
        
        remaining -= pv_cf
        
        if remaining <= 0:
            # Interpolate to get precise payback time
            excess = abs(remaining)
            if discounted:
                recovery_cf = cf / (1 + discount_rate) ** year
            else:
                recovery_cf = cf
            
            if recovery_cf == 0:
                return float(year)
            
            fraction = excess / recovery_cf
            return float(year - 1 + (1 - fraction))
    
    raise ValueError("Payback never occurs within given cash flow periods")


def calculate_mirr(
    investment_cash_flows: List[float],
    financing_rate: float,
    reinvestment_rate: float
) -> float:
    """
    Calculate Modified Internal Rate of Return (MIRR).
    
    Args:
        investment_cash_flows: List of cash flows
        financing_rate: Rate for negative cash flows (cost of capital)
        reinvestment_rate: Rate for positive cash flows (reinvestment rate)
    
    Returns:
        MIRR as decimal (e.g., 0.15 for 15%)
    """
    # Separate positive and negative cash flows
    negative_cfs = [cf if cf < 0 else 0 for cf in investment_cash_flows]
    positive_cfs = [cf if cf > 0 else 0 for cf in investment_cash_flows]
    
    # Calculate PV of negative cash flows
    pv_negative = sum(
        negative_cfs[i] / (1 + financing_rate) ** i
        for i in range(len(negative_cfs))
    )
    
    # Calculate FV of positive cash flows
    n = len(investment_cash_flows) - 1
    fv_positive = sum(
        positive_cfs[i] * (1 + reinvestment_rate) ** (n - i)
        for i in range(len(positive_cfs))
    )
    
    # MIRR = (FV / |PV|) ^ (1/n) - 1
    if pv_negative == 0:
        raise ValueError("No negative cash flows for MIRR calculation")
    
    mirr = (fv_positive / abs(pv_negative)) ** (1 / n) - 1
    return float(mirr)


def calculate_unit_economics(
    cac: float,
    arpu: float,
    gross_margin: float,
    customer_lifetime_years: float = 3.0
) -> Dict[str, float]:
    """
    Calculate unit economics metrics.
    
    Args:
        cac: Customer Acquisition Cost
        arpu: Annual Recurring Revenue Per User
        gross_margin: Gross margin as decimal (e.g., 0.80 for 80%)
        customer_lifetime_years: Expected customer lifetime
    
    Returns:
        Dictionary with unit economics metrics
    """
    ltv = arpu * gross_margin * customer_lifetime_years
    ltv_to_cac = ltv / cac if cac > 0 else 0
    cac_payback_months = (cac / (arpu * gross_margin / 12)) if (arpu * gross_margin) > 0 else 0
    
    return {
        "ltv": float(ltv),
        "ltv_to_cac_ratio": float(ltv_to_cac),
        "cac_payback_months": float(cac_payback_months),
        "annual_gross_profit_per_customer": float(arpu * gross_margin)
    }


def calculate_breakeven(
    fixed_costs: float,
    unit_price: float,
    unit_variable_cost: float
) -> Dict[str, float]:
    """
    Calculate breakeven analysis.
    
    Args:
        fixed_costs: Total fixed costs
        unit_price: Price per unit
        unit_variable_cost: Variable cost per unit
    
    Returns:
        Dictionary with breakeven metrics
    """
    if unit_price <= unit_variable_cost:
        raise ValueError("Unit price must be greater than unit variable cost")
    
    contribution_margin = unit_price - unit_variable_cost
    contribution_margin_pct = contribution_margin / unit_price
    
    breakeven_units = fixed_costs / contribution_margin
    breakeven_revenue = breakeven_units * unit_price
    
    return {
        "breakeven_units": float(breakeven_units),
        "breakeven_revenue": float(breakeven_revenue),
        "contribution_margin_per_unit": float(contribution_margin),
        "contribution_margin_percentage": float(contribution_margin_pct)
    }


def calculate_wacc(
    risk_free_rate: float,
    market_risk_premium: float,
    beta: float,
    tax_rate: float,
    debt_weight: float,
    equity_weight: float,
    cost_of_debt: float
) -> float:
    """
    Calculate Weighted Average Cost of Capital (WACC).
    
    WACC = (E/V × Re) + (D/V × Rd × (1 - Tc))
    
    Where:
    - Re = Risk-free rate + Beta × Market risk premium
    - Rd = Cost of debt
    - Tc = Tax rate
    
    Args:
        risk_free_rate: Risk-free rate as decimal
        market_risk_premium: Market risk premium as decimal
        beta: Beta coefficient
        tax_rate: Tax rate as decimal
        debt_weight: Weight of debt (D/V)
        equity_weight: Weight of equity (E/V)
        cost_of_debt: Cost of debt as decimal
    
    Returns:
        WACC as decimal
    """
    if abs((debt_weight + equity_weight) - 1.0) > 0.001:
        raise ValueError("Debt weight + Equity weight must equal 1.0")
    
    # Cost of equity using CAPM
    cost_of_equity = risk_free_rate + (beta * market_risk_premium)
    
    # WACC
    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
    return float(wacc)


if __name__ == "__main__":
    # Example usage
    print("[INFO] Financial Calculator Module")
    print("[INFO] Use by importing functions into your models")
