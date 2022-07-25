from flask import Flask, request, json, Response, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="mysql://admin:adminadmin@market2.ck3bn4bomvmi.us-east-1.rds.amazonaws.com:3306/basicmarketdb" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db = SQLAlchemy(app)

# Base = automap_base()
# Base.prepare(db.engine, reflect = True)
# Shop = Base.classes.shop
# Category = Base.classes.category
# Products = Base.classes.products


class Shop(db.Model):
    __tablename__ = 'shop'
    __table_args__ = {
        'autoload': True,
        #'schema': 'shop',
        'autoload_with': db.engine
    }

class Category(db.Model):
    __tablename__ = 'category'
    __table_args__ = {
        'autoload': True,
        #'schema': 'category',
        'autoload_with': db.engine
    }

class Products(db.Model):
    __tablename__ = 'products'
    __table_args__ = {
        'autoload': True,
        #'schema': 'products',
        'autoload_with': db.engine
    } 

class Listitems(db.Model):
    __tablename__ = 'list_items'
    __table_args__ = {
        'autoload': True,
        #'schema': 'products',
        'autoload_with': db.engine
    }

    
@app.route('/',methods=['GET'])
def home():
    # result_count = db.session.query(Products).count
    # return jsonify(result_count)
    message = "Bienvenido a la api productos de basic Market"
    return jsonify(message)
    # result = Products.query.count()
    # return jsonify(result)
    

@app.route('/getProducts', methods=['GET'])
def get_products():
    results = db.session.query(Products,Listitems).join(Listitems, Products.id == Listitems.id_product).all()
    data_dicccionary = {}
    lista = []
    for i,l in results:
        lista.append({'id':i.id,'name':i.name,'code':i.code, 'status':i.status,'url_image':i.url_image,'id_category':i.id_category,'shop_id':i.shop_id,'price':l.price})

    if(lista):

        data_dicccionary['items']=lista

    return data_dicccionary

@app.route('/productsFilterByNameList', methods=['POST'])
def filter_products_by_name_list():
    parameter = request.get_json()
    if parameter.get('name'):
        search = '%{}%'.format(parameter['name'])
        data_dicccionary = {}
        lista = []
        result = db.session.query(Products,Shop,Listitems).join(Shop, Products.shop_id == Shop.id).join(Listitems, Products.id == Listitems.id_product).filter(Products.name.like(search)).all()
        print(result)
        for i in result:
            print(i)
            lista.append({'id':i.Products.id,'name':i.Products.name,'code':i.Products.code, 'status':i.Products.status,'url_image':i.Products.url_image,'id_category':i.Products.id_category,'shop_id':i.Products.shop_id,'shop_name':i.Shop.name,'shop_img':i.Shop.img,'price':i.Listitems.price})

        if result:

            data_dicccionary['product'] = lista
        return data_dicccionary
    else:
        return make_response(jsonify("debes mandar un id"),400)


@app.route('/productFilterByNameOne', methods=['POST'])
def filter_product_by_name():
    parameter = request.get_json()
    if parameter.get('name'):
        name = parameter['name']
        search = '%{}%'.format(name)
        data_dicccionary = {}
        lista = []
        product =  db.session.query(Products,Shop,Listitems).join(Shop, Shop.id == Products.id).join(Listitems, Products.id == Listitems.id_product).filter(Products.name.like(search)).first()
        print(product.Listitems.price)
        if(product):
            
            lista.append({'id':product.Products.id,'name':product.Products.name,'code':product.Products.code, 'status':product.Products.status,'url_image':product.Products.url_image,'id_category':product.Products.id_category,'shop_id':product.Products.shop_id,'shop_name':product.Shop.name,'shop_img':product.Shop.img,'price':product.Listitems.price})
            data_dicccionary['product'] = lista

        
        return data_dicccionary
    else:
        return make_response(jsonify("debes mandar un id"),400)

@app.route('/insertProduct', methods=['POST'])
def inser_product():
    paramaters = request.get_json()
    name = paramaters['name']   
    code = paramaters['code']
    status = paramaters['status']
    url_image = paramaters['url_image']
    id_category = paramaters['id_category']
    shop_id = paramaters['shop_id']

    product = Products(
        name = f'{name}', 
        code = f'{code}', 
        status = status,
        url_image = f'{url_image}',
        id_category = id_category,
        shop_id = shop_id
    )
    db.session.add(product)
    db.session.commit()
    listProducts = Products.query.all()
    data_dicccionary = {}
    lista = []
    for i in listProducts:
        lista.append({'id':i.id,'name':i.name,'code':i.code, 'status':i.status,'url_image':i.url_image,'id_category':i.id_category,'shop_id':i.shop_id})

    if(lista):
        data_dicccionary['product']=lista

    return data_dicccionary


