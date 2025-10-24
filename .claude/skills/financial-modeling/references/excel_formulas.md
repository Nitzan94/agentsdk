# Advanced Excel Formulas for Financial Modeling

## Financial Functions

### IRR (Internal Rate of Return)
```
=IRR(cash_flows, [guess])

Example:
=IRR(B2:B10, 0.1)
Returns: 0.1543 (15.43%)

Use: Calculate investment return rate where NPV = 0
Caution: Returns only first solution; multiple rates may exist
```

### NPV (Net Present Value)
```
=NPV(rate, value1, [value2], ...)

Example:
=NPV(0.10, B2:B10) - B1
Note: B1 is initial investment (negative), NPV excludes it
Returns: Present value of cash flows

Use: Discount future cash flows to present value
```

### MIRR (Modified Internal Rate of Return)
```
=MIRR(values, finance_rate, reinvest_rate)

Example:
=MIRR(B2:B10, 0.08, 0.12)
Returns: Modified IRR accounting for reinvestment rate

Use: More realistic than IRR when assuming reinvestment
```

### PV (Present Value)
```
=PV(rate, nper, pmt, [fv], [type])

Example:
=PV(0.08, 5, -1000, 0, 0)
Returns: Present value of annuity

Use: Calculate PV of regular payments
```

### FV (Future Value)
```
=FV(rate, nper, pmt, [pv], [type])

Example:
=FV(0.05, 10, -1000, -5000, 0)
Returns: Future value after 10 years of $1000 annual payments

Use: Calculate compound growth
```

### RATE (Discount Rate)
```
=RATE(nper, pmt, pv, [fv], [type], [guess])

Example:
=RATE(5, -1000, 5000, -2000)
Returns: Rate needed to grow $5000 to $2000 with $1000 payments

Use: Solve for discount rate
```

## Lookup & Reference Functions

### VLOOKUP (Vertical Lookup)
```
=VLOOKUP(lookup_value, table_array, col_index_num, [range_lookup])

Example:
=VLOOKUP("Revenue Growth", Assumptions!A:B, 2, FALSE)
Returns: Value from column 2 matching lookup

Use: Find values in table (exact match: FALSE, approximate: TRUE)
Limitation: Can only look right
```

### INDEX & MATCH (Better than VLOOKUP)
```
=INDEX(return_array, MATCH(lookup_value, lookup_array, 0))

Example:
=INDEX(Assumptions!B:B, MATCH("Revenue Growth", Assumptions!A:A, 0))
Returns: Same as VLOOKUP but more flexible

Use: Horizontal lookups, multiple criteria
Advantage: Can look left or right
```

### HLOOKUP (Horizontal Lookup)
```
=HLOOKUP(lookup_value, table_array, row_index_num, [range_lookup])

Example:
=HLOOKUP(2024, Years!1:5, 2, FALSE)
Returns: Value in row 2 of column matching 2024

Use: When lookup values are in rows (not columns)
```

### INDIRECT (Dynamic References)
```
=INDIRECT(cell_ref_text)

Example:
=INDIRECT("Assumptions!B"&COLUMN())
Returns: Dynamic reference based on current column

Use: Build flexible formulas that adapt to copying
Advanced: Create scenarios that reference different assumption sets
```

## Array Formulas

### SUMPRODUCT (Array Sum with Conditions)
```
=SUMPRODUCT(array1, array2, ...)

Example:
=SUMPRODUCT((Revenue > 100) * FCF)
Returns: Sum of FCF where Revenue > 100

Use: Sum with multiple conditions
Advanced: =SUMPRODUCT(Cash_Flows / (1 + Rate) ^ ROW(Cash_Flows))
```

### SUM with IF (Conditional Sum - Array Formula)
```
=SUM(IF(condition, sum_range, 0))
Enter with Ctrl+Shift+Enter

Example:
=SUM(IF(Year >= 2024, FCF, 0))
Returns: Sum of FCF for years 2024 forward

Use: Complex conditions (multiple IF statements)
```

### SUMIFS (Conditional Sum - Simpler)
```
=SUMIFS(sum_range, criteria_range1, criteria1, ...)

Example:
=SUMIFS(FCF, Year, ">= 2024", Scenario, "Base Case")
Returns: Sum of FCF matching multiple criteria

Use: Preferred over array formulas (no Ctrl+Shift+Enter)
```

