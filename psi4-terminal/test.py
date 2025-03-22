import os
print("Current working directory:", os.getcwd())
print("Templates folder exists:", os.path.isdir("templates"))
print("Index.html exists:", os.path.isfile("templates/index.html"))
