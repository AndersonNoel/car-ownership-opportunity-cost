from car import Car
from financial_helpers import future_value, total_inflation

# --- Assumptions ---
# Adjust these to model different scenarios.
GAS_PRICE_PER_GALLON: float = 3.5
MILES_PER_YEAR: float = 16500.0
TOTAL_CAR_MILEAGE: float = 250000.0      # assumed total lifespan of any car in miles
INFLATION_RATE: float = 0.03
RATE_OF_RETURN: float = 0.06
TOTAL_WORKING_BUDGET: float = 30000.0    # money available to spend on a car at purchase time

# Counterfactual annual budget: what you'd spend/invest each year if you weren't buying this car.
# Gas and repairs represent a reference baseline cost; savings go toward the next car.
MAX_REPAIR_COST_PER_YEAR: float = 700.0
REFERENCE_GAS_PER_YEAR: float = 3500.0
NEW_CAR_SAVINGS_PER_YEAR: float = 2500.00

# NEW_CAR_YEARS_TO_LIVE: the design lifespan of any car at 0 miles (used in lifespan comparisons
# and the age-dependent repair formula). ANALYSIS_YEARS is the integer period both simulations
# run over — truncated from the float so loop-based and formula-based calculations match
NEW_CAR_YEARS_TO_LIVE: float = TOTAL_CAR_MILEAGE / MILES_PER_YEAR
ANALYSIS_YEARS: int = int(NEW_CAR_YEARS_TO_LIVE)

def print_assumptions(output_file=None) -> None:
    lines = [
        f"{'─' * 40}",
        f"{'Assumptions':^40}",
        f"{'─' * 40}",
        f"{'Gas Price/Gallon':<28}${GAS_PRICE_PER_GALLON:.2f}",
        f"{'Miles per Year':<28}{MILES_PER_YEAR:,.0f}",
        f"{'Total Car Mileage':<28}{TOTAL_CAR_MILEAGE:,.0f}",
        f"{'Inflation Rate':<28}{INFLATION_RATE:.1%}",
        f"{'Rate of Return':<28}{RATE_OF_RETURN:.1%}",
        f"{'Total Working Budget':<28}${TOTAL_WORKING_BUDGET:,.2f}",
        f"{'Reference Gas/Year':<28}${REFERENCE_GAS_PER_YEAR:,.2f}",
        f"{'New Car Years to Live':<28}{NEW_CAR_YEARS_TO_LIVE:.1f}",
        f"{'New Car Savings/Year':<28}${NEW_CAR_SAVINGS_PER_YEAR:,.2f}",
        f"{'─' * 40}",
    ]
    for line in lines:
        if output_file:
            output_file.write(line + "\n")
    if output_file:
        output_file.write("\n")