@app.route('/updateProduct', methods=['PUT'])
def updateProduct():
    paramaters = request.get_json()
    if(paramaters.get('id')):
        id = paramaters['id']
        product = Products.query.filter_by(id = (id)).first()
        if(product):
            if(paramaters.get('name')):
                product.name = paramaters['name']

            if(paramaters.get('code')):
                product.code = paramaters['code']

            if(paramaters.get('status')):
                product.status = int(paramaters['status'])

            if(paramaters.get('url_image')):
                product.url_image = paramaters['url_image']
            

            if(paramaters.get('id_category')):
                product.id_category = long(paramaters['id_category'])

            if(paramaters.get('shop_id')):
                product.shop_id = long(paramaters['shop_id'])
            
            db.session.commit()
            data_dicccionary = {}
            lista = []
            lista.append({'id':product.id,'name':product.name,'code':product.code, 'status':product.status,'url_image':product.url_image,'id_category':product.id_category,'shop_id':product.shop_id})
            data_dicccionary['product']= lista
            
            return data_dicccionary
        else:
            return jsonify("No existe producto")
    else:
        return jsonify("debes mandar el id")

@app.route('/deleteProduct', methods=['DELETE'])
def delete_product():
    parameters = request.get_json()
    if(parameters.get('id')):
        id = parameters['id']
        product = Products.query.filter_by(id = (id)).first()
        if(product):
            db.session.delete(product)
            db.session.commit()
            data_dicccionary = {}
            lista = []
            list_products = Products.query.all()
            for i in list_products:
                lista.append({'id':i.id,'name':i.name,'code':i.code, 'status':i.status,'url_image':i.url_image,'id_category':i.id_category,'shop_id':i.shop_id})

            data_dicccionary['product']=lista

            return data_dicccionary
        else:
            return jsonify("no se encontró el producto")
    else:
        return jsonify("Debes mandar el id para borrar")

@app.route('/getAllCategories', methods = ['GET'])
def get_all_categories():
    data_dicccionary = {}
    lista = []
    list_categories = Category.query.all()
    for i in list_categories:
        lista.append({'id':i.id, 'name':i.name,'description':i.description})
    
    data_dicccionary['categories']=lista
    return data_dicccionary

@app.route('/insertCategory', methods = ['POST'])
def insert_category():
    paramaters = request.get_json()

    name = paramaters['name']
    description = paramaters['description']
    if(description):
        description = paramaters['description']
        category = Category(
            name = f'{name}',
            description = f'{description}'
        )
        db.session.add(category)
        db.session.commit()
        data_dicccionary = {}
        lista = []
        list_categories = Category.query.all()
        for i in list_categories:
            lista.append({'id':i.id, 'name':i.name,'description':i.description})
        
        data_dicccionary['Categories']=lista
        return data_dicccionary
    
    category = Category(
        name = f'name'
    )
    db.session.add(category)
    db.session.commit()
    data_dicccionary = {}
    lista = []
    list_categories = Category.query.all()
    for i in list_categories:
        lista.append({'id':i.id, 'name':i.name, 'description':i.description})
    data_dicccionary['shops']=lista
    return data_dicccionary

@app.route('/updateCategory', methods=['PUT'])
def update_category():
    parameters = request.get_json()
    
    if(parameters.get('id')):
        id = parameters['id']
        category = Category.query.filter_by(id = (id)).first()
        if (category):
            if(parameters.get('name')):
                name = parameters['name']
                category.name = f'{name}'
            if(parameters.get('description')):
                description = parameters['description']
                category.description = f'{description}'
            db.session.commit()
            data_dicccionary = {}
            lista = []
            list_categories = Category.query.all()
            for i in list_categories:
                lista.append({'id':i.id, 'name':i.name,'description':i.description})
            
            data_dicccionary['categories']=lista
            return data_dicccionary
        else:
            return jsonify("no se encontró categoria")
    else:
        return jsonify("debes mandar el id")


@app.route('/deleteCategory', methods = ['DELETE'])
def delete_category():
    parameters = request.get_json()
    if(parameters.get('id')):
        id = parameters['id']
        category = Category.query.filter_by(id = (id)).first()
        if (category):
            db.session.delete(category)
            db.session.commit()
            data_dicccionary = {}
            lista = []
            list_category = Category.query.all()
            for i in list_category:
                lista.append({'id':i.id, 'name':i.name, 'description':i.description})
            
            data_dicccionary['categories']=lista
            return data_dicccionary
        else:
            return jsonify("no se encontró categoria")

    else:
        return jsonify("manda un id")

