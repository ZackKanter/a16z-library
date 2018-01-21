# quick and dirty python script to get the ratings of the books in the Marc Andreesen library via the
# Goodreads API, sort from highest to lowest and output a markdown file for viewing
from goodreads import client
import sys

# since we are reading only, no need to authenticate
# the script expects the api client key and the client secret as the first two arguments to the script
# you gets these from Goodreads (see https://www.goodreads.com/api for more details and to get your own)
gc = client.GoodreadsClient(sys.argv[1], sys.argv[2])

# parse the markdown document (table) into lines
lines = [line.strip() for line in open('books.md')]

# use the table column markdown to parse the header into a list and add fields for the average rating and rating counts
records = []
records.append(lines[0].split(' | '))
records[0].append("Average Rating")
records[0].append("Ratings Count")

# skip the second line from the markdown file as it is markdown for the table header
for line in lines[2:]:
    # within each line use the table column markdown to split into fields
    record = line.split(' | ')

    # set the default rating to '0.0' and the rating count to '0'
    average_rating = '0.0'
    ratings_count = '0'

    # we can only use the Goodreads API to get the ratings data if a link to the book in Goodreads exists
    if "[Goodreads]" in record[3]:
        # the Goodreads book id is essentially the part at the end of the link
        start = record[3].find('(https://www.goodreads.com/book/show/') + len('(https://www.goodreads.com/book/show/')
        end = record[3].find(')', start)
        found = record[3][start:end]

        # use the Goodreads API to get the rating data TODO: add error/exception handling!
        book = gc.book(found)
        average_rating = book.average_rating
        ratings_count = book.ratings_count

    # append the rating data to the end of each record
    record.append(average_rating)
    record.append(ratings_count)
    records.append(record)

# cheap way to skip the header and second record which is header markdown TODO: fix this by removing this record up front
recs = records[1:]

# sort by average rating: highest to lowest
recs.sort(key=lambda x: float(x[4]), reverse=True)

# write the output to a markdown file similar to the markdown file input into the script
with open("books_ratings.md", "w") as file:
    file.write(' | '.join(records[0]) + '\n')
    file.write(' | '.join(['---', '---', '---', '---', '---', '---']) + '\n')
    for record in recs:
        file.write(' | '.join(record) + '\n')






