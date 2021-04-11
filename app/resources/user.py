from flask_restful import Resource, marshal, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models import User
from app.schemas import user_items_fields


class Profile(Resource):

    @jwt_required
    def put(self):
        parser = reqparse.RequestParser(trim=True)
        parser.add_argument(
            "first_name", required=True, help="o campo primeiro nome é obrigatório."
        )
        parser.add_argument(
            "last_name", required=True, help="o campo último nome é obrigatório."
        )
        parser.add_argument(
            "document", required=True, help="o documento é obrigatório."
        )
        parser.add_argument(
            "phone", required=True, help="o campo telefone é obrigatório."
        )
        args = parser.parse_args(strict=True)

        current_user = get_jwt_identity()


class Orders(Resource):

    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.get(current_user["id"])
        return marshal(user.items, user_items_fields)
