#
#Command line program to analyze newspaper visitor logs
#

import psycopg2

DBNAME = "news"

def getMostPop():
  """Return the three most popular articles of all time"""

  db = psycopg2.connect(database=DBNAME)
  c = db.cursor()
  c.execute(""" select articles.id, articles.title, views from articles,
    (select count(*) as views, replace(path, '/article/', '') as slug from log
      where status = '200 OK'
          and path != '/'
      group by slug
      order by views desc) as log
          where log.slug = articles.slug
          limit 3; """)
  articles = c.fetchall()
  db.close()

  #loop through the results and print them row-by-row
  pops = 'The three most popular articles of all time: \n'
  for row in articles:
      title = row[1]
      views = "{:,}".format(row[2])
      pops += u"\"%s\" - %s views \n" % (title, views)

  pops += "\n\n";

  return pops

def getPopAuthors():
    """ Return a list of authors sorted by views """

    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute(""" select authors.name, SUM(views) as total_views from articles,
      (select count(*) as views, replace(path, '/article/', '') as slug from log
        where status = '200 OK'
            and path != '/'
        group by slug
        order by views desc) as log,
        authors
            where log.slug = articles.slug
            and articles.author = authors.id
            group by authors.name
            order by total_views desc;
    """)
    articles = c.fetchall()
    db.close()

    #loop through the results and print them row-by-row
    author_views = 'Most popular article authors of all time: \n'
    for row in articles:
        name = row[0]
        views = "{:,}".format(row[1])
        #coding=utf-8
        author_views += u"%s - %s views \n" % (name, views)

    return author_views


def exportResults():
    """Create a plain text file with all the results"""

    f = open('results.txt', 'w')
    f.write(getMostPop())
    f.write(getPopAuthors())
    f.close()
