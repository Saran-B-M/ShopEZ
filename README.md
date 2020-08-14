# ShopEZ
ShopEZ is a e-commerce webiste made with 
Frontend:
HTML
CSS
BOOTSTRAP-4

Backend:
Flask

## Installation

Use the requirements.txt to install the required modules in your virtual enivironment

```bash
pip install -r requirements.txt
```

## Usage

Run the following commands in your shell to create the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

Configure the mail credentials in app/config to enable password reseting functionality. 
In your gmail enable insecure apps to use this email to mail users

Run the following command to run the server:
```bash
flask run
```

Admin email address: admin@shopez.com,
Admin password: password

login as admin and go to http://localhost:[your-port]/add-product to add Products.
As of now the categories are shirt, pant, shoe.
Add atleast 4 products in each category.
As admin go to http://localhost:[your-port]/admin to perform basic CRUD operations and View received orders
