from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

vendas_bp = Blueprint('vendas', __name__, template_folder='templates')

@vendas_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT v.*, c.nome AS cliente_nome 
        FROM vendas v
        JOIN clientes c ON v.id_cliente = c.id
        ORDER BY v.id DESC
    """
    cursor.execute(query)
    vendas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('vendas/lista.html', vendas=vendas)

@vendas_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        id_cliente = request.form.get('id_cliente')
        produtos_selecionados = request.form.getlist('id_produto[]')
        quantidades = request.form.getlist('quantidade[]')

        if not id_cliente or not produtos_selecionados:
            flash('Selecione um cliente e pelo menos um produto para realizar a venda!', 'danger')
            cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
            clientes = cursor.fetchall()
            cursor.execute("SELECT id, nome, preco FROM produtos ORDER BY nome ASC")
            produtos = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('vendas/form.html', clientes=clientes, produtos=produtos)

        total_venda = 0.0
        itens_para_gravar = []

        # Calcula o subtotal de cada produto com base no preço cadastrado
        for prod_id, qtd_str in zip(produtos_selecionados, quantidades):
            if prod_id and qtd_str:
                qtd = int(qtd_str)
                if qtd > 0:
                    cursor.execute("SELECT preco FROM produtos WHERE id = %s", (prod_id,))
                    prod = cursor.fetchone()
                    if prod:
                        preco_unit = float(prod['preco'])
                        total_venda += preco_unit * qtd
                        itens_para_gravar.append((int(prod_id), qtd, preco_unit))

        if not itens_para_gravar:
            flash('Informe quantidades válidas para os produtos selecionados!', 'danger')
            cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
            clientes = cursor.fetchall()
            cursor.execute("SELECT id, nome, preco FROM produtos ORDER BY nome ASC")
            produtos = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('vendas/form.html', clientes=clientes, produtos=produtos)

        # Grava a venda principal
        cursor.execute(
            "INSERT INTO vendas (id_cliente, total) VALUES (%s, %s)",
            (id_cliente, total_venda)
        )
        id_venda = cursor.lastrowid

        # Grava os itens vinculados a essa venda
        for item in itens_para_gravar:
            cursor.execute(
                "INSERT INTO itens_venda (id_venda, id_produto, quantidade, preco_unitario) VALUES (%s, %s, %s, %s)",
                (id_venda, item[0], item[1], item[2])
            )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Venda registrada com sucesso!', 'success')
        return redirect(url_for('vendas.detalhes', id=id_venda))

    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
    clientes = cursor.fetchall()

    cursor.execute("SELECT id, nome, preco FROM produtos ORDER BY nome ASC")
    produtos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('vendas/form.html', clientes=clientes, produtos=produtos)

@vendas_bp.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.*, c.nome AS cliente_nome, c.email AS cliente_email
        FROM vendas v
        JOIN clientes c ON v.id_cliente = c.id
        WHERE v.id = %s
    """, (id,))
    venda = cursor.fetchone()

    if not venda:
        cursor.close()
        conn.close()
        flash('Venda não encontrada!', 'warning')
        return redirect(url_for('vendas.listar'))

    cursor.execute("""
        SELECT iv.*, p.nome AS produto_nome, p.codigo AS produto_codigo, (iv.quantidade * iv.preco_unitario) AS subtotal
        FROM itens_venda iv
        JOIN produtos p ON iv.id_produto = p.id
        WHERE iv.id_venda = %s
    """, (id,))
    itens = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('vendas/detalhes.html', venda=venda, itens=itens)

@vendas_bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM itens_venda WHERE id_venda = %s", (id,))
    cursor.execute("DELETE FROM vendas WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Venda removida com sucesso!', 'success')
    return redirect(url_for('vendas.listar'))