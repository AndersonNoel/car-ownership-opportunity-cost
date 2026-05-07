import copy
import csv
import dataclasses

from car import Car
from car_data import all_cars
from calculations import generate_cost_data, print_assumptions, symulate

LABEL_WIDTH = 44
COL_WIDTH = 16


def _format_value(field_name: str, value) -> str:
    if isinstance(value, str):
        return value
    if field_name == "year":
        return str(value)
    if field_name == "odometer_miles":
        return f"{value:,} mi"
    if field_name == "mpg_combined":
        return str(value)
    if field_name == "years_to_live":
        return f"{value:.1f}"
    if isinstance(value, float):
        return f"${value:,.0f}"
    return str(value)


def _write_car_table(output_file, cars: list[Car], title: str) -> None:
    total_width = LABEL_WIDTH + COL_WIDTH * len(cars)

    output_file.write(f"{title}\n")
    output_file.write("═" * total_width + "\n")

    header = f"{'':>{LABEL_WIDTH}}"
    for i in range(len(cars)):
        header += f"{'Car ' + str(i + 1):^{COL_WIDTH}}"
    output_file.write(header + "\n")
    output_file.write("─" * total_width + "\n")

    for field in dataclasses.fields(Car):
        line = f"{field.name:<{LABEL_WIDTH}}"
        for car in cars:
            line += f"{_format_value(field.name, getattr(car, field.name)):>{COL_WIDTH}}"
        output_file.write(line + "\n")


def write_all_cars_to_file(output_file, sim1_cars: list[Car], sim2_cars: list[Car]) -> None:
    _write_car_table(output_file, sim1_cars, "Simulation 1 — symulate")
    output_file.write("\n")
    _write_car_table(output_file, sim2_cars, "Simulation 2 — generate_cost_data")


def write_all_cars_to_csv(csv_file, sim1_cars: list[Car], sim2_cars: list[Car]) -> None:
    writer = csv.writer(csv_file)

    for sim_label, cars in [("Simulation 1 — symulate", sim1_cars), ("Simulation 2 — generate_cost_data", sim2_cars)]:
        writer.writerow([sim_label] + [f"Car {i + 1}" for i in range(len(cars))])
        for field in dataclasses.fields(Car):
            writer.writerow([field.name] + [getattr(car, field.name) for car in cars])
        writer.writerow([])


def main():
    sim1_cars = copy.deepcopy(all_cars)
    sim2_cars = copy.deepcopy(all_cars)

    for car in sim1_cars:
        symulate(car)

    for car in sim2_cars:
        generate_cost_data(car)

    with open("output.txt", "w") as output_file:
        print_assumptions(output_file)
        write_all_cars_to_file(output_file, sim1_cars, sim2_cars)

    with open("output.csv", "w", newline="") as csv_file:
        write_all_cars_to_csv(csv_file, sim1_cars, sim2_cars)

    print("Results written to output.txt and output.csv")


if __name__ == "__main__":
    main()
