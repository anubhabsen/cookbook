# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

@auth.requires_membership('user_3')
def manage():
    grid = SQLFORM.smartgrid(db.recipe)
    return dict(grid=grid)
def index():
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def list():
    id=int(request.vars.id)
    if id>0:
        back=id-1
    else:
        back=id
    #form=SQLFORM(db.recipe,fields=['category'])
    recipes = db().select(db.recipe.ALL, orderby=db.recipe.created_on, limitby=(id*10,id*10+10))
    return dict(recipes=recipes, k = id + 1, back = back)

@auth.requires_login()
def upload():
    form = SQLFORM(db.recipe).process()
    return dict(form=form)

def show():
    recipe = db.recipe(request.args(0)) or redirect(URL('index'))
    recipe_id = request.args(0,cast=int)
    rec = db.recipe(recipe_id) or redirect(URL('index'))
    likes = db(db.recipe_likes.recipe == recipe_id).count()
    if auth.user_id:
        liked = db((db.recipe_likes.recipe == recipe_id) & (db.recipe_likes.liked_by == auth.user_id)).select()
        liked = True if len(liked) == 1 else False
    else:
        liked = False
    return locals()

@auth.requires_login()
def myrecipe():
    if len(request.args): page=int(request.args[0])
    else: page=0
    items_per_page=10
    limitby=(page*items_per_page,(page+1)*items_per_page+1)
    recipe = db(db.recipe.user_id==auth.user_id).select(orderby=~db.recipe.created_on,limitby=limitby)
    return dict(recipe=recipe,page=page,items_per_page=items_per_page)

@auth.requires_login()
def usermanage():
    query=db.recipe.user_id==db.auth_user(auth.user_id).id
    ##query = db.image.id>9
    grid = SQLFORM.grid(query)
    grid = SQLFORM.grid(query,user_signature=True,paginate=10,csv=False,maxtextlength=100)
    return dict(grid=grid)




@auth.requires_login()
def like():
    recipe_id = request.args(0,cast=int)
    rec = db.recipe(recipe_id) or redirect(URL('index')) # Check recipe_id validity
    liked = db((db.recipe_likes.recipe == recipe_id) & (db.recipe_likes.liked_by == auth.user_id)).count()
    liked = True if liked == 1 else False
    if not liked:
        db.recipe_likes.insert(recipe=recipe_id, liked_by=auth.user_id)
    redirect(URL('show', args=request.args))
    return dict()

@auth.requires_login()
def unlike():
    recipe_id = request.args(0,cast=int)
    rec = db.recipe(recipe_id) or redirect(URL('index')) # Check recipe_id validity
    liked = db((db.recipe_likes.recipe == recipe_id) & (db.recipe_likes.liked_by == auth.user_id)).select().first()
    if liked:
        del db.recipe_likes[liked.id]
    redirect(URL('show', args=request.args))
    return dict()
