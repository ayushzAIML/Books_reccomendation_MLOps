import pandas as pd

# Load datasets
books = pd.read_csv("books_final.csv")
ratings = pd.read_csv("BX-Book-Ratings.csv")

# Standardize ISBN column names if needed
books.rename(columns={'book_isbn':'ISBN'}, inplace=True)
ratings.rename(columns={'book_isbn':'ISBN'}, inplace=True)

# Merge based on common ISBN
merged_df = ratings.merge(books, on="ISBN", how="inner")

# Check result
print("Shape after merge:", merged_df.shape)
print(merged_df.head())

# Save merged dataset
merged_df.to_csv("merged_books_ratings.csv", index=False)
print("✅ Merged dataset saved as merged_books_ratings.csv")
