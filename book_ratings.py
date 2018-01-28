# quick and dirty python script to get the ratings of the books in the Marc Andreesen library via the
# Goodreads API, sort from highest to lowest and output a markdown file for viewing
from goodreads import client
from pandas import DataFrame
import sys

# some useful "constants"
GOODREADS_LINK_START = '(https://www.goodreads.com/book/show/'
GOODREADS_LINK_START_LENGTH = len('(https://www.goodreads.com/book/show/')
GOODREADS_LINK_END = ')'

def find_book_id(record):
    # the Goodreads book id is essentially the part at the end of the link
    start = record.find(GOODREADS_LINK_START) + GOODREADS_LINK_START_LENGTH
    end = record.find(GOODREADS_LINK_END, start)
    return record[start:end]

def get_book_attributes(goodreads_client, book_id):
    # use the Goodreads API to get attributes of the book
    book = goodreads_client.book(book_id)
    book_attributes = {}
    book_attributes["title"] = book.title
    book_attributes["average rating"] = book.average_rating
    book_attributes["ratings count"] = book.ratings_count
    book_attributes["number pages"] = book.num_pages
    # create a formatted string for the date tuple returned by the API client
    if book.publication_date is None:
        month, day, year = (1, 1, 1000)
    else:
        month, day, year = book.publication_date
    book_attributes["publication date"] = "{0}/{1}/{2}".format(month,day,year)
    book_attributes["publisher"] = book.publisher
    book_attributes["isbn"] = book.isbn
    return book_attributes

def create_new_headings(old_markdown_header):
    new_headings = old_markdown_header.split(' | ')
    new_headings.append("Book Title")
    new_headings.append("Average Rating")
    new_headings.append("Ratings Count")
    new_headings.append("Number Pages")
    new_headings.append("Publication Date")
    new_headings.append("Publisher")
    new_headings.append("ISBN")
    return new_headings

def write_markdown(file_name, headings, book_records):
    with open(file_name, "w") as file:
        file.write(' | '.join(headings) + '\n')
        file.write(' | '.join(['---'] * len(headings)) + '\n')
        for record in book_records:
            file.write(' | '.join(record) + '\n')

def write_data(file_name, headings, book_records):
    df = DataFrame(book_records)
    df.columns = headings
    df.to_csv(file_name + '.csv')

def main(argv):
    # since we are reading only, no need to authenticate
    # the script expects the api client key and the client secret as the first two arguments to the script
    # you gets these from Goodreads (see https://www.goodreads.com/api for more details and to get your own)
    gc = client.GoodreadsClient(argv[1], argv[2])

    # parse the markdown document (table) into lines
    lines = [line.strip() for line in open('books.md')]

    # create new headings starting with the old markdown file header
    headings = create_new_headings(lines[0])

    # create a list for the parsed and extended book records
    records = []

    idx = 1
    # skip the second line from the markdown file as it is markdown for the table header
    for line in lines[2:]:
        print(idx)
        idx = idx + 1
        # within each line use the table column markdown to split into fields
        record = line.split(' | ')

        # set some defaults for the book attributes in case they cannot be found
        # set the default rating to '0.0' and the rating count to '0'
        book_title = ''
        average_rating = '0.0'
        ratings_count = '0'
        number_pages = '0'
        publication_date = '1/1/1000'
        publisher = ''
        isbn = ''

        # we can only use the Goodreads API to get the ratings data if a link to the book in Goodreads exists
        if "[Goodreads]" in record[3]:
            book_id = find_book_id(record[3])
            attributes = get_book_attributes(gc, book_id)
            book_title = book_title if attributes["title"] is None else attributes["title"]
            average_rating = average_rating if attributes["average rating"] is None else attributes["average rating"]
            ratings_count = ratings_count if attributes["ratings count"] is None else attributes["ratings count"]
            number_pages = number_pages if attributes["number pages"] is None else attributes["number pages"]
            publication_date = publication_date if attributes["publication date"] is None else attributes["publication date"]
            publisher = publisher if attributes["publisher"] is None else attributes["publisher"]
            isbn = isbn if attributes["isbn"] is None else attributes["isbn"]

        record.append(book_title)
        record.append(average_rating)
        record.append(ratings_count)
        record.append(number_pages)
        record.append(publication_date)
        record.append(publisher)
        record.append(isbn)
        records.append(record)

    # sort by average rating: highest to lowest
    records.sort(key=lambda x: float(x[5]), reverse=True)

    # write the output
    write_markdown("books_ratings.md", headings, records)
    write_data("books_ratings", headings, records)

if __name__ == "__main__":
    main(sys.argv)