from operator import itemgetter
from marketplace import email_tools
import os
import re
from flask_login import login_user, logout_user
from werkzeug.utils import secure_filename
from marketplace.api_folder.schemas import order_schema, consumer_sign_up_schema, producer_sign_up_schema, \
    product_schema
from marketplace.models import Order, Consumer, Producer, Category, Product, Cart, User
from flask_restful import abort
from marketplace import db, app


# Abort methods

def failed_email_check(email):
    abort(406, message='Given email = \'{}\'  is invalid'.format(email))


def failed_password_len_check():
    abort(406, message='Given password is too short')


def failed_email_uniqueness_check(email):
    abort(406, message='User with given email = {} already exists'.format(email))


def failed_producer_name_uniqueness_check(name):
    abort(406, message='Producer with given name = {} already exists'.format(name))


def no_file_part_in_request():
    abort(406, message='No file part in request')


def no_image_presented():
    abort(406, message='No image presented')


# Abort if methods


def abort_if_order_doesnt_exist_or_get(order_id):
    order = Order.query.get(order_id)
    if order is None:
        abort(404, message='Order with id = {} doesn\'t exists'.format(order_id))
    return order


def abort_if_consumer_doesnt_exist_or_get(consumer_id):
    consumer = Consumer.query.filter_by(entity='consumer').filter_by(id=consumer_id).first()
    if consumer is None:
        abort(404, message='Consumer with id = {} doesn\'t exists'.format(consumer_id))
    return consumer


def abort_if_producer_doesnt_exist_or_get(producer_id):
    producer = Producer.query.filter_by(entity='producer').filter_by(id=producer_id).first()
    if producer is None:
        abort(404, message='Producer with id = {} doesn\'t exists'.format(producer_id))
    return producer


def abort_if_category_doesnt_exist_or_get(category_id):
    category = Category.query.get(category_id)
    if category is None:
        abort(404, message='Category with id = {} doesn\'t exists'.format(category_id))
    return category


def abort_if_category_doesnt_exist_slug_or_get(category_slug):
    category = Category.query.filter_by(slug=category_slug)
    if category is None:
        abort(404, message='Category with name = {} doesn\'t exists'.format(category_slug))
    return category


def abort_if_product_doesnt_exist_or_get(product):
    product = Product.query.get(product)
    if product is None:
        abort(404, message='Product with id = {} doesn\'t exists'.format(product))
    return product


# Get by id methods

def get_orders_by_producer_id(producer_id):
    abort_if_producer_doesnt_exist_or_get(producer_id)
    return Order.query.filter_by(producer_id=producer_id).all()


def get_orders_by_consumer_id(consumer_id):
    abort_if_consumer_doesnt_exist_or_get(consumer_id)
    return Order.query.filter_by(consumer_id=consumer_id).all()


def get_order_by_id(order_id):
    return abort_if_order_doesnt_exist_or_get(order_id)


def get_consumer_by_id(consumer_id):
    return abort_if_consumer_doesnt_exist_or_get(consumer_id)


def get_producer_by_id(producer_id):
    return abort_if_producer_doesnt_exist_or_get(producer_id)


def get_category_by_id(category_id):
    return abort_if_category_doesnt_exist_or_get(category_id)


def get_subcategories_by_category_id(category_id):
    abort_if_category_doesnt_exist_or_get(category_id)
    return Category.query.filter_by(parent_id=category_id).all()


def get_subcategories_by_category_slug(category_slug):
    abort_if_category_doesnt_exist_slug_or_get(category_slug)
    category_id = Category.query.filter_by(slug=category_slug).first().id
    return Category.query.filter_by(parent_id=category_id).all()


def get_product_by_id(product_id):
    return abort_if_product_doesnt_exist_or_get(product_id)


def get_products_by_category_id(category_id):
    category = get_category_by_id(category_id)
    if category.parent_id != 0:
        return category.get_products()
    else:
        subcategories = get_subcategories_by_category_id(category_id)
        divided_products = [subcategory.get_products() for subcategory in subcategories]
        return [product for subcategory in divided_products for product in subcategory]


def get_products_by_producer_id(producer_id):
    abort_if_producer_doesnt_exist_or_get(producer_id)
    return Product.query.filter_by(producer_id=producer_id).all()


def get_cart_by_consumer_id(consumer_id):
    abort_if_consumer_doesnt_exist_or_get(consumer_id)
    cart = Cart.query.filter_by(consumer_id=consumer_id).first()
    return cart if cart is not None else post_cart(consumer_id)