@app.route('/getAllShops', methods = ['GET'])
def get_all_shops():
    list_shops = Shop.query.all()
    data_dicccionary = {}
    lista = []
    for i in list_shops:
        #print(i)
        lista.append({'id':i.id,'name':i.name, 'img':i.img, 'id_list_items':i.id_list_items})
        #print('aqui',keyy_value)

    data_dicccionary['shops'] = lista    
    return data_dicccionary

@app.route('/insertShop', methods=['POST'])
def insert_shop():
    parameter = request.get_json()
    name = parameter['name']
    img = parameter['img']
    id_list_items = parameter['id_list_items']
    if(name and img and id_list_items):
        shop = Shop(
            name = f'{name}',
            img = f'{img}',
            id_list_items = id_list_items
        )
        db.session.add(shop)
        db.session.commit()
        list_shops = Shop.query.all()
        data_dicccionary = {}
        lista = []
        for i in list_shops:
            lista.append({'id':i.id,'name':i.name, 'img':i.img, 'id_list_items':i.id_list_items})
            
        data_dicccionary['shops'] = lista    

        return data_dicccionary
    else:
        jsonify("faltan parametros para la inserción")

@app.route('/updateShop', methods=['PUT'])
def update_shop():
    parameter = request.get_json()
    id = parameter['id']
    shop = ''
    if(id):
        shop = Shop.query.filter_by(id = (id)).first()
        if(shop):
            if(parameter.get('name')):
                name = parameter['name']
                shop.name = f'{name}'

            if(parameter.get('img')):
                img = parameter['img']
                shop.img = f'{img}'

            if(parameter.get('id_lis_items')):
                id_list_items = parameter['id_list_items']
                shop.id_list_items = id_list_items
            
            db.session.commit()
            data_dicccionary = {}
            lista = []
            #for i in shop:
            lista.append({'id':shop.id,'name':shop.name, 'img':shop.img, 'id_list_items':shop.id_list_items})
            data_dicccionary['shop'] = lista
            return data_dicccionary
    else:
        return jsonify("Debe mandar el id")

@app.route('/deleteShop', methods=['DELETE'])
def delete_shop():
    paramater = request.get_json()
    id = paramater['id']
    if(id):
        shop = Shop.query.filter_by(id = (id)).first()
        db.session.delete(shop)
        db.session.commit()
        data_dicccionary = {}
        lista = []
        list_shops = Shop.query.all()
        for i in list_shops:
            lista.append({'id':i.id,'name':i.name, 'img':i.img, 'id_list_items':i.id_list_items})
        data_dicccionary['shops']=lista    
        return data_dicccionary
    else:
        return jsonify("debe mandar el id")


@app.route('/getListItems', methods=['GET'])
def get_list_items():
    items = Listitems.query.all()
    data_dicccionary = {}
    lista = []
    for i in items:
        
        lista.append({'id':i.id,'id_product':i.id_product,'price':i.price,'link':i.link,'shop_id':i.shop_id})

    if(lista):
        data_dicccionary['users'] = lista
    
    return data_dicccionary

@app.route('/insertListItem', methods=['POST'])
def insert_list_item():
    paramaters = request.get_json()
    id_product = paramaters['id_product']
    price = paramaters['price']
    link = paramaters['link']
    shop_id = paramaters['shop_id']
    if(id_product and price and link):
        item = Listitems(
            id_product = id_product,
            price = price,
            link = f'{link}',
            shop_id = shop_id
        )
        db.session.add(item)
        db.session.commit()
        data_dicccionary = {}
        lista = []
        if item:
            lista.append({'id':item.id,'id_product':item.id_product,'price':item.price,'link':item.link,'shop_id':item.shop_id})
            data_dicccionary['listItems']=lista
        
        return data_dicccionary
    else:
        return jsonify("falta un parametro")

