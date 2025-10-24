# DCF Valuation Methodology

## Overview

A Discounted Cash Flow (DCF) valuation estimates a company's intrinsic value based on the present value of its future cash flows. The fundamental principle: a business is worth the sum of all cash it will generate, discounted to today's dollars.

## DCF Framework

### Step 1: Forecast Free Cash Flows (Explicit Period)

**Typical period**: 5-10 years (most common: 5 years)

#### Starting Point: Revenue Forecast
- Project revenue growth based on:
  - Historical growth rates
  - Market expansion
  - Competitive positioning
  - Economic outlook

#### Calculate Operating Cash Flow
1. **EBIT** (Earnings Before Interest & Taxes)
   - Start with revenue
   - Subtract operating expenses
   - Result: EBIT

2. **NOPAT** (Net Operating Profit After Tax)
   - Formula: EBIT × (1 - Tax Rate)
   - Shows cash available before capital decisions

3. **Adjust for Non-Cash Items**
   - Add back: Depreciation & Amortization
   - These reduce taxable income but aren't cash

4. **Adjust for Capital Needs**
   - Subtract: Capital Expenditures (CapEx)
   - Needed to maintain/grow business

5. **Adjust for Working Capital**
   - Subtract: Increase in Net Working Capital
   - Money tied up in receivables, inventory, payables

**Result**: Free Cash Flow (FCF) = NOPAT + D&A - CapEx - Δ NWC

#### FCF Projection Example (5-year)

| Year | 1 | 2 | 3 | 4 | 5 |
|------|---|---|---|---|---|
| Revenue | $100M | $115M | $132M | $152M | $175M |
| EBIT Margin | 20% | 21% | 22% | 23% | 24% |
| EBIT | $20M | $24M | $29M | $35M | $42M |
| Tax Rate | 21% | 21% | 21% | 21% | 21% |
| NOPAT | $15.8M | $19.0M | $23.0M | $27.7M | $33.2M |
| + D&A | $5M | $5.5M | $6M | $7M | $8M |
| - CapEx | $3M | $3.5M | $4M | $5M | $6M |
| - Δ NWC | $1M | $1.5M | $2M | $2.5M | $3M |
| **FCF** | **$16.8M** | **$19.5M** | **$23.0M** | **$27.2M** | **$32.2M** |

### Step 2: Calculate Terminal Value

**Definition**: Value of all cash flows beyond the explicit forecast period.

**Two Methods**:

#### Method 1: Perpetuity Growth Method (Most Common)
**Formula**: TV = FCF_Year5 × (1 + g) / (WACC - g)

**Where**:
- FCF_Year5: Final year explicit forecast FCF
- g: Long-term growth rate (typically 2-3%)
- WACC: Discount rate

**Example**:
- FCF Year 5: $32.2M
- Growth Rate: 2.5%
- WACC: 9%
- TV = $32.2M × 1.025 / (0.09 - 0.025) = $599M

**Sanity Checks**:
- Terminal year FCF growth shouldn't exceed GDP growth
- Typical perpetuity growth: 2-3%
- Higher growth requires strong justification

#### Method 2: Exit Multiple Method
**Formula**: TV = FCF_Year5 × Exit Multiple

**Common Multiples**:
- EV/EBITDA: 8-15x depending on industry
- EV/Revenue: 2-5x depending on industry

**Example**:
- EBITDA Year 5: $50M
- Exit Multiple: 10x EBITDA
- TV = $50M × 10 = $500M

**When to Use**:
- Transaction comparable data available
- Industry trading multiples well-established
- More conservative than perpetuity method

### Step 3: Calculate Present Value of Cash Flows

**Discount explicit period FCF**:
```
Year 1 FCF: $16.8M / (1.09)^1 = $15.4M
Year 2 FCF: $19.5M / (1.09)^2 = $16.4M
Year 3 FCF: $23.0M / (1.09)^3 = $17.8M
Year 4 FCF: $27.2M / (1.09)^4 = $19.2M
Year 5 FCF: $32.2M / (1.09)^5 = $20.9M
PV of Explicit FCF = $89.7M
```

**Discount Terminal Value**:
```
TV: $599M / (1.09)^5 = $389M
```

### Step 4: Calculate Enterprise Value

**Formula**: EV = PV of Explicit FCF + PV of Terminal Value

**Example**:
- EV = $89.7M + $389M = $478.7M

### Step 5: Calculate Equity Value

**Formula**: Equity Value = Enterprise Value - Net Debt

**Where**: Net Debt = Total Debt - Cash & Equivalents

**Example**:
- EV: $478.7M
- Total Debt: $150M
- Cash: $50M
- Net Debt: $100M
- Equity Value = $478.7M - $100M = $378.7M

### Step 6: Calculate Value Per Share

**Formula**: Value Per Share = Equity Value / Shares Outstanding

