#
#Command line program to analyze newspaper visitor logs
#

import psycopg2

DBNAME = "news"

def getMostPop():
  """Return the three most popular articles of all time"""

  db = psycopg2.connect(database=DBNAME)
  c = db.cursor()
  c.execute("select * from authors;")
  articles = c.fetchall()
  db.close()

  #loop through the results and print them row-by-row
  pops = ''
  for row in articles:
      pops += row[0] + "\n"

  return pops


def exportResults():
    """Create a plain text file with all the results"""

    f = open('results.txt', 'w')
    f.write(getMostPop())
    f.close()
