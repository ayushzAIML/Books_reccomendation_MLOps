import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

books = pd.read_csv("/home/ayushz/Projects/Books_recommendation_END_TO_END/data/raw/cleaned_books.csv", low_memory=False)

books = books.rename(columns={
    "Book-Title": "Title",
    "Book-Author": "Author",
    "Year-Of-Publication": "Year"
})

cache = {}

def fetch_from_google(isbn):
    if isbn in cache:
        return cache[isbn]

    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        res = requests.get(url).json()
        items = res.get("items")
        if not items:
            cache[isbn] = (None, None)
            return cache[isbn]

        info = items[0]["volumeInfo"]
        genre = info.get("categories", [None])[0]
        description = info.get("description", None)

        cache[isbn] = (genre, description)
        return cache[isbn]

    except:
        cache[isbn] = (None, None)
        return cache[isbn]

# Run in parallel
with ThreadPoolExecutor(max_workers=24) as executor:
    results = list(tqdm(executor.map(fetch_from_google, books["ISBN"]), total=len(books)))

books["Genre"], books["Description"] = zip(*results)

books.to_csv("books_final.csv", index=False)
