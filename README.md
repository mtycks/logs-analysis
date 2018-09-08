# logs-analysis
Logs Analysis project for Udacity

View for third
"""
create view log_errors as
  select date_trunc('day', time) as day, count(*) as total_errors
      from log
      where status != '200 OK'
      group by day;

"""
