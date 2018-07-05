# flask restfull api example
## an of web service made with 
- flask
- flask_restful
- flask_script
- flask_migrate
- marshmallow
- flask_sqlalchemy 
- flask_marshmallow 
- marshmallow-sqlalchemy 
this is ready to use (test) just
1) clone or dowload this reposotery (folder) in your computer for example in folder named 
  ** flask_restfull_exampe **
2) cd  ** flask_restfull_exampe **
3) open a terminal in this directory ** flask_restfull_exampe **
4)copy past and click enter for each of this command  execute this commands :
   source env/bin/activate
   source env/bin/activate
   pip install --upgrade pip  # must be connected for this
   pip install -r requirements.txt  # must be connected for this
   python migrate.py db init
   python migrate.py db migrate
   python migrate.py db upgrade
   python run.py
then enjoy by testing this links
http://127.0.0.1:5000/api/Hello
http://127.0.0.1:5000/api/Category
for mor details see this tuto https://www.codementor.io/dongido/how-to-build-restful-apis-with-python-and-flask-fh5x7zjrx
