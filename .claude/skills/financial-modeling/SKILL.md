---
name: financial-modeling
description: financial modeling including DCF valuation, financial statement forecasting, scenario analysis, and ad hoc financial calculations. Use this skill when building new financial models from scratch, enhancing existing financial models, performing valuation analysis, creating sensitivity analyses, or performing specialized financial calculations like IRR, NPV, breakeven analysis, and unit economics modeling.
---

# Financial Modeling

## Overview

This skill provides comprehensive financial modeling capabilities for building, analyzing, and enhancing financial models. It supports creating DCF valuations, multi-period financial statements (P&L, balance sheet, cash flow), scenario and sensitivity analysis, and specialized financial calculations. The skill works with both new models created from scratch and existing financial models you provide.

## Core Capabilities

### 1. DCF & Valuation Models
Build and enhance Discounted Cash Flow models from scratch or using existing financial data:
- **DCF Model Creation**: Generate multi-period DCF models with explicit forecast periods and terminal value calculations
- **Comparable Company Analysis**: Create valuation analysis based on comparable company multiples
- **Precedent Transaction Analysis**: Build valuation frameworks based on historical transaction data
- **Terminal Value Calculation**: Support perpetuity growth and exit multiple methods

### 2. Financial Statements
Create comprehensive multi-period financial projections:
- **Income Statement (P&L)**: Revenue forecasts, operating expenses, taxes, net income
- **Balance Sheet**: Assets, liabilities, equity projections with balance validation
- **Cash Flow Statement**: Operating, investing, and financing activities with reconciliation to net income
- **Integrated Statements**: Automatic linking between statements with formula validation

### 3. Scenario & Sensitivity Analysis
Analyze financial model behavior under different assumptions:
- **Scenario Modeling**: Best case, base case, and worst case scenarios with driver assumption variations
- **Sensitivity Tables**: 1-way and 2-way sensitivity tables for valuation outputs (IRR, NPV, valuation multiples)
- **Tornado Diagrams**: Identify which drivers have the most impact on valuation
- **Monte Carlo Simulation**: Multi-variable scenario analysis with assumption ranges

### 4. Ad Hoc Financial Calculations
Perform specialized financial analyses:
- **IRR/MIRR**: Internal rate of return and modified IRR calculations
- **NPV**: Net present value calculations with custom discount rates
- **Payback Period**: Simple and discounted payback analysis
- **Unit Economics**: CAC (Customer Acquisition Cost), LTV (Lifetime Value), CAC payback period
- **Breakeven Analysis**: Fixed/variable cost breakeven with sensitivity
- **Financial Ratios**: Profitability, leverage, liquidity, and efficiency ratios

## Workflow: Creating and Working with Models

### Starting a New Model
When asked to build a new financial model:
1. Gather key assumptions (revenue growth, margins, capex, working capital, tax rate, discount rate)
2. Structure the model with separate assumption and calculation sections
3. Build integrated statements (P&L → Balance Sheet → Cash Flow)
4. Apply valuation methodology (DCF, multiples, or transaction-based)
5. Output as XLSX with formulas preserved and CSV for data sharing

### Enhancing Existing Models
When provided an existing financial model:
1. Analyze the current model structure and formulas
2. Identify what's already modeled and what's missing
3. Add requested enhancements (new calculations, scenarios, statements)
4. Validate formula integrity and cross-statement linkages
5. Output updated model as XLSX with all formulas intact

### Building Valuations from Models
When creating DCF or valuation analysis:
1. Use financial statement projections as the basis for cash flow calculations
2. Calculate Free Cash Flow (EBIT(1-Tax) + D&A - Capex - Change in NWC)
3. Project to explicit period then apply terminal value methodology
4. Discount cash flows to present value using WACC or required return
5. Output valuation summary with sensitivity tables

## Best Practices

### Model Structure
- Separate assumptions from calculations for easy scenario changes
- Use consistent naming conventions (e.g., all percentages as decimals or %)
- Include data validation and error checking (balance sheet must balance, etc.)
- Document all key formulas and assumptions
- Use absolute references ($) for inputs, relative for calculations

### Formula Quality
- Never hard-code values; use cell references to assumptions
- Use named ranges for key inputs (e.g., "discount_rate", "tax_rate")
- Include input validation with data type and range restrictions
- Build models to automatically adjust for different time periods
- Use Excel functions: IF for conditionals, SUMPRODUCT for arrays, INDIRECT for flexibility

### Output Format
- XLSX: Primary format with formulas preserved for model interactivity
- CSV: Secondary format for data import/analysis in other tools
- Include metadata sheets with assumptions, sources, and model documentation
- Color-code sheets by function: Blue for inputs, White for calculations, Green for outputs

## Key Formulas & Calculations

### Free Cash Flow
FCF = EBIT × (1 - Tax Rate) + Depreciation & Amortization - Capex - Change in Net Working Capital

### Terminal Value (Perpetuity Growth)
TV = Final Year FCF × (1 + Growth Rate) / (Discount Rate - Growth Rate)

### Terminal Value (Exit Multiple)
TV = Final Year EBITDA × Exit Multiple

### NPV Calculation
NPV = SUM(Discounted Cash Flows) + Terminal Value (Discounted)

### IRR
Solve for rate where: 0 = SUM(Cash Flows / (1 + IRR)^Period)

### Unit Economics
- CAC Payback = CAC / (ARPU × Gross Margin)
- LTV/CAC Ratio = LTV / CAC (target: >3:1)
- Magic Number = (Current Quarter Revenue - Prior Quarter Revenue) × 4 / Prior Quarter Sales & marketing spend

## Resources

### scripts/
Executable Python scripts for financial calculations and model generation:
- `financial_calculator.py`: Core financial functions (IRR, NPV, FCF calculations)
- `model_builder.py`: Automated model generation from assumptions
- `sensitivity_analysis.py`: Generate sensitivity tables and scenarios
- `valuation_analyzer.py`: DCF and comparable company analysis

### references/
Detailed documentation and reference material:
- `financial_definitions.md`: Complete financial terminology and formula reference
- `dcf_methodology.md`: Comprehensive guide to DCF model construction
- `best_practices.md`: Financial modeling standards and conventions
- `excel_formulas.md`: Advanced Excel formula patterns for financial models

### assets/
Template Excel files and boilerplate models:
- `dcf_template.xlsx`: Ready-to-customize DCF model template
- `financial_statements_template.xlsx`: P&L, Balance Sheet, Cash Flow template
- `scenario_analysis_template.xlsx`: Sensitivity and scenario analysis template
- `valuation_summary_template.xlsx`: Valuation output and summary template

## Output Formats

All models are delivered in two formats:

**XLSX (Excel)**: 
- Primary format with all formulas and formatting preserved
- Interactive - allows changing assumptions and seeing results update
- Multiple sheets organized by function (Assumptions, Calculations, Output, Scenarios)
- Professional formatting with conditional formatting and data validation

**CSV (Comma-Separated Values)**:
- Data export for analysis in Python, R, or other tools
- One CSV per sheet for multi-sheet models
- Clean data format without formulas for import/integration
