import pandas as pd
from project_paths import data_file


def main() -> None:
    rounds = pd.read_csv(data_file("foodtruck_clean_rounds.csv"))
    print("Day-wise conditions:")
    for day in sorted(rounds["day"].unique()):
        day_data = rounds[rounds["day"] == day]
        print(f"\nDay {day}:")
        print(f"  n_rows: {len(day_data)}")
        print(f"  advice_shown_planned: {day_data['advice_shown_planned'].unique()}")
        print(f"  social_mode_planned: {day_data['social_mode_planned'].unique()}")


if __name__ == "__main__":
    main()
