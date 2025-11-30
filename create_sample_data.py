import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Create a larger sample dataset for testing
np.random.seed(42)

# Items and their properties
items_data = [
    ('MILK', 'Milk', 'Dairy', 3.50, 0.30),
    ('BREAD', 'Bread', 'Bakery', 2.00, 0.25),
    ('BUTTER', 'Butter', 'Dairy', 4.00, 0.35),
    ('CEREAL', 'Cereal', 'Breakfast', 5.00, 0.40),
    ('EGGS', 'Eggs', 'Dairy', 3.00, 0.35),
    ('CHEESE', 'Cheese', 'Dairy', 6.00, 0.35),
    ('BANANA', 'Banana', 'Produce', 0.80, 0.50),
    ('APPLES', 'Apples', 'Produce', 2.50, 0.45),
    ('CHICKEN', 'Chicken', 'Meat', 12.00, 0.20),
    ('BEEF', 'Beef', 'Meat', 15.00, 0.25),
    ('POTATOES', 'Potatoes', 'Produce', 4.00, 0.40),
    ('RICE', 'Rice', 'Pantry', 2.50, 0.30),
    ('PASTA', 'Pasta', 'Pantry', 1.50, 0.35),
    ('TOMATOES', 'Tomatoes', 'Produce', 3.00, 0.50),
    ('SALAD', 'Salad', 'Prepared', 6.50, 0.25),
    ('SANDWICH', 'Sandwich', 'Prepared', 8.50, 0.20),
    ('COKE', 'Coke', 'Beverages', 2.50, 0.15),
    ('WATER', 'Water', 'Beverages', 1.00, 0.10),
    ('COFFEE', 'Coffee', 'Beverages', 4.50, 0.40),
    ('TEA', 'Tea', 'Beverages', 3.00, 0.35),
    ('JAM', 'Jam', 'Pantry', 3.50, 0.35),
    ('PEANUT_BUTTER', 'Peanut Butter', 'Pantry', 4.00, 0.40),
    ('YOGURT', 'Yogurt', 'Dairy', 2.50, 0.35),
    ('CORNFLAKES', 'Cornflakes', 'Breakfast', 4.50, 0.45),
    ('OATMEAL', 'Oatmeal', 'Breakfast', 3.50, 0.40)
]

# Association patterns to simulate
patterns = [
    # Breakfast patterns
    (['MILK'], ['CEREAL'], 0.6, 'morning'),
    (['MILK'], ['BREAD'], 0.4, 'morning'),
    (['BREAD'], ['JAM'], 0.5, 'morning'),
    (['CEREAL'], ['MILK'], 0.8, 'morning'),

    # Store-specific patterns
    (['CHEESE'], ['WINE'], 0.7, 'STORE_B'),
    (['PIZZA'], ['BEER'], 0.6, 'STORE_B'),

    # Lunch patterns
    (['SANDWICH'], ['COKE'], 0.9, 'midday'),
    (['SALAD'], ['WATER'], 0.8, 'midday'),

    # General patterns
    (['MILK'], ['EGGS'], 0.3, None),
    (['BREAD'], ['CHEESE'], 0.4, None),
]

# Generate transactions
transactions = []
transaction_id = 1

# Generate data for 30 days
start_date = datetime(2023, 1, 1)
for day in range(30):
    current_date = start_date + timedelta(days=day)

    # Generate 10-20 transactions per day
    daily_transactions = np.random.randint(10, 21)

    for trans in range(daily_transactions):
        store = 'STORE_A' if np.random.random() < 0.7 else 'STORE_B'
        hour = np.random.choice([8, 9, 12, 13, 18, 19, 20])  # Peak shopping hours
        timestamp = current_date.replace(hour=hour, minute=np.random.randint(0, 60))

        # Basket size 1-8 items
        basket_size = np.random.randint(1, 9)

        # Select items with some patterns
        basket_items = []

        # Start with some common items
        if np.random.random() < 0.4:  # 40% chance of milk
            basket_items.append('MILK')
            # Add cereal with some probability
            if np.random.random() < 0.6 and hour < 11:
                basket_items.append('CEREAL')

        if np.random.random() < 0.3:  # 30% chance of bread
            basket_items.append('BREAD')
            if np.random.random() < 0.5 and hour < 11:
                basket_items.append('JAM')

        # Add more random items
        available_items = [item[0] for item in items_data if item[0] not in basket_items]
        n_additional = min(basket_size - len(basket_items), len(available_items))
        if n_additional > 0:
            additional_items = np.random.choice(available_items, n_additional, replace=False)
            basket_items.extend(additional_items)

        # Ensure at least one item
        if not basket_items:
            basket_items = ['MILK']

        # Create transaction records
        for item_id in basket_items:
            item_info = next(item for item in items_data if item[0] == item_id)
            discount_flag = 1 if np.random.random() < 0.1 else 0  # 10% discount rate

            transactions.append({
                'transaction_id': f'T{transaction_id:04d}',
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'store_id': store,
                'item_id': item_id,
                'price': item_info[3],
                'item_name': item_info[1],
                'category': item_info[2],
                'quantity': 1,
                'customer_id_hash': f'CUST{np.random.randint(1, 201):03d}',
                'discount_flag': discount_flag,
                'margin_pct': item_info[4]
            })

        transaction_id += 1

# Create DataFrame and save
df = pd.DataFrame(transactions)
df.to_csv('data/sample/sample_1k.csv', index=False)

print(f"Generated {len(df)} transaction items in {df['transaction_id'].nunique()} transactions")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Stores: {df['store_id'].unique()}")
print(f"Items: {df['item_id'].nunique()} unique items")
print(f"Categories: {df['category'].unique()}")
