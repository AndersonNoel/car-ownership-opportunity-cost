def future_value(present_value: float, annual_deposit: float, rate: float, years: float) -> float:
    """Calculate the future value of an investment with regular annual deposits.

    Args:
        present_value:  Starting balance of the investment.
        annual_deposit: Amount deposited each year.
        rate:           Annual rate of return as a decimal (e.g. 0.07 for 7%).
        years:          Number of years the investment grows.

    Returns:
        The total value of the investment after the given number of years.

    Raises:
        ValueError: If rate is zero (division by zero in the annuity formula).
    """
    if rate == 0.0:
        raise ValueError("rate must be non-zero")
    fv_lump_sum = present_value * (1 + rate) ** years
    fv_deposits = annual_deposit * (((1 + rate) ** years - 1) / rate)
    return fv_lump_sum + fv_deposits


def total_inflation(rate: float, years: float) -> float:
    """Calculate the cumulative inflation multiplier over a number of years.

    Args:
        rate:  Annual inflation rate as a decimal (e.g. 0.03 for 3%).
        years: Number of years to compound over.

    Returns:
        Total fractional increase due to inflation (e.g. 0.344 means 34.4% more expensive).
    """
    return (1 + rate) ** years
