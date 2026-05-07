# Car Ownership Opportunity Cost

A Python tool that compares the true financial cost of different car purchases by modeling the opportunity cost of money spent on gas, repairs, and the purchase price itself.

## How It Works

Each car is evaluated against a counterfactual: what would your money be worth if you had invested it instead? The tool tracks four cost components:

- **Purchase** — opportunity cost of the down payment (money no longer invested)
- **Gas** — actual fuel cost vs a reference driver's spending
- **Repairs** — actual repair costs vs a flat annual repair budget
- **New-car savings** — money saved toward replacement cars vs the reference driver's savings

Both simulations run over the same analysis period (`ANALYSIS_YEARS`) and output all values in real (inflation-adjusted) dollars.

## Simulations

**Simulation 1 — `symulate`**: Year-by-year loop. Tracks two running investment portfolios (counterfactual and actual) and compounds each cost component independently. Replacement cars are purchased when the current car reaches end of life.

**Simulation 2 — `generate_cost_data`**: Closed-form calculation using future value formulas where possible. Used cars that need replacement still use a loop for the new-car savings component.

## Usage

1. Edit `car_data.py` to add the cars you want to compare.
2. Adjust assumptions in `calculations.py` (gas price, miles per year, rate of return, etc.).
3. Run:
   ```
   python main.py
   ```
4. Results are written to `output.txt` (formatted table) and `output.csv` (spreadsheet-ready).

## Files

| File | Purpose |
|---|---|
| `main.py` | Runs both simulations and writes output |
| `calculations.py` | Core simulation logic and assumptions |
| `car.py` | `Car` dataclass — all input and output fields |
| `car_data.py` | The list of cars to compare |
| `financial_helpers.py` | `future_value()` and `total_inflation()` helpers |

## Key Concepts

**Counterfactual**: The benchmark portfolio — invest `TOTAL_WORKING_BUDGET` today and deposit the full annual budget every year, as if you never bought a car.

**Net cost**: `counterfactual_ending_assets - actual_ending_assets`. Lower is better; it represents how much owning this car cost you relative to just investing the money.

**`NEW_CAR_YEARS_TO_LIVE`**: The design lifespan of a brand-new car (`TOTAL_CAR_MILEAGE / MILES_PER_YEAR`). Used for lifespan comparisons and the age-dependent repair formula.

**`ANALYSIS_YEARS`**: The integer number of years both simulations run over (`int(NEW_CAR_YEARS_TO_LIVE)`). Truncated so loop-based and formula-based calculations produce the same result.
