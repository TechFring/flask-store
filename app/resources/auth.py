import logging
import secrets

from base64 import b64decode
from datetime import timedelta
from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User
from app.extensions import db
from app.services.mail import send_mail


class Login(Resource):

    def get(self):
        if not request.headers.get("Authorization"):
            return {"message": "autorização não encontrada."}, 400

        basic, code = request.headers["Authorization"].split(" ")
        if not basic.lower() == "basic":
            return {"message": "autorização mal formatada."}, 400

        email, password = b64decode(code).decode().split(":")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return {"message": "credenciais inválidas."}, 400

        token = create_access_token({"id": user.id}, expires_delta=timedelta(days=1))

        return {"access_token": token}, 200


class Register(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True, help="o campo email é obrigatório.")
        parser.add_argument(
            "password", required=True, help="o campo senha é obrigatório."
        )
        args = parser.parse_args()

        user = User.query.filter_by(email=args.email).first()
        if user:
            return {"message": "email já cadastrado."}, 400

        user = User()
        user.email = args.email
        user.password = generate_password_hash(args.password, salt_length=10)
        db.session.add(user)

        try:
            db.session.commit()

            send_mail("Seja bem-vindo(a)!", user.email, "welcome", email=user.email)

            return {"message": "usuário registrado com sucesso."}, 201
        except Exception as e:
            db.session.rollback()
            logging.critical(str(e))

            return {"message": "ocorreu um erro interno, tente novamente."}, 500


class ForgetPassword(Resource):

    def post(self):
        parser = reqparse.RequestParser(trim=True)
        parser.add_argument("email", required=True, help="o campo email é obrigatório.")
        args = parser.parse_args()

        user = User.query.filter_by(email=args.email).first()
        if not user:
            return {"message": "email não encontrado."}, 400

        password_temp = secrets.token_hex(16)
        user.password = generate_password_hash(password_temp)
        db.session.add(user)
        db.session.commit()

        send_mail(
            "Recuperação de conta",
            user.email,
            "forget-password",
            password_temp=password_temp,
        )
        return {"message": "email enviado com sucesso."}, 200

