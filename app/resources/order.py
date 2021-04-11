import datetime
import logging
from flask import current_app
from flask_restful import Resource, reqparse, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from random import getrandbits

from app.models import Product, Order, Item
from app.extensions import db
from app.schemas import order_fields
from app.services.picpay import picpay


class Create(Resource):

    @jwt_required
    def post(self):
        current_user = get_jwt_identity()

        parser = reqparse.RequestParser()
        parser.add_argument(
            "product_id",
            type=int,
            required=True,
            help="o campo id do produto é obrigatório.",
        )
        parser.add_argument(
            "quantity",
            type=int,
            required=True,
            help="o campo quantidade é obrigatório.",
        )

        args = parser.parse_args()

        product = Product.query.get(args.product_id)
        if not product:
            return {"message": "produto não encontrado."}, 400

        if args.quantity > product.quantity:
            return {"message": "não possuimos essa quantidade."}, 400

        try:
            order = Order()
            order.reference_id = f"FLS-{getrandbits(16)}"
            db.session.add(order)
            db.session.commit()

            item = Item()
            item.order_id = order.id
            item.product_id = product.id
            item.user_id = current_user["id"]
            item.quantity = args.quantity
            item.price = product.price * args.quantity
            db.session.add(item)
            db.session.commit()

            return marshal(order, order_fields, "order")
        except Exception as e:
            logging.critical(str(e))
            db.session.rollback()
            return {"message": "ocorreu um erro interno, tente novamente"}, 500


class Pay(Resource):

    @jwt_required
    def get(self, reference_id):
        order = Order.query.filter_by(reference_id=reference_id).first()
        if not order:
            return {"esse pedido não existe"}, 400

        expires = datetime.datetime.now() + datetime.timedelta(days=3)

        if not order.item.user.profile:
            return {
                "message": "você precisa atualizar o seu perfil antes de continuar."
            }, 400

        response = picpay.payment(
            {
                "referenceId": order.reference_id,
                "callbackUrl": current_app.config["PICPAY_CALLBACK_URL"],
                "returnUrl": current_app.config["PICPAY_RETURN_URL"],
                "value": order.item.price,
                "expiresAt": expires.isoformat(),
                "buyer": {
                    "firstName": order.user.profile.first_name,
                    "lastName": order.user.profile.last_name,
                    "document": order.user.profile.document,
                    "email": order.user.profile.email,
                    "phone": order.user.profile.phone,
                },
            }
        )

        return response.json()


class Notifications(Resource):
    pass

