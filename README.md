# chatBot_for_Food_Business
ABOUT PROJECT:
---------------
1) This is an Integrated Intermediate service(chatBot) for the users to place a new order, track the orders(via order ID and mobile number), and Store hours via this chatBot platform.
2) DialogFlow is used as the chatBot platform which is then integrated into my own website.
3) Whenever the user types his request through the chatBot, an Intent with the associated training phrase will match and the corresponding response will be displayed.
4) DialogFlow Contexts are used to handle the flow of the Intents.
5) Order status is automated. i.e. (Initially it will be as 'Being Prepared' and then after 20 min it will be 'In transit' and after the 45 minutes it wil be as 'Delivered'.
6) Backend server (FastAPI(python)) is called whenever the webhook request is enabled for the Intents, which will retrieve the data from the database (MySQL)

PROJECT STATUS:
-----------------
1) Currently the user can place an order, track an order, and view the store hours.
2) It can also be improved by sending messages to users once the order is delivered.
3) Retrieve the past and current orders of the users.
4) Support payment through the chatBot.

DEMO VIDEO:
------------
[Demo Video](https://drive.google.com/file/d/1Peft0vjxJ7G_ZNLwub_6q91RcZDRyD41/view?usp=drive_link)
