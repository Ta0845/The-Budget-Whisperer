import easyocr
import re

reader = easyocr.Reader(['en']) #Creates OCR
results = reader.readtext('img/receipt.png') #reads all the text using one receipt for now for testing
# Common issues could be how the OCR scans the total could affect the total itself if split 

with open('store_names.txt', 'r') as file: ## This loads all the preset store names we have we use these to find the store names in the text we have
    known_stores = file.read().splitlines()

numbers = []
all_text = []

# --- TOTAL ---
# This pattern finds prices like:
# 12.99
# 5.00
# 147.50
# 1.25
for result in results:
    text = result[1]
    all_text.append(text)
    
    found_prices = re.findall(r'\d+\.\d{2}', text)
    for price in found_prices:
        numbers.append(float(price))

# --- STORE NAME ---
all_text_combined = " ".join(all_text).lower()
store_name = "nil"
for store in known_stores:
    if store in all_text_combined:
        store_name = store.title()
        break

# --- DATE ---
# This pattern finds dates like:
# 01/15/2024
# 1-5-24
# 12/31/99
date_found = "nil"
for text in all_text:
    date_match = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
    if len(date_match) > 0:
        date_found = date_match[0]
        break

total = max(numbers) if len(numbers) > 0 else 0.00

# Print the receipt info
print([store_name, date_found, total])

#Saving to a file
line_to_save = store_name + ", " + date_found + ", " + str(total) + "\n" # Format: Store, Date, Total (one receipt per line)
with open('receipt_data.txt', 'a') as file:
    file.write(line_to_save)