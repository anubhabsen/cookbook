# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.auth_user.password.requires = IS_STRONG(min=8, upper=1)

db.define_table('recipe', Field('user_id', 'reference auth_user',default=auth.user_id),
Field('title'), Field('image', 'upload'), Field('image2', 'upload'), Field('image3', 'upload'), Field('duration'), Field('ingredients', 'text'), Field('cuisine'), Field('classer'), Field('body', 'text'), auth.signature)
db.define_table('response', Field('rcp_id', 'reference recipe'), Field('responses', 'text'), auth.signature)
db.define_table('recipe_likes',
                  Field('recipe', 'reference recipe'),
                  Field('liked_by', 'reference auth_user', default=auth.user_id))
db.recipe.title.requires = IS_NOT_EMPTY()
db.recipe.image.requires = IS_NOT_EMPTY()
db.recipe.ingredients.requires = IS_NOT_EMPTY()
db.recipe.body.requires = IS_NOT_EMPTY()
db.response.responses.requires = IS_NOT_EMPTY()
db.recipe.user_id.writable = db.recipe.user_id.readable = False
db.recipe.cuisine.requires = IS_IN_SET(['Italian','Thai','Japanese','Arab','Spanish','German','Korean', 'African', 'Australian', 'Greek', 'Caribbean', 'Indian', 'Mexican', 'Brazilian', 'Chinese', 'American', 'Others'])
db.recipe.duration.requires = IS_IN_SET(['0-30 mins','30-60 mins','60-90 mins','90-180 mins','180-300 mins','more than 300 mins'])
db.recipe.classer.requires = IS_IN_SET(['Aperitivo- Meal opener','Antipasto- Heavier starter','Primo- First course','Secondo- Meats and fish','Contorno- Side Dish','Insalata- Salad','Formaggi e Frutta- Cheese and Seasonal Fruit', 'Dolce- Dessert', 'Caffe- Coffee', 'Digestivo- Meal concluder'])
