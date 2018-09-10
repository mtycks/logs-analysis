# logs-analysis
# Logs Analysis project for Udacity

## Imports
``` import psycopg2 ```
Let's first import Psycopg so we can access our PostgreSQL database.

``` from datetime import datetime ```
Then we need to import the datetime module from the datetime class to be able to format dates in our output.

``` import os ```
Lastly, we'll import the OS class to be able to print the file path of the created file.

## SQL views created
``` sql
create view article_views as
select count(*) as views, replace(path, '/article/', '') as slug from log
    where status = '200 OK'
        and path != '/'
    group by slug
    order by views desc;
```

The above view creates a table that totals each article's views in a column and also creates a column for each article's slug.

---

``` sql
create view log_errors as
  select to_char(time, 'FMMonth DD, YYYY') as day, count(*) as total_errors
      from log
      where status != '200 OK'
      group by day;
```

The above view creates a column for each day regardless of time and totals all the errors for one day into another column.


## getMostPop()
``` sql
select articles.id, articles.title, views from articles,
  article_views as log
        where log.slug = articles.slug
        limit 3;
```
My PostgreSQL query selects the ID and title from the **articles** table and selects the views from the **article_views** view that I created to aggregate the total views of each article.

``` python
pops = 'The three most popular articles of all time: \n'
    for row in articles:
        title = row[1]
        views = "{:,}".format(row[2])
        pops += u"\"%s\" - %s views \n" % (title, views)

    pops += "\n\n"
```

Once we get the list from the query, we loop through it to create a readable list for our output.

## getPopAuthors()
``` sql
select authors.name, SUM(views) as total_views from articles,
      article_views as log,
      authors
          where log.slug = articles.slug
          and articles.author = authors.id
          group by authors.name
          order by total_views desc;
```
The above query joins the articles and authors table along with the article_views view to select the author names and their total views for their articles. The output is grouped by author name and sorted from most views to least.

``` python
author_views = 'Most popular article authors of all time: \n'
    for row in articles:
        name = row[0]
        views = "{:,}".format(row[1])
        author_views += u"%s - %s views \n" % (name, views)

    author_views += "\n\n"
```

Once we get the list from the query, we loop through it to create a readable list for our output.


# getPageErrors()
``` sql
select day, percentages.percent from
  (select log_errors.day,
      log_errors.total_errors,
      totals.total_requests,
      round((
          log_errors.total_errors * 100.0) /
              totals.total_requests, 1)
              as percent
      from log_errors,
          (select date_trunc('day', time) as day,
              count(*) as total_requests
              from log
              group by day) as totals
      where totals.day = log_errors.day) as percentages
  where percent > 1;
```
The above query uses two subqueries and a view to accomplish its output.

The inner-most subquery creates a table with a column for total requests on any given day. Taking a step back, there's a subquery that finds the total number of errors for any given day as well as creates a column that finds what the percentage of errors for any given day is.

Finally, the query uses a `where` conditional to only show days with an error percentage over 1 percent.

``` python
error_list = 'Days with more than 1% of their requests as errors: \n'
    for row in list:
        day = row[0].strftime("%B %d, %Y")
        percentage = row[1]
        error_list += u"%s - %s%% errors " % (day, percentage)
```

Once we get the list from the query, we loop through it to create a readable list for our output.

## exportResults()
This function creates a text file for our output and calls each previous function in order to write the results to the file.
