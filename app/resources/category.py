from flask_restful import Resource, marshal_with, marshal

from app.models import Category
from app.schemas import category_fields, category_products_fields


class CategoryList(Resource):

    @marshal_with(category_fields, "categories")
    def get(self):
        categories = Category.query.all()
        return categories


class CategoryGet(Resource):

    def get(self, slug):
        category = Category.query.filter_by(slug=slug).first()

        if not category:
            return {"message": "categoria não encontrada."}, 400

        return marshal(category, category_products_fields, "category")