def symulate(car: Car) -> None:
    """Year-by-year simulation comparing two portfolios over ANALYSIS_YEARS:

    Counterfactual: invest TOTAL_WORKING_BUDGET today, deposit the full annual
    budget (gas + savings + repair allowance) each year — as if you never bought a car.

    Actual: start with (TOTAL_WORKING_BUDGET - car.price), deposit the same annual
    budget minus what you actually spend on gas and repairs each year. When the car
    reaches end of life, buy a replacement of the same type and deduct its cost.

    All values are inflation-adjusted to today's dollars at the end.
    """

    gas_per_year = (MILES_PER_YEAR / car.mpg_combined) * GAS_PRICE_PER_GALLON
    car.years_to_live = (TOTAL_CAR_MILEAGE - car.odometer_miles) / MILES_PER_YEAR
    car.initial_car_age = car.odometer_miles / MILES_PER_YEAR

    # Combined annual deposit both portfolios receive before car-specific costs are subtracted.
    yealrly_budget = REFERENCE_GAS_PER_YEAR + NEW_CAR_SAVINGS_PER_YEAR + MAX_REPAIR_COST_PER_YEAR

    # Running totals for the two portfolios.
    countfactual = TOTAL_WORKING_BUDGET
    returns_with_car = TOTAL_WORKING_BUDGET - car.price

    # Itemized component accumulators — track each cost category separately so we can
    # attribute net cost to gas, repairs, purchase, and new-car savings independently.
    car.counterfactual_money_for_new_cars = 0.0
    car.actual_money_for_new_cars = 0.0
    car.counterfactual_purchase_investment = TOTAL_WORKING_BUDGET
    car.actual_purchase_investment = TOTAL_WORKING_BUDGET - car.price
    car.counterfactual_repair_investment = 0.0
    car.actual_repair_investment = 0.0
    car.counterfactual_gas_investment = 0.0
    car.actual_gas_investment = 0.0

    # i tracks years driven on the current car; resets to 0 each time a replacement is bought.
    i = 1
    equity_in_car = 0.0   # inflation-adjusted price of the most recently purchased replacement
    years_on_car = 0.0    # years the replacement car has been in service at end of analysis

    print(f"Simulating {car.make} {car.model} with initial car age of {car.initial_car_age:.1f} and price of ${car.price:.2f}")

    for year in range(1, int(NEW_CAR_YEARS_TO_LIVE) + 1):
        print(f"Year {year}: [1]={i} countfactual={countfactual:.2f} returns_with_car={returns_with_car:.2f}")

        # Grow both portfolios and add the annual budget deposit.
        countfactual = countfactual * (1 + RATE_OF_RETURN) + yealrly_budget

        # Repair cost increases linearly with total car age (initial age + years driven).
        # This reflects that older cars are more expensive to maintain.
        repair_cost_this_year = MAX_REPAIR_COST_PER_YEAR / NEW_CAR_YEARS_TO_LIVE * (car.initial_car_age + i)
        returns_with_car = returns_with_car * (1 + RATE_OF_RETURN) + yealrly_budget - gas_per_year - repair_cost_this_year

        # Itemized: each component compounds its own balance and receives its portion of
        # the annual deposit. The "actual" side subtracts real costs vs the reference baseline.
        car.counterfactual_gas_investment = car.counterfactual_gas_investment * (1 + RATE_OF_RETURN) + REFERENCE_GAS_PER_YEAR
        car.actual_gas_investment = car.actual_gas_investment * (1 + RATE_OF_RETURN) + REFERENCE_GAS_PER_YEAR - gas_per_year

        # Repair savings = what you would have spent at the reference rate minus what you actually paid.
        car.counterfactual_repair_investment = car.counterfactual_repair_investment * (1 + RATE_OF_RETURN) + MAX_REPAIR_COST_PER_YEAR
        car.actual_repair_investment = car.actual_repair_investment * (1 + RATE_OF_RETURN) + MAX_REPAIR_COST_PER_YEAR - repair_cost_this_year

        car.counterfactual_purchase_investment = car.counterfactual_purchase_investment * (1 + RATE_OF_RETURN)
        car.actual_purchase_investment = car.actual_purchase_investment * (1 + RATE_OF_RETURN)

        car.counterfactual_money_for_new_cars = car.counterfactual_money_for_new_cars * (1 + RATE_OF_RETURN) + NEW_CAR_SAVINGS_PER_YEAR
        car.actual_money_for_new_cars = car.actual_money_for_new_cars * (1 + RATE_OF_RETURN) + NEW_CAR_SAVINGS_PER_YEAR

        i += 1
        # Car reaches end of design life when (initial age + years driven) exceeds NEW_CAR_YEARS_TO_LIVE.
        # Deduct the inflation-adjusted purchase price of a same-type replacement.
        if i + car.initial_car_age > NEW_CAR_YEARS_TO_LIVE:
            equity_in_car = car.price * total_inflation(INFLATION_RATE, year)
            returns_with_car -= equity_in_car
            car.actual_money_for_new_cars -= equity_in_car
            years_on_car = NEW_CAR_YEARS_TO_LIVE - year  # fractional years the replacement is in service
            i = 0
            print(f"Purchased new car at year {year}, removing ${equity_in_car:.2f} from returns_with_car = {returns_with_car:.2f}")

    # If a replacement was bought, add back its residual value at end of analysis.
    # The car still has (years_to_live - years_on_car) of its life remaining, so we recover
    # that fraction of the purchase price rather than treating the whole cost as a loss.
    if equity_in_car != 0:
        residual = equity_in_car * (car.years_to_live - years_on_car) / car.years_to_live
        returns_with_car += residual
        car.actual_money_for_new_cars += residual
        print(f"Car has been driven for {years_on_car:.1f} years, with {car.years_to_live - years_on_car:.1f} years left, adding back ${residual:.2f} to returns_with_car for remaining value of car")

    # Convert all nominal end-of-period values to real (today's) dollars.
    car.counterfactual_repair_investment = car.counterfactual_repair_investment / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.actual_repair_investment = car.actual_repair_investment / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.total_repair_cost = car.counterfactual_repair_investment - car.actual_repair_investment

    car.counterfactual_money_for_new_cars = car.counterfactual_money_for_new_cars / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.actual_money_for_new_cars = car.actual_money_for_new_cars / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.actual_cost_of_new_cars = car.counterfactual_money_for_new_cars - car.actual_money_for_new_cars

    car.counterfactual_purchase_investment = car.counterfactual_purchase_investment / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.actual_purchase_investment = car.actual_purchase_investment / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.investment_ajusted_coast_of_purchase = car.counterfactual_purchase_investment - car.actual_purchase_investment
    # Combined purchase cost per year: opportunity cost of the down payment + net new-car spending.
    car.purchase_cost_per_year = (car.investment_ajusted_coast_of_purchase + car.actual_cost_of_new_cars) / ANALYSIS_YEARS

    car.counterfactual_gas_investment = car.counterfactual_gas_investment / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.actual_gas_investment = car.actual_gas_investment / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.total_gas_cost = car.counterfactual_gas_investment - car.actual_gas_investment
    car.gas_cost_per_year = car.total_gas_cost / ANALYSIS_YEARS

    # Itemized totals: sum of components should equal the single-portfolio totals below.
    car.counterfactual_opportunity_cost_simulation = (
        car.counterfactual_purchase_investment + car.counterfactual_repair_investment
        + car.counterfactual_gas_investment + car.counterfactual_money_for_new_cars
    )
    car.total_ending_assets_simulation = (
        car.actual_purchase_investment + car.actual_repair_investment
        + car.actual_gas_investment + car.actual_money_for_new_cars
    )

    # Single-portfolio totals computed directly from the running balances — used as a cross-check.
    car.counterfactual_opportunity_cost_total = countfactual / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.total_ending_assets_total = returns_with_car / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)

    car.net_cost_total = car.counterfactual_opportunity_cost_simulation - car.total_ending_assets_simulation
    car.net_cost_per_year = car.net_cost_total / ANALYSIS_YEARS