# Get by other params
def get_parent_category_by_category_id(category_id):
    parent_category_id = Category.query.filter_by(id=category_id).first().parent_id
    return get_category_by_id(parent_category_id)


def get_number_of_products_in_cart(consumer_id):
    items = Cart.query.filter_by(consumer_id=consumer_id).first().items
    return sum(int(v) for k, v in items.items())


def get_products_from_cart(items):
    items = {int(k): int(v) for k, v in items.items()}
    products = [get_product_by_id(id) for id in items]
    return products


# Get by name

def get_category_by_name(slug):
    return Category.query.filter_by(slug=slug).first()


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


def get_producer_by_name(name):
    return Producer.query.filter_by(name=name).first()


# Get sorted


def get_popular_products_by_category_id(category_id):
    category = get_category_by_id(category_id)
    return sorted(category.get_products(), key=lambda product: product.times_ordered, reverse=True)


def get_popular_products():
    return sorted(get_all_products(), key=lambda product: product.times_ordered, reverse=True)


# Get all methods

def get_all_orders():
    return Order.query.all()


def get_all_consumers():
    return Consumer.query.filter_by(entity='consumer').all()


def get_all_producers():
    return Producer.query.filter_by(entity='producer').all()


def get_all_base_categories():
    return Category.query.filter_by(parent_id=0).all()


def get_all_products():
    return Product.query.all()


# Category methods
def delete_categories_if_it_was_the_last_product(product):
    quantity_of_products_with_this_category = len(Product.query.filter_by(producer_id=product.producer_id).filter_by(
        category_id=product.category_id).all())
    if quantity_of_products_with_this_category == 1:
        category = get_category_by_id(product.category_id)
        producer = get_producer_by_id(product.producer_id)
        producer.categories.remove(category)
        subcategories = get_subcategories_by_category_id(category.parent_id)
        has_such_categories = False
        for cat in subcategories:
            if cat in producer.categories:
                has_such_categories = True
                break
        if not has_such_categories:
            parent_category = get_category_by_id(category.parent_id)
            producer.categories.remove(parent_category)


def add_product_categories_if_producer_doesnt_have_them(product, new_category_id):
    producer = get_producer_by_id(product.producer_id)
    category = get_category_by_id(new_category_id)
    parent_category = get_category_by_id(category.parent_id)
    for category in (category, parent_category):
        if category not in producer.categories:
            producer.categories.append(category)


def check_producer_categories(new_category_id, product):
    if product.category_id != int(new_category_id):
        delete_categories_if_it_was_the_last_product(product)
        add_product_categories_if_producer_doesnt_have_them(product, new_category_id)


# Product methods

def producer_has_product_with_such_name(args):
    if Product.query.filter_by(producer_id=args['producer_id']).filter_by(name=args['name']).first():
        return True


# Post methods

def post_order(args):
    abort_if_producer_doesnt_exist_or_get(args['producer_id'])
    abort_if_consumer_doesnt_exist_or_get(args['consumer_id'])
    new_order = order_schema.load(args).data
    db.session.add(new_order)
    db.session.commit()
    return new_order


def post_consumer(args):
    validate_registration_data(args['email'], args['password'])
    check_email_uniqueness(args['email'])
    new_consumer = consumer_sign_up_schema.load(args).data
    db.session.add(new_consumer)
    db.session.commit()
    email_tools.send_confirmation_email(new_consumer.email)
    return new_consumer


def post_producer(args):
    validate_registration_data(args['email'], args['password'])
    check_email_uniqueness(args['email'])
    check_producer_name_uniqueness(args['name'])
    new_producer = producer_sign_up_schema.load(args).data
    db.session.add(new_producer)
    db.session.commit()
    email_tools.send_confirmation_email(new_producer.email)
    return new_producer


def post_product(args):
    abort_if_producer_doesnt_exist_or_get(args['producer_id'])
    abort_if_category_doesnt_exist_or_get(args['category_id'])
    new_product = product_schema.load(args).data
    db.session.add(new_product)
    producer = get_producer_by_id(args['producer_id'])
    category = get_category_by_id(args['category_id'])
    parent_category = get_category_by_id(category.parent_id)
    for category in (category, parent_category):
        if category not in producer.categories:
            producer.categories.append(category)
    db.session.commit()
    return new_product


