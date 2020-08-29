from flask import Blueprint,render_template,g
from flask import current_app as app
from datetime import datetime
from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from flask import current_app as app
import redis
import random
from flask import jsonify

rds=redis.from_url("redis://rediscloud:YI2yzztWurvdkTUTm6FWa3G84XABtFkG@redis-14825.c232.us-east-1-2.ec2.cloud.redislabs.com:14825")
home_bp=Blueprint('home_bp',__name__,static_folder='static',template_folder='templates', static_url_path='/home/static')


def decode_redis(src):
    if isinstance(src, list):
        rv = list()
        for key in src:
            rv.append(decode_redis(key))
        return rv
    elif isinstance(src, dict):
        rv = dict()
        for key in src:
            rv[key.decode()] = decode_redis(src[key])
        return rv
    elif isinstance(src, bytes):
        return src.decode()
    else:
        raise Exception("type not handled: " +type(src))

def get_table_order(table):
    this_table={}
    top_level=decode_redis(rds.hgetall(table))
    for top_key in top_level:
        if not this_table.get(table):
            this_table[data[table]]={}
        this_table[data[table]][top_key]={}
        top_level_value=top_level[top_key]
        mid_level=decode_redis(rds.hgetall(top_level_value))
        for mid_key in mid_level:
            this_table[data[table]][top_key][mid_key]=mid_level[mid_key]
    return this_table

@home_bp.route('/<table>',methods=['GET','POST'])
def home(table):
    return render_template('index.html',table=table)


@socketio.on('get_cart')
def handle_get_cart(data):
    check=rds.exists(data['table'])
    this_table={}
    top_level=decode_redis(rds.hgetall(data['table']))
    for top_key in top_level:
        if not this_table.get(data['table']):
            this_table[data['table']]={}
        this_table[data['table']][top_key]={}
        top_level_value=top_level[top_key]
        mid_level=decode_redis(rds.hgetall(top_level_value))
        for mid_key in mid_level:
            this_table[data['table']][top_key][mid_key]=mid_level[mid_key]
    print('joined_cart'+str(data['table']))
    print(this_table)
    socketio.emit('broadcast_additem',this_table)


@socketio.on('additem')
def handle_addItem(data):
    print('addeditem'+data['table'])
    check=rds.exists(data['table'])
    rds.hset(data['table'],str(data['rawname']),'specstable'+str(data['rawname'])+str(data['table']))
    orderspecs= {
            "quantity":str(data['quantity']),
            "price":str(data['price']),
            "name":str(data['name']),
            "rawname":str(data['rawname']),
            "unitprice":str(data['unitprice'])
        }
    for i in orderspecs.keys():
        rds.hset('specstable'+str(data['rawname'])+str(data['table']),i,orderspecs[i])

    socketio.emit('broadcast_additem',data)

@socketio.on('socketedititem')
def handle_socketedititem(data):
    print('entered socketedititem')
    quant=int(data['quantity'])
    price=float(data['unitprice'])
    newprice=float(quant*price)
    if quant>0:
        rds.hset('specstable'+str(data['rawname'])+str(data['table']),'quantity',quant)
        rds.hset('specstable'+str(data['rawname'])+str(data['table']),'price',newprice)
    else:
        rds.hdel(data['table'],str(data['rawname']))
    socketio.emit('broadcast_edititem',data)
