import smtplib
from email.message import EmailMessage

class EmailManager:
    """
    A class to manage email sending operations for the weekly meal planner.

    Attributes:
    ----------
    SENDER : str
        Email address of the sender.
    PASSWORD : str
        Email account password of the sender.
    RECIEVER : str
        Email address of the recipient.
    """

    SENDER = 'python.tester1989@gmail.com'
    PASSWORD = "eqcu xsvd shcu znnt"
    # RECIEVER = 'python.tester1989@gmail.com'
    RECIEVER = 'supmario89@gmail.com'

    @staticmethod
    def send_email(subject, content):
        """
        Sends an email with the given subject and content.

        Parameters:
        ----------
        subject : str
            The subject of the email.
        content : str
            The HTML content of the email.
        """
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EmailManager.SENDER
        msg['To'] = EmailManager.RECIEVER
        msg.set_content(content, subtype='html')
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EmailManager.SENDER, EmailManager.PASSWORD)
            smtp.send_message(msg)

    @staticmethod
    def create_email_content(menu_df, ingredients_prices, images, additional_grocery_list):
        """
        Creates the HTML content for the email based on the menu, ingredient prices, images, and additional grocery list.

        Parameters:
        ----------
        menu_df : pandas.DataFrame
            DataFrame containing the menu for the week.
        ingredients_prices : list
            List of ingredients with their prices.
        images : str
            HTML string containing images of some of the meals.
        additional_grocery_list : list
            List of additional grocery items to be included.

        Returns:
        -------
        str
            HTML content for the email.
        """
        # Can change number of meals by adding day and by changing variable in menu_manager
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        meals = menu_df['Meal'].values
        recipe_images = menu_df['Image'].values

        email_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }
                .container {
                    width: 600px;
                    margin: 0 auto;
                    background-color: #fff;
                    padding: 0px;
                }
                .header {
                    background-color: #5bc0de;
                    color: white;
                    text-align: center;
                    padding: 30px 0;
                    font-size: 40px;
                    font-weight: bold;
                }
                .day {
                    position: relative;
                    margin: 20px 0;
                    height: 150px; /* Adjust the height as needed */
                    background-size: cover;
                    background-position: center;
                }
                .day p {
                    position: absolute;
                    top: 120px;
                    left: 0;
                    width: 60%;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 5px 30px;
                    font-size: 18px;
                    display:inline-block;
                    margin: 0;
                    box-sizing: border-box;
                }
                .grocery-list {
                    background-color: #5bc0de;
                    padding: 10px;
                    color: white;
                    margin: 0px auto;
                    font-size: 16px;
                    width: 75%;
                    text-align: center;
                }
                .grocery-list ul {
                    list-style-type: none;
                    padding: 0;
                }
                .grocery-list ul li {
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    This Week's Menu!
                </div>
        """
        for i, day in enumerate(days):
            email_content += f"""<div class="day" style="background-image: url('{recipe_images[i]}');">
                                    <p><strong>{day}:</strong> {meals[i]}</p>
                                 </div>"""

        email_content += """<div class="grocery-list">
                            <h3><b><p>Grocery List</p></b></h3>
                            <ul>"""
        for ingredient in ingredients_prices:
            email_content += f"<li>{ingredient}</li>"
        email_content += "</ul><br>"
        
        email_content += """<div class="grocery-list">
                            <h3><b><p>Additional Grocery List</p></b></h3>
                            <ul>"""
        for item in additional_grocery_list:
            email_content += f"<li>{item}</li>"
        email_content += "</ul><br>"

        email_content += images
        email_content += """
            </div>
        </body>
        </html>"""

        return email_content