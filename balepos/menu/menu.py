from flask import Blueprint,render_template,request,session,redirect,url_for
from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from flask_socketio import emit, join_room, leave_room
from .. import socketio
import redis
from flask import jsonify

rds=redis.Redis()
db=SQLAlchemy(app)

menu_bp=Blueprint('menu_bp',__name__,static_folder='static',template_folder='templates', static_url_path='/menu/static')
#create datastore
class DataStore():
    firstp_last= None
    secondp_last=None
#page list
page_list=['menu_bp.balifood','menu_bp.lombokfood','menu_bp.sundafood','menu_bp.riceandnoodle','menu_bp.appetizers','menu_bp.desserts']

balids = DataStore()
lombokds = DataStore()
sundads=DataStore()
appetizerds=DataStore()
dessertds=DataStore()
Base=automap_base()
#mirror db
Base.prepare(db.engine,reflect=True)
Food=Base.classes.fooditem
Menu=Base.classes.menu
#set page limits

#move functon
def move(table,pagename):
    idx=page_list.index(pagename)
    nxt=page_list[idx+1]
    if(idx!=0):
        bck=page_list[idx-1]
    if 'nextbutton.x' in request.form:
        return redirect(url_for(nxt,table=table))
    elif 'backbutton.x' in request.form:
        return redirect(url_for(bck, table=table))

@menu_bp.route('/<table>/balifood',methods=['GET','POST'])
def balifood(table):
    pagename='menu_bp.balifood'

    if request.method =="GET":
        bali=db.session.query(Food).filter(Food.food_origin=="bali").order_by(Food.idfood.asc()).limit(6)
        return render_template('menu.html',results=bali,current_page='/' + str(table) + '/balifood', page=pagename, cnt = 6,table=table)
    elif request.method== "POST":
        return move(table,pagename)




@menu_bp.route('/<table>/lombokfood',methods=['GET','POST'])
def lombokfood(table):
    pagename='menu_bp.lombokfood'
    if request.method =="GET":
        lombok=db.session.query(Food).filter(Food.food_origin=="lombok").order_by(Food.idfood.asc())
        return render_template('menu.html',results=lombok,current_page='/' + str(table) + '/lombokfood', page=pagename,cnt=11,table=table)
    elif request.method== "POST":
        return move(table,pagename)





@menu_bp.route('/<table>/sundafood',methods=['GET','POST'])
def sundafood(table):
    pagename='menu_bp.sundafood'
    if request.method =="GET":
        sunda=db.session.query(Food).filter(Food.food_origin=="sunda").order_by(Food.idfood.asc())
        return render_template('menu.html',results=sunda,current_page='/' + str(table) + '/sundafood', page=pagename,cnt=22,table=table)
    elif request.method== "POST":
        return move(table,pagename)


@menu_bp.route('/<table>/riceandnoodle',methods=['GET','POST'])
def riceandnoodle(table):
    pagename='menu_bp.riceandnoodle'
    if request.method =="GET":
        riceandnoodle=db.session.query(Food).filter(Food.food_origin=="riceandnoodle").order_by(Food.idfood.asc())
        return render_template('menu.html',results=riceandnoodle,current_page='/' + str(table) + '/riceandnoodle', page=pagename,cnt=6,table=table)
    elif request.method== "POST":
        return move(table,pagename)

@menu_bp.route('/<table>/appetizers',methods=['GET','POST'])
def appetizers(table):
    pagename='menu_bp.appetizers'
    if request.method =="GET":
        appetizer=db.session.query(Food).filter(Food.food_origin=="appetizer").order_by(Food.idfood.asc())
        return render_template('menu.html',results=appetizer,current_page='/' + str(table) + '/appetizers', page=pagename, cnt=6,table=table)
    elif request.method== "POST":
        return move(table,pagename)

@menu_bp.route('/<table>/desserts',methods=['GET','POST'])
def desserts(table):
    pagename='menu_bp.desserts'
    if request.method =="GET":
        dessert=db.session.query(Food).filter(Food.food_origin=="dessert").order_by(Food.idfood.asc())
        return render_template('menu.html',results=dessert,current_page='/' + str(table) + '/desserts', page=pagename,cnt=10,table=table)
    elif request.method== "POST":
        return move(table,pagename)



