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

    query = """ select articles.title, views from articles,
    article_views as log
          where log.slug = articles.slug
          limit 3; """
    articles = execute_query(query)

    # loop through the results and print them row-by-row
    pops = 'The three most popular articles of all time: \n'
    for title, views in articles:
        pops += ('"{}" - {:,} views\n'.format(title, views))

    pops += "\n\n"

    return pops


def getPopAuthors():
    """ Return a list of authors sorted by views """

    query = """
    select authors.name, SUM(views) as total_views from articles,
        article_views as log,
        authors
            where log.slug = articles.slug
            and articles.author = authors.id
            group by authors.name
            order by total_views desc;
    """
    articles = execute_query(query)

    # loop through the results and print them row-by-row
    author_views = 'Most popular article authors of all time: \n'
    for name, total_views in articles:
        author_views += ('"{}" - {:,} views\n'.format(name, total_views))

    author_views += "\n\n"

    return author_views


def getPageErrors():
    """ Return a list of dates that had more than 1% of request errors """

    query = """
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
    """
    list = execute_query(query)

    # loop through the results and print them row-by-row
    error_list = 'Days with more than 1% of their requests as errors: \n'
    for day, percent in list:
        error_list += ('{} - {}% errors'.format(day, percent))

    return error_list


def execute_query(query):
    """
    execute_query takes an SQL query as a parameter,
    executes the query and returns the results as a list of tuples.

    args:
      query - (string) an SQL query statement to be executed.

    returns:
      A list of tuples containing the results of the query.
    """
    try:
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        c.execute(query)
        result = c.fetchall()
        db.close()
        return result

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def exportResults():
    """Create a plain text file with all the results"""

    f = open('results.txt', 'w')
    f.write(getMostPop())
    f.write(getPopAuthors())
    f.write(getPageErrors())
    f.close()


if __name__ == "__main__":
    main()
