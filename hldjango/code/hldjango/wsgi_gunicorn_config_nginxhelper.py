# gunicorn configuration file, referred to explicitly when launching gunicorn from shell
# see https://docs.gunicorn.org/en/stable/configure.html#configuration-file
# see https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py
# see https://azureossd.github.io/2023/01/27/Configuring-Gunicorn-worker-classes-and-other-general-settings/

import multiprocessing


# see nginx_config.conf and run_mainservices.sh for use of this file


# this 0.0.0.0 is needed to expose 127.0.0.1 from docker
bind = "0.0.0.0:8000"
#bind = "0.0.0.0:80"



# normal suggested setting?
#workers = multiprocessing.cpu_count() * 2 + 1


# see https://pythonspeed.com/articles/gunicorn-in-docker/
workers = 2
threads = 4
worker_class = "gthread"



# log to stdout/stderr
accesslog = "-"
errorlog = "-"
#loglevel = "debug"