## Logical Functions

### IF (Conditional)
```
=IF(condition, value_if_true, value_if_false)

Example:
=IF(Revenue > 100, 0.25, 0.20)
Returns: 25% commission if revenue > 100, else 20%

Use: Simple conditional logic
Nested: =IF(A > B, "High", IF(A > C, "Medium", "Low"))
Limit: Don't nest more than 3 levels
```

### IFS (Multiple Conditions)
```
=IFS(condition1, value1, condition2, value2, ...)

Example:
=IFS(Revenue > 500, 0.30, Revenue > 100, 0.25, TRUE, 0.20)
Returns: Tiered commission based on revenue

Use: Cleaner than nested IF
Advantage: Easier to read and maintain
```

### CHOOSE (Select from List)
```
=CHOOSE(index_num, value1, value2, ...)

Example:
=CHOOSE(Scenario_Number, Bull_Case, Base_Case, Bear_Case)
Returns: Value based on scenario number

Use: Alternative to nested IF for lists
```

### AND / OR (Multiple Conditions)
```
=AND(condition1, condition2, ...)
=OR(condition1, condition2, ...)

Example:
=IF(AND(Revenue > 100, FCF > 50), "Strong", "Weak")
Returns: "Strong" only if both conditions true

Use: Combine multiple conditions in IF statements
```

## Text Functions

### CONCATENATE / & (Combine Text)
```
=A1 & " - " & B1
or
=CONCATENATE(A1, " - ", B1)

Example:
="Year " & 2024 & ": " & Revenue & "M"
Returns: "Year 2024: 100M"

Use: Build labels and dynamic text
Modern: Use & operator (simpler)
```

### TEXT (Format Numbers as Text)
```
=TEXT(value, format_code)

Example:
=TEXT(0.15, "0.0%")
Returns: "15.0%"

Use: Format numbers in formulas
Finance: =TEXT(1000000, "$#,##0,, \"M\"")
Returns: "$1M"
```

### LEFT / RIGHT / MID (Extract Text)
```
=LEFT(text, num_chars)
=RIGHT(text, num_chars)
=MID(text, start_num, num_chars)

Example:
=LEFT("2024-10-15", 4)
Returns: "2024"

Use: Parse dates, codes, identifiers
```

## Math Functions

### ROUND (Rounding)
```
=ROUND(number, num_digits)

Example:
=ROUND(1234.5678, 2)
Returns: 1234.57

Financial Modeling: Use 0 decimals for thousands, 2 for percentages
```

### ABS (Absolute Value)
```
=ABS(number)

Example:
=ABS(-100)
Returns: 100

Use: Convert negative to positive
Finance: Calculate variance magnitude
```

### POWER (Exponentiation)
```
=POWER(number, power)

Example:
=POWER(1.05, 10)
Returns: 1.6289 (5% growth over 10 years)

Use: Compound growth calculations
CAGR: =POWER(End/Start, 1/Years) - 1
```

### MIN / MAX (Extreme Values)
```
=MIN(array)
=MAX(array)

Example:
=MAX(FCF_Scenarios)
Returns: Highest FCF across scenarios

Use: Sensitivity ranges, valuation bounds
```

### AVERAGE / MEDIAN (Central Tendency)
```
=AVERAGE(array)
=MEDIAN(array)

Example:
=MEDIAN(Comparable_Multiples)
Returns: Median valuation multiple

Use: Statistical analysis of comps
```

## Date Functions

### TODAY / NOW (Current Date/Time)
```
=TODAY()
Returns: Today's date (updates daily)

Use: Model refresh date, age calculations
Caution: Volatile; recalculates on every change
```

### DATE (Create Dates)
```
=DATE(year, month, day)

Example:
=DATE(2024, 10, 15)
Returns: 10/15/2024

Use: Dynamic date construction
```

### YEAR / MONTH / DAY (Extract from Date)
```
=YEAR(date)
=MONTH(date)
=DAY(date)

Example:
=YEAR(TODAY())
Returns: 2024

Use: Extract date components
```

### DATEDIF (Days Between Dates)
```
=DATEDIF(start_date, end_date, "D")

Example:
=DATEDIF(A1, TODAY(), "D")
Returns: Days since A1

Use: Calculate holding periods, age
```

