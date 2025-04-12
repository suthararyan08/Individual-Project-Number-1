import csv
import os
import matplotlib.pyplot as plt
import requests

class Book:
    """Represents a book with basic attributes."""
    def __init__(self, title, author, genre, year):
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year

    def to_dict(self):
        """Convert book object to dictionary for CSV storage."""
        return {"Title": self.title, "Author": self.author, "Genre": self.genre, "Year": self.year}

    def __str__(self):
        return f"{self.title} by {self.author} ({self.genre}, {self.year})"

class FictionBook(Book):
    """Represents a fiction book, inheriting from Book."""
    def __init__(self, title, author, year, subgenre):
        super().__init__(title, author, "Fiction", year)
        self.subgenre = subgenre

class NonFictionBook(Book):
    """Represents a non-fiction book, inheriting from Book."""
    def __init__(self, title, author, year, field):
        super().__init__(title, author, "Non-Fiction", year)
        self.field = field

class Library:
    """Manages the book collection."""
    FILE_NAME = "library.csv"

    def __init__(self):
        self.books = []
        self.load_books()

    def load_books(self):
        """Loads books from CSV file."""
        if not os.path.exists(self.FILE_NAME):
            return
        with open(self.FILE_NAME, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.books.append(Book(row['Title'], row['Author'], row['Genre'], row['Year']))

    def save_books(self):
        """Saves books to CSV file."""
        with open(self.FILE_NAME, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Title", "Author", "Genre", "Year"])
            writer.writeheader()
            for book in self.books:
                writer.writerow(book.to_dict())

    def add_book(self, book):
        """Adds a new book to the library."""
        self.books.append(book)
        self.save_books()

    def search_books(self, keyword):
        """Search for books by title, author, or genre."""
        return [book for book in self.books if keyword.lower() in book.title.lower() or 
                keyword.lower() in book.author.lower() or keyword.lower() in book.genre.lower()]

    def update_book(self, title, new_title=None, new_author=None, new_genre=None, new_year=None):
        """Update book information."""
        for book in self.books:
            if book.title.lower() == title.lower():
                if new_title:
                    book.title = new_title
                if new_author:
                    book.author = new_author
                if new_genre:
                    book.genre = new_genre
                if new_year:
                    book.year = new_year
                self.save_books()
                return True
        return False

    def remove_book(self, title):
        """Remove a book from the collection."""
        initial_count = len(self.books)
        self.books = [book for book in self.books if book.title.lower() != title.lower()]
        self.save_books()
        return initial_count != len(self.books)  # Returns True if a book was removed, False otherwise


    def display_books(self, filter_by=None):
        """Display books, optionally filtering by genre, in a formatted table."""
        books_to_display = self.books if not filter_by else [book for book in self.books if book.genre.lower() == filter_by.lower()]
        if not books_to_display:
            print("No books found.")
            return
        print(f"{'Title':<30}{'Author':<25}{'Genre':<15}{'Year':<5}")
        print("-" * 75)
        for book in books_to_display:
            print(f"{book.title:<30}{book.author:<25}{book.genre:<15}{book.year:<5}")

    def visualize_books_by_genre(self):
        """Generates a bar chart showing the number of books per genre."""
        genre_count = {}
        for book in self.books:
            genre_count[book.genre] = genre_count.get(book.genre, 0) + 1

        plt.bar(genre_count.keys(), genre_count.values())
        plt.xlabel("Genre")
        plt.ylabel("Number of Books")
        plt.title("Books by Genre")
        plt.xticks(rotation=45)
        plt.show()

    def import_books_from_api(self, query):
        """Fetches books from Google Books API and adds them to the library."""
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("items", []):
                volume_info = item.get("volumeInfo", {})
                title = volume_info.get("title", "Unknown")
                author = ", ".join(volume_info.get("authors", ["Unknown"]))
                genre = volume_info.get("categories", ["General"])[0]
                year = volume_info.get("publishedDate", "Unknown").split("-")[0]
                self.add_book(Book(title, author, genre, year))
            print("Books imported successfully!")
        else:
            print("Failed to fetch books from API.")

# CLI Interface
def main():
    library = Library()
    while True:
        print("\nPersonal Library Management System")
        print("1. Add Book")
        print("2. Search Books")
        print("3. Update Book")
        print("4. Remove Book")
        print("5. Display Books")
        print("6. Visualize Books by Genre")
        print("7. Import Books from API")
        print("8. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Enter title: ")
            author = input("Enter author: ")
            genre = input("Enter genre: ")
            year = input("Enter year: ")
            library.add_book(Book(title, author, genre, year))
            print("Book added successfully!")
        elif choice == "2":
            keyword = input("Enter search keyword: ")
            results = library.search_books(keyword)
            print("\nSearch Results:")
            for book in results:
                print(book)
        elif choice == "3":
            title = input("Enter book title to update: ")
            new_title = input("Enter new title (leave blank to keep unchanged): ")
            new_author = input("Enter new author (leave blank to keep unchanged): ")
            new_genre = input("Enter new genre (leave blank to keep unchanged): ")
            new_year = input("Enter new year (leave blank to keep unchanged): ")
            success = library.update_book(title, new_title or None, new_author or None, new_genre or None, new_year or None)
            print("Book updated successfully!" if success else "Book not found.")
        elif choice == "4":
            title = input("Enter book title to remove: ")
            success = library.remove_book(title)
            print("Book removed successfully!" if success else "Book not found.")
        elif choice == "5":
            filter_by = input("Enter genre to filter by (leave blank for all books): ").strip()
            library.display_books(filter_by if filter_by else None)
        elif choice == "6":
            library.visualize_books_by_genre()
        elif choice == "7":
            query = input("Enter search term for API import: ")
            library.import_books_from_api(query)
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
