from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

produtos_bp = Blueprint('produtos', __name__, template_folder='templates')

@produtos_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT p.*, c.nome AS categoria_nome 
        FROM produtos p
        LEFT JOIN categorias c ON p.id_categoria = c.id
        ORDER BY p.id DESC
    """
    cursor.execute(query)
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('produtos/lista.html', produtos=produtos)

@produtos_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        id_categoria = request.form.get('id_categoria')

        if not codigo or not nome or not preco or not id_categoria:
            flash('Código, nome, preço e categoria são obrigatórios!', 'danger')
            cursor.execute("SELECT id, nome FROM categorias ORDER BY nome ASC")
            categorias = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('produtos/form.html', produto=None, categorias=categorias)

        cursor.execute(
            "INSERT INTO produtos (codigo, nome, descricao, preco, id_categoria) VALUES (%s, %s, %s, %s, %s)",
            (codigo, nome, descricao, float(preco), int(id_categoria))
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('produtos.listar'))

    cursor.execute("SELECT id, nome FROM categorias ORDER BY nome ASC")
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('produtos/form.html', produto=None, categorias=categorias)

@produtos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        id_categoria = request.form.get('id_categoria')

        if not codigo or not nome or not preco or not id_categoria:
            flash('Código, nome, preço e categoria são obrigatórios!', 'danger')
            cursor.execute("SELECT id, nome FROM categorias ORDER BY nome ASC")
            categorias = cursor.fetchall()
            cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
            produto = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template('produtos/form.html', produto=produto, categorias=categorias)

        cursor.execute(
            "UPDATE produtos SET codigo = %s, nome = %s, descricao = %s, preco = %s, id_categoria = %s WHERE id = %s",
            (codigo, nome, descricao, float(preco), int(id_categoria), id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('produtos.listar'))

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
    produto = cursor.fetchone()

    cursor.execute("SELECT id, nome FROM categorias ORDER BY nome ASC")
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()

    if not produto:
        flash('Produto não encontrado!', 'warning')
        return redirect(url_for('produtos.listar'))

    return render_template('produtos/form.html', produto=produto, categorias=categorias)

@produtos_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Produto removido com sucesso!', 'success')
    return redirect(url_for('produtos.listar'))