## Financial Modeling Patterns

### Pattern 1: Waterfall Calculation
```
=IF(Row=1, Starting_Value, Previous_Row + Current_Change)

Example:
Year 1: =100 (starting revenue)
Year 2: =B2 * (1 + growth_rate)
Year 3: =B3 * (1 + growth_rate)
```

### Pattern 2: Tiered Calculation with Growth Moderation
```
=IF(Year <= 3, Base_Growth, IF(Year <= 5, Mid_Growth, Terminal_Growth))

Example:
Growth Rate = IF(COLUMN() <= 4, 0.20, IF(COLUMN() <= 6, 0.10, 0.03))
Returns: 20% years 1-3, 10% years 4-5, 3% year 6+
```

### Pattern 3: Scenario Switch
```
=IF($Scenario_Cell = "Bull", Bull_Value, IF($Scenario_Cell = "Base", Base_Value, Bear_Value))

Example:
Revenue = IF($A$1 = "Bull", Revenue_Bull, IF($A$1 = "Base", Revenue_Base, Revenue_Bear))
```

### Pattern 4: Safe Division (Avoid #DIV/0!)
```
=IF(Denominator = 0, 0, Numerator / Denominator)

Example:
Margin = IF(Revenue = 0, 0, EBIT / Revenue)
```

### Pattern 5: Present Value Series
```
=SUMPRODUCT(Cash_Flows / (1 + Rate) ^ ROW(Cash_Flows))

Example:
PV_FCF = SUMPRODUCT(FCF_Array / (1 + WACC) ^ ROW(FCF_Array))
Calculates PV of entire FCF stream in one formula
```

### Pattern 6: Compound Growth
```
=Starting_Value * (1 + Growth_Rate) ^ Number_of_Periods

Example:
Revenue_2030 = Revenue_2024 * (1 + CAGR) ^ 6
```

### Pattern 7: Interpolation (Find Value Between Points)
```
=Low_Value + (High_Value - Low_Value) * (Target - Low_Point) / (High_Point - Low_Point)

Example:
VAR_Rate = IF(Credit_Score >= 700, 5%, IF(Credit_Score >= 650, 
  5% + (6% - 5%) * (700 - Credit_Score) / (700 - 650), 6%))
```

### Pattern 8: Cross-Validation
```
=IF(Calc_Method1 <> Calc_Method2, "ERROR", "OK")

Example:
Check = IF(Total_Assets <> Total_Liabilities + Equity, "ERROR", "OK")
Validates balance sheet
```

## Performance Tips

### Volatile Functions to Avoid
- **TODAY()** / **NOW()**: Recalculate on every change
- **RAND()**: Random number generator
- **INDIRECT()**: Volatile in some versions

**Solution**: Use sparingly or update manually

### Array Formula Optimization
Instead of:
```
=SUM(IF(Range > 100, Range * 0.25, Range * 0.20))
```

Use SUMPRODUCT:
```
=SUMPRODUCT((Range > 100) * Range * 0.25) + SUMPRODUCT((Range <= 100) * Range * 0.20)
```

### Large Range Management
- Specify exact ranges instead of entire columns
- **Bad**: `=SUM(A:A)`
- **Good**: `=SUM(A2:A1000)`

### Circular Reference Prevention
- Never create: Formula in A1 references A1
- Use: Helper columns or multi-step calculations
- Check: Formulas → Error Checking → Circular References

## Common Financial Formulas Summary

| Calculation | Formula |
|-------------|---------|
| CAGR | `=POWER(Ending/Beginning, 1/Years) - 1` |
| IRR | `=IRR(Cash_Flows)` |
| NPV | `=NPV(Rate, CF1:CFn) + Initial_CF` |
| WACC | `=(E/V * Re) + (D/V * Rd * (1-Tax))` |
| Free Cash Flow | `=EBIT*(1-Tax) + D&A - CapEx - ∆NWC` |
| Terminal Value | `=FCF * (1+g) / (WACC - g)` |
| Payback Period | `=Initial / Annual_CF` |
| ROE | `=Net Income / Equity` |
| Debt/Equity | `=Total Debt / Total Equity` |
| Interest Coverage | `=EBIT / Interest Expense` |

