from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

categorias_bp = Blueprint('categorias', __name__, template_folder='templates')

@categorias_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias ORDER BY id DESC")
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('categorias/lista.html', categorias=categorias)

@categorias_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')

        if not nome:
            flash('O nome da categoria é obrigatório!', 'danger')
            return redirect(url_for('categorias.novo'))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categorias (nome, descricao) VALUES (%s, %s)",
            (nome, descricao)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Categoria cadastrada com sucesso!', 'success')
        return redirect(url_for('categorias.listar'))

    return render_template('categorias/form.html', categoria=None)

@categorias_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')

        if not nome:
            flash('O nome da categoria é obrigatório!', 'danger')
            return redirect(url_for('categorias.editar', id=id))

        cursor.execute(
            "UPDATE categorias SET nome = %s, descricao = %s WHERE id = %s",
            (nome, descricao, id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Categoria atualizada com sucesso!', 'success')
        return redirect(url_for('categorias.listar'))

    cursor.execute("SELECT * FROM categorias WHERE id = %s", (id,))
    categoria = cursor.fetchone()
    cursor.close()
    conn.close()

    if not categoria:
        flash('Categoria não encontrada!', 'warning')
        return redirect(url_for('categorias.listar'))

    return render_template('categorias/form.html', categoria=categoria)

@categorias_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categorias WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Categoria removida com sucesso!', 'success')
    return redirect(url_for('categorias.listar'))