import os
import shutil
from sqlalchemy import update

from marketplace import db, email_tools, app, sitemap_tools
from marketplace.api_folder.schemas import producer_sign_up_schema
from marketplace.api_folder.utils.abortions import abort_if_producer_doesnt_exist_or_get, abort_if_invalid_rating_value
from marketplace.api_folder.utils.checkers import check_email_uniqueness, check_producer_name_uniqueness
from marketplace.api_folder.utils.uploaders import upload_image
from marketplace.api_folder.utils.validators import validate_registration_data
from marketplace.models import Producer, Category, Product


def get_producer_by_id(producer_id: int) -> Producer:
    """Returns producer"""
    return abort_if_producer_doesnt_exist_or_get(producer_id)


def get_producer_rating_by_id(producer_id: int) -> float:
    """Returns producer's rating"""
    return round(get_producer_by_id(producer_id).rating, 2)


def get_producer_by_name(name: str) -> Producer:
    """Returns producer by name"""
    return Producer.query.filter_by(name=name).first()


def get_producer_name_by_id(producer_id: int) -> str:
    """Returns producers's name"""
    return db.session.query(Producer.name).filter(Producer.id == producer_id).first()[0]


def get_all_producers() -> list:
    """"Returns all producers"""
    return Producer.query.filter_by(entity='producer').all()


def post_producer(args: dict) -> Producer:
    """Post producer and return him"""
    validate_registration_data(args['email'], args['password'])
    check_email_uniqueness(args['email'])
    check_producer_name_uniqueness(args['name'])
    new_producer = producer_sign_up_schema.load(args).data
    db.session.add(new_producer)
    db.session.commit()
    # make directory to store this producer's images
    os.mkdir(os.path.join(os.getcwd(), 'marketplace/static/img/user_images/' + str(new_producer.id) + '/'))
    email_tools.send_confirmation_email(new_producer.email, new_producer.person_to_contact)
    sitemap_tools.create_producer_sitemap.apply_async((new_producer.id,),
                                                      link=sitemap_tools.add_producer_to_global_sitemap.s())
    return new_producer


def put_producer(args: dict, producer_id: int) -> Producer:
    """Change producer and returns it"""
    producer = get_producer_by_id(producer_id)
    args['id'] = None
    for k, v in args.items():
        if v:
            setattr(producer, k, v)
    db.session.commit()
    sitemap_tools.update_producer_sitemap.apply_async((producer_id,),
                                                      link=sitemap_tools.update_producer_info_in_global_sitemap.s())
    return producer


def delete_producer_by_id(producer_id: int) -> dict:
    """Delete producer with given id"""
    producer = get_producer_by_id(producer_id)
    # TODO перенести функцию get_products_by_producer_id из product_utils в producer_utils
    # producer_products = get_products_by_producer_id(producer_id)
    producer_products = Product.query.filter_by(producer_id=producer_id).all()
    for product in producer_products:
        db.session.delete(product)
    image_directory_path = os.path.join(os.getcwd(), 'marketplace/static/img/user_images/' + str(producer_id) + '/')
    shutil.rmtree(image_directory_path)
    db.session.delete(producer)
    db.session.commit()
    sitemap_tools.delete_producer_sitemap.apply_async((producer_id,),
                                                      link=sitemap_tools.delete_producer_from_global_sitemap.s())
    return {"message": "Producer with id {} has been deleted successfully".format(producer_id)}


def upload_producer_image(producer_id: int, image_data) -> bool:
    """Upload producer's image"""
    producer = get_producer_by_id(producer_id)
    image_size = app.config['USER_IMAGE_PRODUCER_LOGO_SIZE']
    return upload_image(producer, image_data, producer_id, image_size)


def get_producer_names_by_category_name(category_name: str) -> list:
    """Returns list of producers with category presented"""
    category = Category.query.filter_by(name=category_name).first()
    producers = get_all_producers()
    return [producer.name for producer in producers if category in producer.categories]