def post_cart(consumer_id):
    cart = Cart(consumer_id)
    db.session.add(cart)
    db.session.commit()
    return cart


def post_item_to_cart_by_consumer_id(args, consumer_id):
    abort_if_product_doesnt_exist_or_get(int(args['product_id']))
    cart = get_cart_by_consumer_id(consumer_id)
    if args['mode'] == 'inc':
        cart.increase_item_quantity(args['product_id'], args['quantity'])
    elif args['mode'] == 'dec':
        cart.decrease_item_quantity(args['product_id'], args['quantity'])
    elif args['mode'] == 'set':
        cart.set_item_quantity(args['product_id'], args['quantity'])
    db.session.commit()
    return cart


def remove_item_from_cart_by_consumer_id(args, consumer_id):
    abort_if_product_doesnt_exist_or_get(int(args['product_id']))
    cart = get_cart_by_consumer_id(consumer_id)
    cart.remove_item(args['product_id'])
    db.session.commit()
    return cart


# Put methods

def put_order(args, order_id):
    order = get_order_by_id(order_id)
    if args['status'] is not None:
        order.change_status(args['status'])
    db.session.commit()
    return order


def put_producer(args, producer_id):
    producer = get_producer_by_id(producer_id)
    args['id'] = None
    for k, v in args.items():
        if v:
            setattr(producer, k, v)
    db.session.commit()
    return producer


def put_consumer(args, consumer_id):
    consumer = get_consumer_by_id(consumer_id)
    args['id'] = None
    for k, v in args.items():
        if v:
            setattr(consumer, k, v)
    db.session.commit()
    return consumer


def put_product(args, product_id):
    product = get_product_by_id(product_id)

    if args['category_id']:
        check_producer_categories(args['category_id'], product)

    args['id'] = None
    args['producer_id'] = None
    for k, v in args.items():
        if v:
            setattr(product, k, v)
    db.session.commit()
    return product


# Delete methods

def delete_consumer_by_id(consumer_id):
    consumer = get_consumer_by_id(consumer_id)
    db.session.delete(consumer)
    db.session.commit()
    return {"message": "Consumer with id {} has been deleted".format(consumer_id)}


def delete_producer_by_id(producer_id):
    producer = get_producer_by_id(producer_id)
    db.session.delete(producer)
    db.session.commit()
    return {"message": "Producer with id {} has been deleted succesfully".format(producer_id)}


def delete_product_by_id(product_id):
    product = get_product_by_id(product_id)
    delete_categories_if_it_was_the_last_product(product)
    db.session.delete(product)
    db.session.commit()
    return {"message": "Product with id {} has been deleted successfully".format(product_id)}


def clear_cart_by_consumer_id(consumer_id):
    cart = get_cart_by_consumer_id(consumer_id)
    cart.clear_cart()
    db.session.commit()
    return {"message": "Cart has been cleared successfully".format(consumer_id)}


# Login/Logout

def login(args):
    user = User.query.filter_by(email=args['email']).first()
    if user is None or not user.check_password(args['password']):
        return False
    # Вместо True потом добавить возможность пользователю выбирать запоминать его или нет
    login_user(user, True)
    return {"id": user.id}


def logout():
    logout_user()
    return 'Logout'


# Validation

def validate_registration_data(email, password):
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_pattern, email):
        failed_email_check(email)
    if len(password) < 6:
        failed_password_len_check()
    return True


# Checkers

def check_email_uniqueness(email):
    if get_user_by_email(email) is not None:
        failed_email_uniqueness_check(email)


def check_producer_name_uniqueness(name):
    if get_producer_by_name(name) is not None:
        failed_producer_name_uniqueness_check(name)


# Uploaders

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_extension(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(uploader, files):
    if 'image' not in files:
        no_file_part_in_request()
    image = files['image']
    if image.filename == '':
        no_image_presented()
    if image and allowed_extension(image.filename):
        image_url = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
        image.save(image_url)
        uploader.set_photo_url(image_url)
        db.session.commit()
    return True


def upload_consumer_image(consumer_id, files):
    consumer = get_consumer_by_id(consumer_id)
    return upload_image(consumer, files)


def upload_producer_image(producer_id, files):
    producer = get_producer_by_id(producer_id)
    return upload_image(producer, files)


def upload_product_image(product_id, files):
    product = get_product_by_id(product_id)
    return upload_image(product, files)
