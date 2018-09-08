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
  pops = 'The three most popular articles of all time: \n\n'
  for row in articles:
      title = row[1]
      views = row[2]
      #coding=utf-8
      pops += u"\"%s\" - %s views \n" % (title, views)
      #pops += row[1] + str('-') + row[2] + "views \n"

  return pops

def getPopAuthors():
    """ Return  """


def exportResults():
    """Create a plain text file with all the results"""

    f = open('results.txt', 'w')
    f.write(getMostPop())
    f.close()
