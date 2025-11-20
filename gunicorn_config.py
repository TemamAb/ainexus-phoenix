bind = "0.0.0.0:{}".format(int(os.environ.get("PORT", 8080)))
workers = 4
worker_class = "eventlet"
timeout = 120
