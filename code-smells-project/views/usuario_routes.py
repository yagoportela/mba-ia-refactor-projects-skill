from flask import Blueprint, request

from controllers import usuario_controller

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.get("/usuarios")
def listar_usuarios():
    return usuario_controller.listar(request.args)


@usuarios_bp.get("/usuarios/<int:usuario_id>")
def buscar_usuario(usuario_id):
    return usuario_controller.buscar(usuario_id)


@usuarios_bp.post("/usuarios")
def criar_usuario():
    return usuario_controller.criar(request.get_json(silent=True))


@usuarios_bp.post("/login")
def login():
    return usuario_controller.login(request.get_json(silent=True))
