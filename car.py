from dataclasses import dataclass


@dataclass
class Car:
    make: str
    model: str
    trim: str
    year: int
    odometer_miles: int
    price: float
    mpg_combined: float

    years_to_live: float = 0.0

    # gas costs
    counterfactual_gas_investment: float = 0.0
    actual_gas_investment: float = 0.0
    gas_cost_per_year: float = 0.0
    total_gas_cost: float = 0.0
   
    # purchase costs
    counterfactual_purchase_investment: float = 0.0
    actual_purchase_investment: float = 0.0
    investment_ajusted_coast_of_purchase: float = 0.0
    purchase_cost_per_year: float = 0.0
    
    # repair costs
    total_repair_cost: float = 0.0
    counterfactual_repair_investment: float = 0.0
    actual_repair_investment: float = 0.0

    # money for new car
    actual_money_for_new_cars: float = 0.0
    counterfactual_money_for_new_cars: float = 0.0
    actual_cost_of_new_cars: float = 0.0

    counterfactual_opportunity_cost_simulation: float = 0.0
    counterfactual_opportunity_cost_total: float = 0.0
    total_ending_assets_total: float = 0.0
    total_ending_assets_simulation: float = 0.0
    net_cost_total: float = 0.0
    net_cost_per_year: float = 0.0
    
    