@menu_bp.route('/<table>/addCart',methods=['POST'])#problem is the redis server how to update and pull data easily# #SET NEW SESSION STRUCT#
def addCart(table):
    data=request.get_json(force = True)
    rawname=str(data['rawname'])
    producttitle=str(data['name'])
    quantity=int(data['quantity'])
    unitprice=float(data['unitprice'])
    totalprice=float(data['price'])
    orderlist={}
    markuprawname=str(data['table'])+str(rawname)
    session[markuprawname]=quantity
    theorderkey=str(data['table'])+'theOrder'
    if theorderkey in session:
        orderlist=session[theorderkey]
        if rawname in orderlist:
            print("available")
            if quantity<=0:
                print("pop")
                del orderlist[rawname]
                session[theorderkey]=orderlist
            else:
                orderlist[rawname]={"quantity":quantity,"price":totalprice,"name":producttitle,"rawname":rawname,"unitprice":unitprice}
                session[theorderkey]=orderlist
        else:
            print("unavailable")
            orderlist[rawname]={"quantity":quantity,"price":totalprice,"name":producttitle,"rawname":rawname,"unitprice":unitprice}
            session[theorderkey]=orderlist
        print(orderlist)
        sum=0
        for key, value in orderlist.items():
            if type(value) is dict:
                sum+=value["price"]
        session[str(data['table'])+'subtotal']=sum
        session[str(data['table'])+'grandtotal']=round(sum*1.15,2)
        session[str(data['table'])+'services']=round(sum*0.15,2)
    else:
        print("fresh dict")
        orderlist[rawname]={"quantity":quantity,"price":totalprice,"name":producttitle,"rawname":rawname,"unitprice":unitprice}
        session[theorderkey]=orderlist
        print(session[theorderkey])
        sum=0
        for key, value in orderlist.items():
            if type(value) is dict:
                sum+=value["price"]
        session[str(data['table'])+'subtotal']=sum
        session[str(data['table'])+'grandtotal']=round(sum*1.15,2)
        session[str(data['table'])+'services']=round(sum*0.15,2)
    return jsonify(status="success")

@menu_bp.route('/<table>/emitedititem',methods=['POST'])#problem is the redis server how to update and pull data easily# #SET NEW SESSION STRUCT#
def emitedititem(table):
    data=request.get_json(force = True)
    print(data)
    print('emitedititem')
    socketio.emit('socketedititem',data)
    return jsonify(status="success")


@menu_bp.route('/<table>/editCart',methods=['POST'])#problem is the redis server how to update and pull data easily# #SET NEW SESSION STRUCT#
def editCart(table):
    data=request.get_json(force = True)
    rawname=str(data['rawname'])
    producttitle=str(data['name'])
    quantity=int(data['quantity'])
    unitprice=float(data['unitprice'])
    totalprice=float(data['price'])
    orderlist={}
    markuprawname=str(data['table'])+str(rawname)
    session[markuprawname]=quantity
    theorderkey=str(data['table'])+'theOrder'
    if theorderkey in session:
        orderlist=session[theorderkey]
        if rawname in orderlist:
            print("available")
            if quantity<=0:
                print("pop")
                del orderlist[rawname]
                session[theorderkey]=orderlist
            else:
                orderlist[rawname]={"quantity":quantity,"price":totalprice,"name":producttitle,"rawname":rawname,"unitprice":unitprice}
                session[theorderkey]=orderlist
        else:
            print("unavailable")
            orderlist[rawname]={"quantity":quantity,"price":totalprice,"name":producttitle,"rawname":rawname,"unitprice":unitprice}
            session[theorderkey]=orderlist
        print(orderlist)
        sum=0
        for key, value in orderlist.items():
            if type(value) is dict:
                sum+=value["price"]
        session[str(data['table'])+'subtotal']=sum
        session[str(data['table'])+'grandtotal']=round(sum*1.15,2)
        session[str(data['table'])+'services']=round(sum*0.15,2)
    else:
        print("fresh dict")
        orderlist[rawname]={"quantity":quantity,"price":totalprice,"name":producttitle,"rawname":rawname,"unitprice":unitprice}
        session[theorderkey]=orderlist
        print(session[theorderkey])
        sum=0
        for key, value in orderlist.items():
            if type(value) is dict:
                sum+=value["price"]
        session[str(data['table'])+'subtotal']=sum
        session[str(data['table'])+'grandtotal']=round(sum*1.15,2)
        session[str(data['table'])+'services']=round(sum*0.15,2)
    return jsonify(status="success")

@menu_bp.context_processor
def my_utility_processor():

    def title(itemrawname):
        word=itemrawname.title();
        return word

    def replace(itemrawname,a,b):
        word=itemrawname.replace(a,b)
        return word

    def conc(a,b):
        word=f'{a}{b}'
        return word
    def countkeys(a):
        count=len(a)
        return count
    return dict(title=title, replace=replace, conc=conc, countkeys=countkeys)
