from flask_restful import Resource, reqparse
import marketplace.api_folder.api_utils as utils
from marketplace.api_folder.schemas import order_schema_list, order_schema

order_args = ['orders', 'delivery_address', 'phone', 'email', 'consumer_id', 'status', 'total_cost', 'first_name',
              'last_name']
parser = reqparse.RequestParser()

for arg in order_args:
    parser.add_argument(arg)


class GlobalOrders(Resource):

    def get(self):
        response = dict()
        page_number = utils.get_page_number()
        page = utils.get_all_orders(page_number)
        response['meta'] = utils.get_meta_from_page(page_number, page)
        response['body'] = order_schema_list.dump(page.items).data
        return response, 200

    def post(self):
        args = parser.parse_args()
        utils.decrease_products_quantity_and_increase_times_ordered(args['consumer_id'])
        utils.post_orders(args)
        return "Заказ был успешно оформлен", 201


class Orders(Resource):
    def get(self, order_id):
        return order_schema.dump(utils.get_order_by_id(order_id)).data

    def put(self, order_id):
        args = parser.parse_args()
        return order_schema.dump(utils.put_order(args, order_id)).data, 201

    def delete(self, order_id):
        utils.increase_products_quantity_and_decrease_times_ordered(order_id)
        return utils.delete_order_by_id(order_id), 202


class UnprocessedOrdersByProducerId(Resource):
    def get(self, producer_id):
        return {"quantity": utils.get_number_of_unprocessed_orders_by_producer_id(producer_id)}, 200
