# Financial Modeling Best Practices

## Model Architecture

### Separation of Concerns

**Golden Rule**: Separate inputs from calculations from outputs

#### Input Sheets
- Single source of truth for all assumptions
- Clearly labeled and organized
- Color-coded (light blue background)
- Include units, descriptions, and acceptable ranges
- Version control: date last updated, by whom

**Example Structure**:
```
ASSUMPTIONS Sheet
├── Company Information
├── Revenue Assumptions
├── Operating Assumptions
├── Capital & Working Capital
├── Financing Assumptions
└── Valuation Assumptions
```

#### Calculation Sheets
- Link all to assumptions (use cell references, never hardcode)
- Build formulas from simple to complex
- Use named ranges for key inputs
- Include logic to handle edge cases (negative values, zero denominators)
- White background for working calculations

#### Output Sheets
- Summary metrics and results
- Charts and dashboards
- Light green background
- Should update automatically when assumptions change

### Model Structure Example

```
Workbook Structure:
├── Cover (Overview & contact info)
├── Instructions (How to use model)
├── Assumptions (Input sheet)
├── Income Statement (Calculation)
├── Balance Sheet (Calculation)
├── Cash Flow (Calculation)
├── FCF Calculation (Intermediate calc)
├── DCF Valuation (Intermediate calc)
├── Valuation Summary (Output)
├── Sensitivity (Output)
├── Charts (Output)
└── Support (Helper calculations)
```

## Naming Conventions

### Worksheet Names
- Clear, descriptive: "Income Statement" not "IS" or "P&L"
- Consistent tense: use singular ("Assumption" not "Assumptions")
- Logical order reflects analysis flow

### Cell References & Named Ranges
**Use named ranges for**:
- Key inputs: `discount_rate`, `tax_rate`, `revenue_cagr`
- Key outputs: `enterprise_value`, `equity_value`, `value_per_share`

**Avoid**:
- Generic names: B5, Revenue2024
- Ambiguous abbreviations
- Spaces in names (use underscores)

**Example**:
```
discount_rate = Assumptions!B8
revenue_growth_yr1 = Assumptions!B12
terminal_growth = Assumptions!B15
```

### Variable Naming
- Descriptive but concise
- Use consistent patterns:
  - Rates as decimals: `growth_rate` (not `growth_pct`)
  - Values in thousands: `revenue_m` (M = millions)
  - Year-based: `revenue_2024`, `revenue_2025`

## Formula Construction

### Formula Design Principles

#### 1. Use Cell References, Not Hardcodes
**Bad**:
```
=A1 * 1.15
```

**Good**:
```
=A1 * (1 + revenue_growth_rate)
```

#### 2. Build Formulas Hierarchically
**Bad**: Single complex formula
```
=SUM(B2:B6) / (SUM(B2:B6) + SUM(C2:C6))
```

**Good**: Helper rows then reference
```
Row: Total Revenue = SUM(B2:B6)
Row: Total Costs = SUM(C2:C6)
Row: Revenue % = Total Revenue / (Total Revenue + Total Costs)
```

#### 3. Handle Edge Cases
**Bad**:
```
=A1 / B1
```

**Good**:
```
=IF(B1 = 0, 0, A1 / B1)
```

#### 4. Use Absolute References for Inputs
**Bad**:
```
Year 1: =assumptions!B5 * C5
Year 2: =assumptions!B5 * C6
```
(Gets lost if rows added)

**Good**:
```
Year 1: =assumptions!$B$5 * C5
Year 2: =assumptions!$B$5 * C6
```
(Always references assumptions!B5)

#### 5. Use Relative References for Copies
**Bad**:
```
=assumptions!$B$5 * C$5 (prevents proper copying)
```

**Good**:
```
=INDIRECT("assumptions!B"&COLUMN()) * C5
or use helper formula that adapts
```

### Common Financial Formula Patterns

#### CAGR Calculation
```
=POWER(Ending Value / Beginning Value, 1 / Number of Years) - 1
```

#### Present Value of Series
```
=SUMPRODUCT(Cash Flows / (1 + Discount Rate) ^ ROW(Cash Flows))
```

#### Interpolation (find value between known points)
```
=Low_Value + (High_Value - Low_Value) * (Target - Low_Point) / (High_Point - Low_Point)
```

#### Conditional Calculation (e.g., first year different)
```
=IF(Year = 1, Starting Value, Previous Year Value * (1 + Growth Rate))
```

#### Multi-Level IF (avoid nesting >3 levels)
```
=IF(Scenario = "Bull", Bull_Value, IF(Scenario = "Base", Base_Value, Bear_Value))
or use CHOOSE() or INDEX/MATCH
```

## Data Validation

### Input Validation

Set up data validation on all assumption inputs:

