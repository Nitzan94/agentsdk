#!/usr/bin/env python3
"""
ABOUTME: DCF and valuation analysis tools
ABOUTME: Performs DCF analysis, comparable company valuations, and precedent transactions

Comprehensive valuation analysis including DCF, comparable company multiples,
and precedent transaction analysis.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import statistics


@dataclass
class ValuationResult:
    """Results from a valuation analysis."""
    enterprise_value: float
    equity_value: float
    value_per_share: float
    implied_multiples: Dict[str, float]
    sensitivity_range: Tuple[float, float]


class DCFValuation:
    """Performs DCF valuation analysis."""
    
    def __init__(self, discount_rate: float, terminal_growth: float):
        """
        Initialize DCF valuation.
        
        Args:
            discount_rate: WACC or required return as decimal (e.g., 0.10)
            terminal_growth: Long-term growth rate as decimal
        """
        self.discount_rate = discount_rate
        self.terminal_growth = terminal_growth
    
    def calculate_dcf(
        self,
        explicit_fcf: List[float],
        terminal_fcf: float,
        net_debt: float = 0,
        shares_outstanding: float = 1,
        terminal_value_method: str = "perpetuity"
    ) -> ValuationResult:
        """
        Calculate DCF valuation.
        
        Args:
            explicit_fcf: List of free cash flows for explicit forecast period
            terminal_fcf: FCF in final explicit year
            net_debt: Net debt (debt - cash)
            shares_outstanding: Number of shares outstanding
            terminal_value_method: "perpetuity" or "multiple"
        
        Returns:
            ValuationResult with valuation metrics
        """
        # Calculate PV of explicit period FCF
        pv_explicit = sum(
            fcf / (1 + self.discount_rate) ** (year + 1)
            for year, fcf in enumerate(explicit_fcf)
        )
        
        # Calculate terminal value
        if terminal_value_method == "perpetuity":
            terminal_value = (
                terminal_fcf * (1 + self.terminal_growth) / 
                (self.discount_rate - self.terminal_growth)
            )
        else:
            raise ValueError(f"Unknown terminal value method: {terminal_value_method}")
        
        # Discount terminal value
        years_in_explicit = len(explicit_fcf)
        pv_terminal = terminal_value / (1 + self.discount_rate) ** years_in_explicit
        
        # Enterprise Value
        enterprise_value = pv_explicit + pv_terminal
        
        # Equity Value
        equity_value = enterprise_value - net_debt
        
        # Value per share
        value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        # Implied multiples
        implied_multiples = {
            "ev_to_terminal_fcf": enterprise_value / terminal_fcf if terminal_fcf > 0 else 0,
            "pv_terminal_to_ev": pv_terminal / enterprise_value if enterprise_value > 0 else 0,
            "pv_explicit_to_ev": pv_explicit / enterprise_value if enterprise_value > 0 else 0
        }
        
        # Sensitivity range (simplified: ±1% discount rate change)
        low_case = self._calculate_dcf_at_wacc(explicit_fcf, terminal_fcf, self.discount_rate + 0.01)
        high_case = self._calculate_dcf_at_wacc(explicit_fcf, terminal_fcf, self.discount_rate - 0.01)
        
        return ValuationResult(
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            value_per_share=value_per_share,
            implied_multiples=implied_multiples,
            sensitivity_range=(low_case, high_case)
        )
    
    def _calculate_dcf_at_wacc(
        self,
        explicit_fcf: List[float],
        terminal_fcf: float,
        discount_rate: float
    ) -> float:
        """Helper to calculate DCF at specific WACC."""
        pv_explicit = sum(
            fcf / (1 + discount_rate) ** (year + 1)
            for year, fcf in enumerate(explicit_fcf)
        )
        
        terminal_value = (
            terminal_fcf * (1 + self.terminal_growth) / 
            (discount_rate - self.terminal_growth)
        )
        
        years = len(explicit_fcf)
        pv_terminal = terminal_value / (1 + discount_rate) ** years
        
        return pv_explicit + pv_terminal


class ComparableCompanyValuation:
    """Performs comparable company valuation analysis."""
    
    def __init__(self, comparable_metrics: Dict[str, Dict[str, float]]):
        """
        Initialize comparable company analysis.
        
        Args:
            comparable_metrics: Dict mapping company names to metric dicts
                Example: {
                    "Company A": {"revenue": 100, "ebitda": 25, "net_income": 15},
                    "Company B": {"revenue": 150, "ebitda": 35, "net_income": 20}
                }
        """
        self.comparable_metrics = comparable_metrics
    
    def calculate_multiples(self) -> Dict[str, Dict[str, float]]:
        """Calculate valuation multiples for each comparable."""
        multiples = {}
        
        for company_name, metrics in self.comparable_metrics.items():
            company_multiples = {}
            
            # Calculate multiples if data exists
            if "enterprise_value" in metrics and "revenue" in metrics and metrics["revenue"] > 0:
                company_multiples["ev_revenue"] = metrics["enterprise_value"] / metrics["revenue"]
            
            if "enterprise_value" in metrics and "ebitda" in metrics and metrics["ebitda"] > 0:
                company_multiples["ev_ebitda"] = metrics["enterprise_value"] / metrics["ebitda"]
            
            if "market_cap" in metrics and "net_income" in metrics and metrics["net_income"] > 0:
                company_multiples["pe_ratio"] = metrics["market_cap"] / metrics["net_income"]
            
            multiples[company_name] = company_multiples
        
        return multiples
    
    def calculate_median_multiples(self) -> Dict[str, float]:
        """Calculate median multiples across comparables."""
        multiples = self.calculate_multiples()
        
        # Collect all multiples by type
        multiple_sets = {}
        for company_multiples in multiples.values():
            for multiple_name, value in company_multiples.items():
                if multiple_name not in multiple_sets:
                    multiple_sets[multiple_name] = []
                multiple_sets[multiple_name].append(value)
        
        # Calculate medians
        median_multiples = {}
        for multiple_name, values in multiple_sets.items():
            if values:
                median_multiples[multiple_name] = statistics.median(values)
        
        return median_multiples
    
    def calculate_target_valuation(
        self,
        target_metric: float,
        metric_name: str = "ebitda"
    ) -> Dict[str, float]:
        """
        Calculate target company valuation using comparable multiples.
        
        Args:
            target_metric: Target company metric value (e.g., EBITDA)
            metric_name: Name of metric ("revenue", "ebitda", "net_income")
        
        Returns:
            Dictionary with valuation using different multiple approaches
        """
        multiples = self.calculate_multiples()
        median_multiples = self.calculate_median_multiples()
        
        valuations = {}
        
        if metric_name == "ebitda":
            if "ev_ebitda" in median_multiples:
                valuations["ev_ebitda_median"] = target_metric * median_multiples["ev_ebitda"]
            
            # Also calculate using individual comparables
            individual_valuations = []
            for company_name, company_multiples in multiples.items():
                if "ev_ebitda" in company_multiples:
                    individual_valuations.append(target_metric * company_multiples["ev_ebitda"])
            
            if individual_valuations:
                valuations["ev_ebitda_low"] = min(individual_valuations)
                valuations["ev_ebitda_high"] = max(individual_valuations)
                valuations["ev_ebitda_mean"] = sum(individual_valuations) / len(individual_valuations)
        
        elif metric_name == "revenue":
            if "ev_revenue" in median_multiples:
                valuations["ev_revenue_median"] = target_metric * median_multiples["ev_revenue"]
        
        elif metric_name == "net_income":
            if "pe_ratio" in median_multiples:
                valuations["pe_median"] = target_metric * median_multiples["pe_ratio"]
        
        return valuations


class PrecedentTransactionAnalysis:
    """Performs precedent transaction valuation analysis."""
    
    def __init__(self, transaction_data: List[Dict[str, float]]):
        """
        Initialize precedent transaction analysis.
        
        Args:
            transaction_data: List of transaction dicts with deal metrics
                Example: [
                    {"target_ebitda": 50, "deal_value": 450},
                    {"target_ebitda": 75, "deal_value": 615}
                ]
        """
        self.transaction_data = transaction_data
    
    def calculate_deal_multiples(self) -> List[float]:
        """Calculate multiples from precedent transactions."""
        multiples = []
        
        for transaction in self.transaction_data:
            if "target_ebitda" in transaction and "deal_value" in transaction:
                if transaction["target_ebitda"] > 0:
                    multiple = transaction["deal_value"] / transaction["target_ebitda"]
                    multiples.append(multiple)
        
        return multiples
    
    def calculate_median_multiple(self) -> float:
        """Calculate median multiple from precedent transactions."""
        multiples = self.calculate_deal_multiples()
        if multiples:
            return statistics.median(multiples)
        return 0
    
    def calculate_range(self) -> Tuple[float, float, float]:
        """Calculate multiple range (low, median, high)."""
        multiples = self.calculate_deal_multiples()
        if not multiples:
            return 0, 0, 0
        
        return min(multiples), statistics.median(multiples), max(multiples)
    
    def calculate_valuation(self, target_metric: float) -> Dict[str, float]:
        """
        Calculate target valuation using precedent multiples.
        
        Args:
            target_metric: Target company metric (e.g., EBITDA)
        
        Returns:
            Dictionary with valuations at different multiples
        """
        multiples = self.calculate_deal_multiples()
        if not multiples:
            return {}
        
        low, median, high = self.calculate_range()
        
        return {
            "valuation_low": target_metric * low,
            "valuation_median": target_metric * median,
            "valuation_high": target_metric * high,
            "implied_multiple_low": low,
            "implied_multiple_median": median,
            "implied_multiple_high": high
        }


class ValuationSummary:
    """Combines multiple valuation approaches."""
    
    def __init__(self):
        self.valuations = {}
    
    def add_dcf(self, name: str, result: ValuationResult) -> None:
        """Add DCF valuation result."""
        self.valuations[f"DCF - {name}"] = result.enterprise_value
    
    def add_comps(self, name: str, valuation: float) -> None:
        """Add comparable company valuation."""
        self.valuations[f"Comps - {name}"] = valuation
    
    def add_precedent(self, name: str, valuation: float) -> None:
        """Add precedent transaction valuation."""
        self.valuations[f"Precedent - {name}"] = valuation
    
    def get_summary(self) -> Dict[str, float]:
        """Get valuation summary with statistics."""
        if not self.valuations:
            return {}
        
        values = list(self.valuations.values())
        
        return {
            "low": min(values),
            "mean": sum(values) / len(values),
            "median": statistics.median(values),
            "high": max(values),
            "range": max(values) - min(values),
            "individual_valuations": self.valuations
        }


if __name__ == "__main__":
    print("[INFO] Valuation Analyzer Module")
    print("[INFO] Use for DCF, comparable company, and precedent transaction analysis")
