import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# Base URL of the website
base_url = "http://books.toscrape.com/"
page = requests.get(base_url)
soup = BeautifulSoup(page.content, 'html.parser')

# List to store the data
data = []

# Find the categories
categories = soup.find('ul', class_='nav nav-list').find_all('li')[1:]

for category in categories:
    a_tag = category.find('a') 
    category_name = a_tag.get_text(strip=True) 
    category_link = a_tag['href']
    
    # Ensure the category link is relative to the base URL
    category_url = urljoin(base_url, category_link)
    
    # List to store books for the current category
    books = []

    while category_url:
        # Fetch the category page
        page = requests.get(category_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Find all the books in the category
        cat_page = soup.find('ol', class_='row')
        
        for book in cat_page.find_all('article', class_='product_pod'):
            title = book.find('h3').find('a')['title']
            rating = book.find('p', class_='star-rating')
            r = rating['class']
            price = book.find('p', class_='price_color').text.strip()
            availability = book.find('p', class_='instock availability').get_text(strip=True)
            
            # Create a book dictionary
            book_data = {
                "title": title,
                "rating": r[1],
                "price": price,
                "availability": availability
            }
            
            # Add the book data to the books list
            books.append(book_data)
        
        # Check if there is a "next" page link
        next_button = soup.find('li', class_='next')
        if next_button:
            next_link = next_button.find('a')['href']
            # Remove "index.html" if it exists in the next link
            next_link = next_link.replace('index.html', '')
            # Construct the full URL for the next page
            category_url = urljoin(category_url, next_link)
        else:
            category_url = None
    
    # Create a category object
    category_data = {
        "category": category_name,
        "books": books
    }
    
    # Add the category object to the data list
    data.append(category_data)

# Create the final object with categories
obj = {
    "categories": data
}

# Convert the data list to a JSON string and print it
json_data = json.dumps(obj, ensure_ascii=False, indent=4)
print(json_data)

# Write the JSON data to a file
with open('book_api.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

def count_books_with_rating(data, target_rating):
    """Count the number of books with a specific rating."""
    count = 0
    for category in data['categories']:
        for book in category['books']:
            if book['rating'] == target_rating:
                count += 1
    return count

# Specify the rating to count
target_rating = "Four"

# Get the count of books with the specified rating
count = count_books_with_rating(obj, target_rating)
print(f"Number of books with rating '{target_rating}': {count}")
