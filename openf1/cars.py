from car import Car


def cars_from_api(drivers):
    cars = {}
    for driver in drivers:
        cars[driver["driver_number"]] = Car(
            number=driver["driver_number"],
            driver_name=driver["full_name"],
            driver_acronym=driver["name_acronym"],
            team_name=driver["team_name"],
            color=driver["team_colour"],
        )

    return cars
