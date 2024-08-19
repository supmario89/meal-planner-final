import pandas as pd
NUMBER_OF_MEALS = 4

class MenuManager:
    """
    A class to manage weekly meal planning.

    Attributes:
    ----------
    full_menu_df : DataFrame
        DataFrame containing the full menu.
    last_week_menu_df : DataFrame
        DataFrame containing last week's menu.
    week_meals_df : DataFrame or None
        DataFrame containing this week's meals.
    """

    def __init__(self, full_menu_filepath, last_week_menu_filepath):
        """
        Initializes the MenuManager with file paths to the full menu and last week's menu.

        Parameters:
        ----------
        full_menu_filepath : str
            The file path to the CSV file containing the full menu.
        last_week_menu_filepath : str
            The file path to the CSV file containing last week's menu.
        """
        self.full_menu_df = pd.read_csv(full_menu_filepath, dtype=str)
        self.last_week_menu_df = pd.read_csv(last_week_menu_filepath, dtype=str)
        self.week_meals_df = None

    def get_weeks_meals(self):
        #Number of meals can be changed for more days, days will need to be added to email manager
        """
        Generates this week's meals by sampling from the full menu, excluding meals from last week.

        This method merges the full menu with last week's menu to exclude previously selected meals,
        and then randomly samples 5 meals for this week.
        """
        df_poss_weekly_choices = (pd.merge(self.full_menu_df, self.last_week_menu_df,
                                           indicator=True, how='outer')
                                  .query('_merge=="left_only"')
                                  .drop('_merge', axis=1))
        self.week_meals_df = df_poss_weekly_choices.sample(NUMBER_OF_MEALS)

    def update_last_week(self, filepath):
        """
        Updates the CSV file with this week's meals, setting it as last week's meals for future use.

        Parameters:
        ----------
        filepath : str
            The file path to the CSV file where this week's meals will be saved.
        """
        if self.week_meals_df is not None:
            self.week_meals_df.to_csv(filepath, index=False)