@app.route('/updateList', methods =['PUT'])
def update_list():
    parameters = request.get_json()
    if(parameters.get('id')):
        id = parameters['id']
        item = Listitems.query.filter_by(id = (id)).first()
        if item:
            if parameters.get('id_product'):
                id_product = parameters['id_product']
                item.id_product = id_product
            
            if parameters.get('price'):
                price = parameters['price']
                item.price = price

            if parameters.get('link'):
                link = parameters['link']
                item.link = link

            if parameters.get('shop_id'):
                shop_id = parameters['shop_id']
                item.shop_id = shop_id

            db.session.commit()
            data_dicccionary = {}
            lista = []
            if item:
                lista.append({'id':item.id,'id_product':item.id_product,'price':item.price,'link':item.link,'shop_id':item.shop_id})
                data_dicccionary['listItems']=lista

            return data_dicccionary
        else:
            return jsonify("item no encontrado")
    else:
        return jsonify("debes mandar el id")

@app.route('/deleteList', methods=['DELETE'])
def delete_items():
    parameter = request.get_json()
    if parameter.get('id'):
        id = parameter['id']
        item = Listitems.query.filter_by(id = (id)).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return get_list_items()
        else:
            return jsonify("item no encontrado")
    else:
        jsonify("debes mandar el id")

@app.route('/filterPriceByshop', methods=['POST'])
def filter_price_by_shop():
    parameter = request.get_json()
    if parameter.get('id_product'):
        id = parameter['id_product']
        # results = Products.query.join(Listitems, Products.id == Listitems.id_product). \
        # add_columns(Products.id,Products.code,Products.name,Products.url_image,Listitems.price). \
        # join(Shop, Shop.id_list_items == Listitems.id). \
        # add_columns(Shop.name,Shop.img). \
        # filter(Products.id == id).all()
        # results = db.session.query(Products,Shop,Listitems).join(Listitems, Products.id == Listitems.id_product). \
        # add_columns(Products.id,Products.code,Products.name,Products.url_image,Listitems.price). \
        # join(Shop,Shop.id_list_items == Listitems.id). \
        # add_columns(Shop.name,Shop.img). \
        # filter(Products.id == id).all()
        results = db.session.query(Products,Listitems).join(Listitems, Products.id == Listitems.id_product). \
        filter(Products.id == id).order_by(Listitems.price.desc())
        data_dicccionary = {}
        lista = []
        print(results)
        # for product,listitem in results:
        #     print(product.name, listitem.id)

        if results:
            for product, listitem in results:
                shop = Shop.query.filter_by(id_list_items = (listitem.id_list)).all()
                for s in shop:

                    lista.append({'id_product':product.id,'code':product.code,'product_name':product.name,'url_image':product.url_image,'price':listitem.price,'id_list_item':listitem.id,'id_list':listitem.id_list,'shop_name':s.name,'shop_img':s.img})
        
        if lista:
            data_dicccionary['products_by_shop']=lista

        return data_dicccionary
        
    else:
        return jsonify("Debes mandar un id de producto")

@app.route('/filterPriceProduct', methods=['POST'])
def filter_price_product():
    parameter = request.get_json()
    if parameter.get('id'):
        id = parameter['id']
        result = db.session.query(Products,Listitems).join(Listitems, Products.id == Listitems.id_product). \
        filter(Listitems.id == id).order_by(Listitems.price.desc())        
        data_dicccionary = {}
        lista = []
        print(result)
        if result:
            for product, listitem in result:
                shop = Shop.query.filter_by(id_list_items = (listitem.id_list)).first()
                lista.append({'id_product':product.id,'code':product.code,'product_name':product.name,'url_image':product.url_image,'List_item_id':listitem.id,'price':listitem.price,'shop_id':shop.id,'shop_name':shop.name,'shop_img':shop.img})

        if lista:
            data_dicccionary['Product Filter']= lista
            
        return data_dicccionary


    else:
        jsonify("debes mandar el id")

@app.route('/filterPriceProductObjects', methods=['POST'])
def filter_price_product_objects():
    parameter = request.get_json()
    if parameter.get('id'):
        id = parameter['id']
        result = db.session.query(Products,Listitems).join(Listitems, Products.id == Listitems.id_product). \
        filter(Products.id == id).order_by(Listitems.price.desc())        
        data_dicccionary = {}
        lista = []
        print(result)
        if result:
            for product, listitem in result:
                shop = Shop.query.filter_by(id_list_items = (listitem.id_list)).first()
                lista.append({'id_product':product.id,'code':product.code,'product_name':product.name,'url_image':product.url_image,'List_item_id':listitem.id,'price':listitem.price,'shop_id':shop.id,'shop_name':shop.name,'shop_img':shop.img})

        if lista:
            data_dicccionary['Product Filter']= lista
            
        return data_dicccionary


    else:
        jsonify("debes mandar el id")
    
if __name__ == '__main__':
    
    app.run(debug=True, port=5000, host='0.0.0.0')



        


    