def generate_cost_data(car: Car) -> None:
    """Analytical version of the same counterfactual vs actual comparison.

    Where symulate runs a year-by-year loop, this function computes each component
    using closed-form future_value() calls where possible. Used cars that need
    replacement during the analysis period still require a loop for new-car savings.

    All outputs are real (inflation-adjusted) dollars, consistent with symulate.
    """

    car.years_to_live = (TOTAL_CAR_MILEAGE - car.odometer_miles) / MILES_PER_YEAR

    car.gas_cost_per_year = (MILES_PER_YEAR / car.mpg_combined) * GAS_PRICE_PER_GALLON
    car.total_gas_cost = car.gas_cost_per_year * ANALYSIS_YEARS

    # Gas savings vs the reference driver: positive means this car uses less gas.
    car.actual_gas_investment = future_value(
        present_value=0.0,
        annual_deposit=REFERENCE_GAS_PER_YEAR - car.gas_cost_per_year,
        rate=RATE_OF_RETURN,
        years=ANALYSIS_YEARS,
    ) / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)

    car.purchase_cost_per_year = car.price / car.years_to_live

    # Real value of (budget - purchase price) invested for the full analysis period.
    car.actual_purchase_investment = future_value(
        present_value=TOTAL_WORKING_BUDGET - car.price,
        annual_deposit=0.0,
        rate=RATE_OF_RETURN,
        years=ANALYSIS_YEARS,
    ) / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)

    # What TOTAL_WORKING_BUDGET + full annual deposits would grow to — the benchmark
    # against which all actual portfolios are compared.
    car.counterfactual_opportunity_cost_total = future_value(
        present_value=TOTAL_WORKING_BUDGET,
        annual_deposit=REFERENCE_GAS_PER_YEAR + NEW_CAR_SAVINGS_PER_YEAR + MAX_REPAIR_COST_PER_YEAR,
        rate=RATE_OF_RETURN,
        years=ANALYSIS_YEARS,
    ) / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)

    # Reference new-car savings: $NEW_CAR_SAVINGS_PER_YEAR invested every year for the
    # full period with no car purchases — the baseline for comparing actual new-car spending.
    car.counterfactual_money_for_new_cars = future_value(
        present_value=0.0,
        annual_deposit=NEW_CAR_SAVINGS_PER_YEAR,
        rate=RATE_OF_RETURN,
        years=ANALYSIS_YEARS,
    ) / total_inflation(INFLATION_RATE, ANALYSIS_YEARS)

    car.actual_repair_investment = 0.0
    car.counterfactual_repair_investment = 0.0

    if car.years_to_live < NEW_CAR_YEARS_TO_LIVE:
        # Used car: dies before the analysis period ends, so we simulate buying same-type
        # replacements. The repair formula offsets by (NEW_CAR_YEARS_TO_LIVE - years_to_live)
        # so that year 1 repair costs match where this car type sits on the age curve.
        print(f"{car.make} {car.model} will be driven for {car.years_to_live:.1f} years, which is less than the {NEW_CAR_YEARS_TO_LIVE:.1f} year analysis period.")

        i = 1
        last_car_purchase_year = 0
        car.actual_money_for_new_cars = 0.0
        for year in range(1, int(NEW_CAR_YEARS_TO_LIVE) + 1):
            print(f"Year {year}: i = {i}")
            actual_repair = (i + NEW_CAR_YEARS_TO_LIVE - car.years_to_live) * MAX_REPAIR_COST_PER_YEAR / NEW_CAR_YEARS_TO_LIVE
            car.counterfactual_repair_investment = car.counterfactual_repair_investment * (1 + RATE_OF_RETURN) + MAX_REPAIR_COST_PER_YEAR
            car.actual_repair_investment = car.actual_repair_investment * (1 + RATE_OF_RETURN) + MAX_REPAIR_COST_PER_YEAR - actual_repair

            if i < car.years_to_live:
                # Saving toward the next car purchase: grow existing balance then deposit.
                print(f"{car.actual_money_for_new_cars} -> {(car.actual_money_for_new_cars + NEW_CAR_SAVINGS_PER_YEAR) * (1 + RATE_OF_RETURN)}")
                car.actual_money_for_new_cars = car.actual_money_for_new_cars * (1 + RATE_OF_RETURN)
                car.actual_money_for_new_cars += NEW_CAR_SAVINGS_PER_YEAR
            else:
                # Car has reached end of life — buy a same-type replacement at today's inflated price.
                car.actual_money_for_new_cars -= car.price * total_inflation(INFLATION_RATE, year)
                print(f"Purchased new car for ${car.price * total_inflation(INFLATION_RATE, year):.2f} at year {year}")
                car.actual_money_for_new_cars += NEW_CAR_SAVINGS_PER_YEAR
                car.actual_money_for_new_cars = car.actual_money_for_new_cars * (1 + RATE_OF_RETURN)
                i = 0
                last_car_purchase_year = year
            i += 1

        # Add back the residual value of the last replacement car: it still has life left at
        # the end of the analysis period, so we recover that fraction of its purchase price.
        years_driven_on_last_car = NEW_CAR_YEARS_TO_LIVE - last_car_purchase_year
        residual_fraction = (car.years_to_live - years_driven_on_last_car) / car.years_to_live
        car.actual_money_for_new_cars += residual_fraction * (car.price * total_inflation(INFLATION_RATE, last_car_purchase_year))
        car.actual_money_for_new_cars /= total_inflation(INFLATION_RATE, ANALYSIS_YEARS)

    else:
        # New car (or very low-mileage used car): lasts the full analysis period without replacement.
        # Repair cost increases linearly from year 1 (brand new) to year ANALYSIS_YEARS (fully aged).
        # New-car savings equal the counterfactual since no car purchase is needed during the period.
        for year in range(1, int(NEW_CAR_YEARS_TO_LIVE) + 1):
            actual_repair = year * MAX_REPAIR_COST_PER_YEAR / NEW_CAR_YEARS_TO_LIVE
            car.counterfactual_repair_investment = car.counterfactual_repair_investment * (1 + RATE_OF_RETURN) + MAX_REPAIR_COST_PER_YEAR
            car.actual_repair_investment = car.actual_repair_investment * (1 + RATE_OF_RETURN) + MAX_REPAIR_COST_PER_YEAR - actual_repair

        car.actual_money_for_new_cars = car.counterfactual_money_for_new_cars

    # Positive = you spent less than the reference; negative = you spent more.
    car.actual_cost_of_new_cars = car.counterfactual_money_for_new_cars - car.actual_money_for_new_cars

    car.counterfactual_repair_investment /= total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.actual_repair_investment /= total_inflation(INFLATION_RATE, ANALYSIS_YEARS)
    car.total_repair_cost = car.counterfactual_repair_investment - car.actual_repair_investment

    car.total_ending_assets_total = (
        car.actual_money_for_new_cars + car.actual_gas_investment
        + car.actual_purchase_investment + car.actual_repair_investment
    )

    car.net_cost_total = car.counterfactual_opportunity_cost_total - car.total_ending_assets_total
    car.net_cost_per_year = car.net_cost_total / ANALYSIS_YEARS
