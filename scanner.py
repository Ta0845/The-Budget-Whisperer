import easyocr
import cv2
import re

MAX_DIM = 2000  # EasyOCR handles images up to ~2000px reliably

def load_image(path):
    img = cv2.imread(path)
    h, w = img.shape[:2]
    if max(h, w) > MAX_DIM:
        scale = MAX_DIM / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
    return img

reader = easyocr.Reader(['en']) #Creates OCR
results = reader.readtext(load_image('img/receipt3.png')) #reads all the text using one receipt for now for testing
# Common issues could be how the OCR scans the total could affect the total itself if split 

with open('store_names.txt', 'r') as file:
    known_stores = file.read().splitlines()

with open('total_names.txt', 'r') as file:
    total_labels = [line.strip().lower() for line in file if line.strip()]

all_text = []
all_prices = []  # every price found (fallback)

for result in results:
    text = result[1]
    all_text.append(text)
    for price in re.findall(r'\d+\.\d{2}', text):
        all_prices.append(float(price))

all_text_combined = " ".join(all_text).lower()
store_name = "nil"
for store in known_stores:
    if store in all_text_combined:
        store_name = store.title()
        break

date_found = "nil"
for text in all_text:
    date_match = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
    if len(date_match) > 0:
        date_found = date_match[0]
        break

# Find the total by looking for a total label, then checking that result and
# the next 2 results for a price (label and price are often separate OCR chunks).
# Use the LAST match so grand total wins over subtotal. 
# 
# This was a fix for stores who use mult totals and helps base a idea and we can add more totals to fix more more receipts
labeled_prices = []
for i, result in enumerate(results):
    text_lower = result[1].lower()
    if any(label in text_lower for label in total_labels):
        # Check this chunk and the two that follow it
        for j in range(i, min(i + 3, len(results))):
            prices = re.findall(r'\d+\.\d{2}', results[j][1])
            if prices:
                labeled_prices.append(float(prices[-1]))
                break  # only take one price per label hit

# Use the last labeled price (grand total is last on receipt); fall back to max of all
total = labeled_prices[-1] if labeled_prices else (max(all_prices) if all_prices else 0.00)

# Print the receipt info
print([store_name, date_found, total])

if store_name == "nil":
    print("Receipt rejected: no recognized store name found.")
else:
    #Saving to a file
    line_to_save = store_name + ", " + date_found + ", " + str(total) + "\n" # Format: Store, Date, Total (one receipt per line)
    with open('receipt_data.txt', 'a') as file:
        file.write(line_to_save)