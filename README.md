# Logs Analysis project for Udacity
This command line Python program generates a plain text report that answers the following questions for a fictional news site:
+ What are the three most popular articles of all time based on view count?
+ Who are the most popular article authors of all time?
+ Which days had more than one percent of traffic return an error?

To find the answers, this Python program uses psycopg2 to query a PostgreSQL database. The mock database includes three tables:
+ Articles - a list of all the articles
  + author - integer
  + title - text
  + slug - text
  + lead - text
  + body - text
  + time - timestamp with time zone
  + id - integer
+ Authors - a list of all the Authors
  + name - text
  + bio - text
  + id - integer
+ Log - a list of all the times a page was accessed
  + path - text
  + ip - inet
  + method - text
  + status - text
  + time - timestamp with time zone
  + id - integer

## Requirements
#### VirtualBox
To run this program, you'll need a VirtualBox running Linux.
+ [Download it from virtualbox.org](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
+ Install the platform package for your operating system (you don't need the extension pack or the SDK)

#### Vagrant + configuration files
You'll also need to install Vagrant, which is the software that configures the Virtual Box and let's you use files that are on your computer and the Virtual Box.
+ [Download it from vagrantup.com](https://www.vagrantup.com/downloads.html)
+ Install the version for your operating system
+ [Download the VM configuration here](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip)
  + Unzip and cd into the directory (FSND-Virtual-Machine) using your terminal
  + cd into the *vagrant* directory

#### Start virtual machine
Once you've completed the steps above, you can start your virtual machine:
+ From the vagrant directory, use `vagrant up`
+ Once `vagrant up` finishes (it might take several minutes) run `vagrant ssh` to log in to your new Linux virtual machine.

#### Download and load the database
You can download the `newsdata.sql` database [here](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)
+ Unzip the file after download
+ Place the `newsdata.sql` file in the `vagrant` directory that is shared with your virtual machine
+ `cd` into the vagrant directory and run the following command to load the data: `psql -d news -f newsdata.sql`

#### Add the SQL views
This program relies on two SQL views. After you've created and loaded the database and the data, run these commands to add the SQL views:

```
psql news
```
Connect to the database

---

``` sql
create view article_views as
select count(*) as views, path from log
    where status = '200 OK'
        and path != '/'
    group by path
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


## Run it!
Navigate to wherever you unzipped the FSND-Virtual-Machine directory.
+ `cd` into the `vagrant` directory
+ Add `analyze_this.py` (I have added mine to a subdirectory called `logs-analysis`) and run the program...

```
python analyze_this.py
```

---
**The following is an explanation of how the program was designed.**

## Imports
``` import psycopg2 ```
Let's first import Psycopg so we can access our PostgreSQL database.

``` import os ```
Lastly, we'll import the OS class to be able to print the file path of the created file.


## getMostPop()
``` sql
select articles.title, views from articles,
  article_views as log
        where log.path = '/article/' || articles.slug
        limit 3;
```
My PostgreSQL query selects title from the **articles** table and selects the views from the **article_views** view that I created to aggregate the total views of each article.

``` python
pops = 'The three most popular articles of all time: \n'
for title, views in articles:
    pops += ('"{}" - {:,} views\n'.format(title, views))

pops += "\n\n"
```

Once we get the list from the query, we loop through it to create a readable list for our output.

## getPopAuthors()
``` sql
select authors.name, SUM(views) as total_views from articles,
      article_views as log,
      authors
          where log.path = '/article/' || articles.slug
          and articles.author = authors.id
          group by authors.name
          order by total_views desc;
```
The above query joins the articles and authors table along with the article_views view to select the author names and their total views for their articles. The output is grouped by author name and sorted from most views to least.

``` python
author_views = 'Most popular article authors of all time: \n'
for name, total_views in articles:
    author_views += ('"{}" - {:,} views\n'.format(name, total_views))

author_views += "\n\n"
```

Once we get the list from the query, we loop through it to create a readable list for our output.


# getPageErrors()
``` sql
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
```
The above query uses two subqueries and a view to accomplish its output.

The inner-most subquery creates a table with a column for total requests on any given day. Taking a step back, there's a subquery that finds the total number of errors for any given day as well as creates a column that finds what the percentage of errors for any given day is.

Finally, the query uses a `where` conditional to only show days with an error percentage over 1 percent.

``` python
error_list = 'Days with more than 1% of their requests as errors: \n'
  for day, percent in list:
      error_list += ('{} - {}% errors'.format(day, percent))
```

Once we get the list from the query, we loop through it to create a readable list for our output.

## exportResults()
This function creates a text file for our output and calls each previous function in order to write the results to the file.
