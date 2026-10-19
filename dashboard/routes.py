from flask import Blueprint, render_template
from database import get_connection

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')

@dashboard_bp.route('/')
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM clientes")
    total_clientes = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM categorias")
    total_categorias = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM produtos")
    total_produtos = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total, COALESCE(SUM(total), 0) AS faturamento FROM vendas")
    res_vendas = cursor.fetchone()
    total_vendas = res_vendas['total']
    faturamento = res_vendas['faturamento']

    cursor.close()
    conn.close()

    return render_template(
        'index.html',
        total_clientes=total_clientes,
        total_categorias=total_categorias,
        total_produtos=total_produtos,
        total_vendas=total_vendas,
        faturamento=faturamento
    )