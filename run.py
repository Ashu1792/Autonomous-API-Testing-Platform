from app import create_app
<<<<<<< HEAD
from threading import Thread
from app.services.monitor import monitor_apis

app = create_app()

# 🔥 start monitoring
t = Thread(target=monitor_apis)
t.daemon = True
t.start()

=======

app = create_app()
print(app.url_map)
>>>>>>> d852476d5a88aa5d9738024e40a2fec6ec34e6f6
if __name__ == "__main__":
    app.run(debug=True)