import pandas as pd
import requests
import random
import os
from email_manager import EmailManager
from menu_manager import MenuManager
from concurrent.futures import ThreadPoolExecutor, as_completed

class MealDataProcessor:
    """
    A class to process meal data and manage grocery lists.

    Attributes:
    ----------
    menu_df : pandas.DataFrame
        DataFrame containing the menu for the week.
    separate_grocery_list_path : str
        Path to the file containing the separate weekly grocery list.
    alternate_grocery_list_path : str
        Path to the file containing the bi-weekly grocery list.
    counter_file : str
        Path to the file storing the run count.
    aisle_numbers_path : str
        Path to the CSV file containing aisle numbers for ingredients.
    ingredients : list
        List of ingredients for the week's menu.
    aisle_numbers : dict
        Dictionary mapping ingredients to aisle numbers.
    separate_grocery_list : list
        List of items in the separate weekly grocery list.
    alternate_grocery_list : list
        List of items in the bi-weekly grocery list.
    meals_dict : dict
        Dictionary representation of the menu DataFrame.
    run_count : int
        Counter to keep track of the number of runs.
    """

    def __init__(self, menu_df, separate_grocery_list_path, alternate_grocery_list_path, counter_file, aisle_numbers_path):
        """
        Initializes the MealDataProcessor with menu and grocery list paths.

        Parameters:
        ----------
        menu_df : pandas.DataFrame
            DataFrame containing the menu for the week.
        separate_grocery_list_path : str
            Path to the file containing the separate weekly grocery list.
        alternate_grocery_list_path : str
            Path to the file containing the bi-weekly grocery list.
        counter_file : str
            Path to the file storing the run count.
        aisle_numbers_path : str
            Path to the CSV file containing aisle numbers for ingredients.
        """
        self.menu_df = menu_df
        self.separate_grocery_list_path = separate_grocery_list_path
        self.alternate_grocery_list_path = alternate_grocery_list_path
        self.counter_file = counter_file
        self.aisle_numbers_path = aisle_numbers_path
        self.ingredients = []
        self.aisle_numbers = self.load_aisle_numbers()
        self.separate_grocery_list = self.load_separate_grocery_list()
        self.alternate_grocery_list = self.load_alternate_grocery_list()
        self.meals_dict = menu_df.to_dict(orient='list')
        self.run_count = self.load_run_count()

    def load_separate_grocery_list(self):
        """
        Loads the separate weekly grocery list from a file.

        Returns:
        -------
        list
            List of items in the separate weekly grocery list.
        """
        with open(self.separate_grocery_list_path, 'r') as file:
            return [line.strip() for line in file]

    def load_alternate_grocery_list(self):
        """
        Loads the bi-weekly grocery list from a file.

        Returns:
        -------
        list
            List of items in the bi-weekly grocery list.
        """
        with open(self.alternate_grocery_list_path, 'r') as file:
            return [line.strip() for line in file]

    def load_aisle_numbers(self):
        """
        Loads the aisle numbers for ingredients from a CSV file.

        Returns:
        -------
        dict
            Dictionary mapping ingredients to aisle numbers.
        """
        return pd.read_csv(self.aisle_numbers_path).set_index('Ingredient')['Aisle'].to_dict()

    def load_run_count(self):
        """
        Loads the run count from a file.

        Returns:
        -------
        int
            The number of times the code has been run.
        """
        if os.path.exists(self.counter_file):
            with open(self.counter_file, 'r') as file:
                return int(file.read().strip())
        else:
            return 0

    def save_run_count(self):
        """
        Saves the current run count to a file.
        """
        with open(self.counter_file, 'w') as file:
            file.write(str(self.run_count))

    def increment_run_count(self):
        """
        Increments the run count and saves it to a file.
        """
        self.run_count += 1
        self.save_run_count()

    def get_ingredients(self):
        """
        Extracts and sorts the ingredients for the week's menu by aisle number.
        """
        ingredients = [i.split(',')[0:] for i in self.meals_dict['Ingredients']]
        ingredients = set([item.strip().title() for sublist in ingredients for item in sublist])
        self.ingredients = sorted(ingredients, key=lambda x: self.aisle_numbers.get(x.title(), float('inf')))
        # print("Sorted ingredients by aisle:", self.ingredients)  # Debug print

    def fetch_price_and_image(self, item):
        """
        Fetches the price and image URL for an ingredient from an external API.

        Parameters:
        ----------
        item : str
            The ingredient to fetch price and image for.

        Returns:
        -------
        tuple
            A tuple containing the ingredient with its price and the image HTML tag.
        """
        formatted_item = item.replace(" ", "%20")
        url = f"https://api.aldi.us/v1/catalog-search-product-offers?currency=USD&q={formatted_item}&sort=relevance&merchantReference=474-116"
        response = requests.get(url)
        price = "Not available"
        image = ""
        try:
            data = response.json()
            price = data["data"][0]["attributes"]['catalogSearchProductOfferResults'][0]['prices'][0]['formattedPrice']
            image_url = data["data"][0]["attributes"]['catalogSearchProductOfferResults'][0]['images'][0]['externalUrlLarge']
            image_url = image_url.strip("{slug}").replace("{width}", "116")
            image = f"<img src={image_url} alt={item} height='116'>"
        except (IndexError, KeyError):
            pass
        return f'{item}: {price}', image

    def get_price_and_images(self):
        """
        Fetches prices and images for all ingredients concurrently.

        Returns:
        -------
        tuple
            A tuple containing a list of ingredients with prices and a string of HTML image tags.
        """
        new_ingredients = [None] * len(self.ingredients)
        image_list = [None] * len(self.ingredients)
        
        with ThreadPoolExecutor(max_workers=30) as executor:
            future_to_index = {executor.submit(self.fetch_price_and_image, item): idx for idx, item in enumerate(self.ingredients)}
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    content, image = future.result()
                    new_ingredients[idx] = content
                    image_list[idx] = image
                except Exception as e:
                    print(f"Error fetching data for {self.ingredients[idx]}: {e}")

        images = random.sample([img for img in image_list if img is not None], min(len(image_list), 4))
        images = ' '.join(images)
        return new_ingredients, images

    def get_additional_grocery_list(self):
        """
        Combines the separate and bi-weekly grocery lists, including bi-weekly items every other run.

        Returns:
        -------
        list
            Combined list of grocery items.
        """
        combined_list = self.separate_grocery_list[:]
        if self.run_count % 2 == 1:
            combined_list += self.alternate_grocery_list
        self.increment_run_count()
        return combined_list