**Example for Revenue Growth Rate**:
- Type: Decimal
- Data: between
- Minimum: 0% (can't be negative unless specific case)
- Maximum: 50% (reasonable upper bound)
- Error Message: "Revenue growth should be between 0% and 50%"

**Benefits**:
- Prevents user error
- Self-documenting (shows acceptable ranges)
- Helps catch unrealistic scenarios

### Calculation Validation

#### Balance Sheet Must Balance
Add validation check:
```
Total Assets = Total Liabilities + Total Equity

If not equal:
=IF(Total Assets <> Total Liabilities + Total Equity, "ERROR", "OK")
```

#### FCF Reasonableness Checks
```
=IF(FCF < 0, "WARNING: Negative FCF in Year " & Year, "OK")
=IF(FCF > Revenue, "WARNING: FCF > Revenue (unusual)", "OK")
```

## Formatting & Presentation

### Color Scheme
- **Light Blue** (RGB 217, 225, 242): Input cells
- **White**: Calculated values
- **Light Green** (RGB 226, 239, 218): Output/summary
- **Light Gray** (RGB 231, 230, 230): Section headers
- **Dark Blue** (RGB 68, 114, 196): Header rows (with white text)
- **Yellow**: Highlights (base case in sensitivity, anomalies)
- **Red**: Errors or warnings

### Number Formatting

**Whole Numbers**: No decimals (for counts, most values)
- Format: `#,##0`

**Percentages**: 2 decimal places
- Format: `0.00%`

**Currency**: In thousands if modeling in thousands
- Format: `#,##0, " M"` (if in millions)
- Or: `"$" #,##0` (if in actual dollars)

**Cells Should Show**:
- Values in thousands: "$1,234" = $1,234,000
- Include unit label to prevent confusion

### Row/Column Organization

**Annual Models**:
```
         Col A          Col B    Col C    Col D    Col E
Row 1    [Title]        [blank]  2024     2025     2026
Row 2    [blank]        [blank]
Row 3    [blank]        [blank]
Row 4    Revenue        [calc]   [calc]   [calc]
Row 5    Growth %       [input]  [calc]   [calc]
```

**Key Rules**:
- Headers in row 1-3 area
- Data starts row 4+
- Consistent alignment (metrics in column A, years across columns)
- Use merged cells sparingly (hard to edit later)

### Charts & Dashboards

**Effective Charts**:
- Revenue & FCF Growth Trend (line chart)
- EBITDA Margin Evolution (line chart)
- Leverage Ratio Progression (line chart)
- Valuation Waterfall (waterfall chart)
- Sensitivity Analysis (data table or heatmap)

**Dashboard Best Practices**:
- Single page view when possible
- Key metrics prominently displayed
- Charts linked to calculations (not static)
- Update automatically with assumption changes

## Documentation

### Cover Sheet
Include:
- Company name and valuation date
- Key assumptions summary
- Analyst name and contact
- Confidence level / update frequency
- Key disclaimers

### Instructions Sheet
Explain:
- How to use the model
- Which cells are inputs (assumptions)
- Output sheets and their meanings
- Key sensitivities
- Common mistakes to avoid

### Assumptions Sheet Notes
For each assumption:
- What it represents
- Source (if external)
- How it was derived
- Confidence level
- Historical ranges

**Example**:
```
Discount Rate (WACC): 8.5%
Source: DCF Calculation
Derived from: RF 4.0% + Beta 1.1 × MRP 6% - CoD adjustment
Confidence: High (based on current market rates)
Historical Range: 7.5% - 9.5% (last 5 years)
```

## Version Control & Change Management

### File Naming
```
[Company]_Model_[Version]_[Date]_[Analyst].xlsx
Example: Apple_DCF_v2.1_2024-10-15_JSmith.xlsx
```

### Version Log (on Cover Sheet)
| Version | Date | Analyst | Changes |
|---------|------|---------|---------|
| 2.1 | 2024-10-15 | J.Smith | Updated WACC to 8.5%; adjusted terminal growth to 2.5% |
| 2.0 | 2024-09-20 | K.Jones | Added sensitivity analysis; fixed balance sheet link |
| 1.0 | 2024-08-01 | J.Smith | Initial model |

### Audit Trail
Include:
- Who created/modified
- When changes were made
- What changed (formulas, assumptions, structure)
- Why (reason for change)

## Performance & Maintenance

### File Size
- Keep under 5MB for responsive modeling
- If larger: split into multiple files linked by formulas
- Archive old versions regularly

### Calculation Speed
- Minimize volatile functions (NOW(), RAND())
- Use calculation mode "Manual" during heavy edits
- Use helper sheets to reduce complex array formulas

### Sharing & Collaboration

**Read-Only for Stakeholders**:
- Protect sheets (Format → Cells → Protection)
- Protect workbook structure
- Provide one output sheet for distribution

**Working Version**:
- Unprotected for analysis team
- Shared on central drive or cloud
- Regular backups

## Common Errors & How to Avoid

| Error | Cause | Prevention |
|-------|-------|-----------|
| Circular references | Formula references itself indirectly | Use 1-2 formula levels only |
| Hardcoded values | Manually entering numbers | Always use cell references |
| Wrong formula in copy | Formula doesn't adapt when copied | Test copy behavior first |
| #DIV/0! errors | Dividing by zero | Use IF to check denominator |
| Broken links | Source file moved/deleted | Use internal references when possible |
| Incorrect balance sheet | Failed to link sub-items properly | Validate balance sheet formula |
| Terminal value dominance | Terminal value too large | Check perpetuity growth reasonableness |
| Outdated inputs | Forgot to update assumptions | Set reminder to review quarterly |

## Review Checklist

Before finalizing model:

- [ ] All assumptions in input sheet with no hardcodes elsewhere
- [ ] All calculations link to assumptions (not other calculations)
- [ ] Named ranges created for key inputs/outputs
- [ ] Balance sheet balances
- [ ] Cash flow reconciles to net income
- [ ] Valuation waterfall complete and documented
- [ ] Sensitivity analysis performed (at least one-way)
- [ ] Sanity checks passed (vs. comps, historical, logic)
- [ ] No circular references or errors (Ctrl+`)
- [ ] Formatting consistent (colors, number formats)
- [ ] Documentation complete (cover sheet, instructions)
- [ ] File named properly and version tracked
- [ ] Model tested with different input scenarios
- [ ] Charts update correctly with assumption changes
- [ ] Print layout configured (margins, page breaks)