**Example**:
- Equity Value: $378.7M
- Shares Outstanding: 50M
- Value Per Share = $378.7M / 50M = $7.57

## Key Inputs & Assumptions

### Discount Rate (WACC)

**Components**:
1. **Risk-Free Rate** (Rf)
   - US 10-year Treasury: typically 3-5%
   - Use current rates at valuation date

2. **Beta** (β)
   - Measure of company volatility vs market
   - Tech: 1.2-1.5
   - Utilities: 0.7-0.9
   - Consumer: 0.8-1.0

3. **Market Risk Premium** (Rm - Rf)
   - Expected return above risk-free rate
   - Long-term historical: 5-7%
   - Conservative: use 6%

4. **Cost of Equity** (using CAPM)
   - Formula: Re = Rf + β(Rm - Rf)
   - Example: 4% + 1.0 × 6% = 10%

5. **Cost of Debt** (Rd)
   - Interest rate on debt
   - Check company's actual rates
   - Adjust for credit rating

6. **WACC Calculation**
   - Formula: WACC = (E/V × Re) + (D/V × Rd × (1-Tc))
   - Example:
     - E/V = 70%, Re = 10%
     - D/V = 30%, Rd = 5%, Tax = 21%
     - WACC = (0.70 × 0.10) + (0.30 × 0.05 × 0.79) = 7.7% + 1.2% = 8.9%

### Growth Rates

**Revenue Growth**:
- Early years: Based on market opportunity, execution
- Mid years: Moderating toward industry/GDP growth
- Terminal: 2-3% (rarely above GDP growth)

**Margin Expansion**:
- Reflect operating leverage
- Consider competitive dynamics
- Build in learning curve if new market

**CapEx & Working Capital**:
- Maintenance CapEx: ~% of revenue
- Growth CapEx: Declines as company matures
- NWC: Typically 5-15% of revenue

## Sensitivity Analysis

### One-Way Sensitivity

Test valuation sensitivity to individual inputs:

| WACC | 7% | 8% | 9% | 10% | 11% |
|------|----|----|-----|------|------|
| Value/Share | $9.20 | $8.15 | $7.57 | $7.10 | $6.72 |

### Two-Way Sensitivity

Test valuation to two key drivers:

```
Terminal Growth vs WACC
              7.0%   7.5%   8.0%   8.5%   9.0%
2.0%  $9.42  $9.95  $10.58 $11.35 $12.31
2.5%  $9.73  $10.40 $11.25 $12.33 $13.70
3.0%  $10.09 $10.92 $12.10 $13.63 $15.76
3.5%  $10.51 $11.54 $13.19 $15.47 $19.10
```

### Tornado Chart

Rank inputs by impact on valuation:
- WACC: ±1% → $2.50 impact
- Terminal Growth: ±0.5% → $1.80 impact
- Revenue Growth: ±5% → $1.20 impact
- Tax Rate: ±2% → $0.80 impact

## Common Mistakes to Avoid

### 1. Inconsistent Growth Assumptions
**Mistake**: Forecasting 50% revenue growth but only 5% margin improvement
**Fix**: Model implies competitive responses; ensure consistency

### 2. Excessive Terminal Growth
**Mistake**: Terminal growth rate > GDP growth
**Fix**: Keep terminal growth 2-3% maximum

### 3. Wrong WACC
**Mistake**: Using cost of equity instead of WACC (or vice versa)
**Fix**: Always use WACC for enterprise value calculations

### 4. Ignoring Debt Adjustments
**Mistake**: Forgetting to subtract net debt
**Fix**: Equity Value = EV - Net Debt (always)

### 5. Terminal Value Dominance
**Mistake**: Terminal value > 80% of enterprise value
**Fix**: Indicates over-reliance on terminal assumption; validate

### 6. Not Testing Sensitivity
**Mistake**: Relying on single point estimate
**Fix**: Always provide valuation range with key sensitivities

## DCF Strengths & Limitations

### Strengths
- Based on fundamental economics (cash flows)
- Captures company-specific characteristics
- Provides range of values through sensitivity
- Transparent and auditable

### Limitations
- Highly dependent on forecast accuracy
- Small changes in WACC cause large valuation swings
- Requires detailed financial forecasts
- Terminal value often dominates (long-term uncertainty)
- Less effective for:
  - Pre-revenue companies
  - Highly cyclical businesses
  - Turnaround situations

## Validation: Sanity Checks

1. **Compare to Comps**
   - Is DCF valuation reasonable vs trading multiples?
   - If vastly different, understand why

2. **Check Implied Multiples**
   - Implied EV/EBITDA from DCF
   - Compare to peer multiples

3. **Reverse DCF**
   - What WACC/growth implied by current price?
   - Is it reasonable?

4. **Historical Context**
   - How has valuation moved?
   - What's driving the change?

5. **Scenario Analysis**
   - Bear/base/bull cases
   - What's required for upside case?