def main():
    """
    Main function to execute the meal data processing and send the weekly meal plan email.
    """
    full_menu_filepath = 'src/data/Full_menu.csv'
    last_week_menu_filepath = 'src/data/last_week_meals.csv'
    separate_grocery_list_path = 'src/data/weekly_grocery_list.txt'
    alternate_grocery_list_path = 'src/data/bi_weekly_grocery_list.txt'
    counter_file = 'src/data/run_counter.txt'
    aisle_numbers_path = 'src/data/aisle_numbers.csv'

    menu_manager = MenuManager(full_menu_filepath, last_week_menu_filepath)
    menu_manager.get_weeks_meals()
    menu_manager.update_last_week(last_week_menu_filepath)

    meal_data_processor = MealDataProcessor(menu_manager.week_meals_df, separate_grocery_list_path, alternate_grocery_list_path, counter_file, aisle_numbers_path)
    meal_data_processor.get_ingredients()
    ingredients_prices, images = meal_data_processor.get_price_and_images()
    additional_grocery_list = meal_data_processor.get_additional_grocery_list()

    if menu_manager.week_meals_df is not None and not menu_manager.week_meals_df.empty:
        email_content = EmailManager.create_email_content(menu_manager.week_meals_df, ingredients_prices, images, additional_grocery_list)
        EmailManager.send_email('ILY Weekly Food Menu', email_content)
    else:
        print("No meals available to send.")

if __name__ == '__main__':
    main() 
#RUN FROM SRC Folder
# export PYTHONPATH="${PYTHONPATH}:Kelsey_food_copy/Weekly_Meal_Planner/src"
    # export PYTHONPATH="${PYTHONPATH}:/Users/casaazul/Desktop/Python_Camp2/Kelsey_food_copy/Weekly_Meal_Planner/src"

# pip install sphinx
# sphinx-quickstart docs/api
# sphinx-apidoc -o docs/api/source src/
# cd docs/api
# make html
    

# def main():
#     full_menu_filepath = 'src/data/Full_menu.csv'
#     last_week_menu_filepath = 'src/data/last_week_meals.csv'
#     separate_grocery_list_path = 'src/data/weekly_grocery_list.txt'
#     alternate_grocery_list_path = 'src/data/bi_weekly_grocery_list.txt'
#     counter_file = 'src/data/run_counter.txt'
#     aisle_numbers_path = 'src/data/aisle_numbers.csv'
    
    /home/klinux1989/Weekly_Meal_Planner/src/send_email.py