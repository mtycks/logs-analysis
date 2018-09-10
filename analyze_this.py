#!/usr/bin/env python2.7
# Command line program to analyze newspaper visitor logs

import psycopg2
from datetime import datetime
import os

DBNAME = "news"


def main():
    exportResults()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("File exported: %s/results.txt" % dir_path)


def getMostPop():
    """Return the three most popular articles of all time"""

    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute(""" select articles.title, views from articles,
    article_views as log
          where log.slug = articles.slug
          limit 3; """)
    articles = c.fetchall()
    db.close()

    # loop through the results and print them row-by-row
    pops = 'The three most popular articles of all time: \n'
    for title, views in articles:
        pops += ('"{}" - {:,} views\n'.format(title, views))

    pops += "\n\n"

    return pops


def getPopAuthors():
    """ Return a list of authors sorted by views """

    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("""
    select authors.name, SUM(views) as total_views from articles,
        article_views as log,
        authors
            where log.slug = articles.slug
            and articles.author = authors.id
            group by authors.name
            order by total_views desc;
    """)
    articles = c.fetchall()
    db.close()

    # loop through the results and print them row-by-row
    author_views = 'Most popular article authors of all time: \n'
    for row in articles:
        name = row[0]
        views = "{:,}".format(row[1])
        author_views += u"%s - %s views \n" % (name, views)

    author_views += "\n\n"

    return author_views


def getPageErrors():
    """ Return a list of dates that had more than 1% of request errors """

    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("""
        select day, percentages.percent from
            (select log_errors.day,
                round((
                    log_errors.total_errors * 100.0) /
                        totals.total_requests, 1)
                        as percent
                from log_errors,
                    (select to_char(time, 'FMMonth DD, YYYY') as day,
                        count(*) as total_requests
                        from log
                        group by day) as totals
                where totals.day = log_errors.day) as percentages
            where percent > 1;
    """)
    list = c.fetchall()
    db.close()

    # loop through the results and print them row-by-row
    error_list = 'Days with more than 1% of their requests as errors: \n'
    for row in list:
        day = row[0]
        percentage = row[1]
        error_list += u"%s - %s%% errors " % (day, percentage)

    return error_list


def exportResults():
    """Create a plain text file with all the results"""

    f = open('results.txt', 'w')
    f.write(getMostPop())
    f.write(getPopAuthors())
    f.write(getPageErrors())
    f.close()


if __name__ == "__main__":
    main()
