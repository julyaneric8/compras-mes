import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database" / "compras.db"

MESES = [
    "",
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro"
]

CATEGORIAS = [
    "Alimentação",
    "Limpeza",
    "Higiene",
    "Bebidas",
    "Outros"
]


# Banco de dados

def conectar_banco():
    conexao = sqlite3.connect(DATABASE)
    conexao.row_factory = sqlite3.Row

    return conexao


def coluna_existe(conexao, tabela, coluna):
    colunas = conexao.execute(
        f"PRAGMA table_info({tabela})"
    ).fetchall()

    return any(
        item["name"] == coluna
        for item in colunas
    )


def criar_banco():
    DATABASE.parent.mkdir(exist_ok=True)

    hoje = date.today()

    with conectar_banco() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY,
                orcamento_centavos INTEGER NOT NULL
            )
            """
        )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                preco_centavos INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                ano INTEGER NOT NULL,
                comprado INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        if not coluna_existe(
            conexao,
            "produtos",
            "mes"
        ):
            conexao.execute(
                """
                ALTER TABLE produtos
                ADD COLUMN mes INTEGER
                """
            )

            conexao.execute(
                """
                UPDATE produtos
                SET mes = ?
                WHERE mes IS NULL
                """,
                (hoje.month,)
            )

        if not coluna_existe(
            conexao,
            "produtos",
            "ano"
        ):
            conexao.execute(
                """
                ALTER TABLE produtos
                ADD COLUMN ano INTEGER
                """
            )

            conexao.execute(
                """
                UPDATE produtos
                SET ano = ?
                WHERE ano IS NULL
                """,
                (hoje.year,)
            )

        if not coluna_existe(
            conexao,
            "produtos",
            "comprado"
        ):
            conexao.execute(
                """
                ALTER TABLE produtos
                ADD COLUMN comprado INTEGER
                NOT NULL DEFAULT 0
                """
            )

        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mes INTEGER NOT NULL,
                ano INTEGER NOT NULL,
                valor_centavos INTEGER NOT NULL,
                UNIQUE (mes, ano)
            )
            """
        )

        configuracao_antiga = conexao.execute(
            """
            SELECT orcamento_centavos
            FROM configuracoes
            WHERE id = 1
            """
        ).fetchone()

        orcamento_atual = conexao.execute(
            """
            SELECT id
            FROM orcamentos
            WHERE mes = ?
              AND ano = ?
            """,
            (
                hoje.month,
                hoje.year
            )
        ).fetchone()

        if orcamento_atual is None:
            if configuracao_antiga is not None:
                valor_inicial = (
                    configuracao_antiga[
                        "orcamento_centavos"
                    ]
                )
            else:
                valor_inicial = 80000

            conexao.execute(
                """
                INSERT INTO orcamentos (
                    mes,
                    ano,
                    valor_centavos
                )
                VALUES (?, ?, ?)
                """,
                (
                    hoje.month,
                    hoje.year,
                    valor_inicial
                )
            )

        conexao.commit()


# Dinheiro

def decimal_para_centavos(valor):
    valor = valor.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return int(valor * 100)


def texto_para_decimal(valor):
    valor = valor.strip()

    if not valor:
        raise InvalidOperation

    if "," in valor:
        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

    return Decimal(valor)


def formatar_reais(centavos):
    valor = (
        Decimal(centavos)
        / Decimal("100")
    )

    texto = f"{valor:,.2f}"

    texto = texto.replace(",", "X")
    texto = texto.replace(".", ",")
    texto = texto.replace("X", ".")

    return f"R$ {texto}"


# Mês

def normalizar_mes_ano(mes, ano):
    hoje = date.today()

    try:
        mes = int(mes)
        ano = int(ano)
    except (TypeError, ValueError):
        return hoje.month, hoje.year

    if mes < 1 or mes > 12:
        return hoje.month, hoje.year

    return mes, ano


def mes_anterior(mes, ano):
    if mes == 1:
        return 12, ano - 1

    return mes - 1, ano


def proximo_mes(mes, ano):
    if mes == 12:
        return 1, ano + 1

    return mes + 1, ano


# Orçamento mensal

def obter_orcamento_centavos(mes, ano):
    with conectar_banco() as conexao:
        orcamento = conexao.execute(
            """
            SELECT valor_centavos
            FROM orcamentos
            WHERE mes = ?
              AND ano = ?
            """,
            (
                mes,
                ano
            )
        ).fetchone()

    if orcamento is None:
        return 0

    return orcamento["valor_centavos"]


def salvar_orcamento(valor, mes, ano):
    centavos = decimal_para_centavos(valor)

    with conectar_banco() as conexao:
        orcamento = conexao.execute(
            """
            SELECT id
            FROM orcamentos
            WHERE mes = ?
              AND ano = ?
            """,
            (
                mes,
                ano
            )
        ).fetchone()

        if orcamento is None:
            conexao.execute(
                """
                INSERT INTO orcamentos (
                    mes,
                    ano,
                    valor_centavos
                )
                VALUES (?, ?, ?)
                """,
                (
                    mes,
                    ano,
                    centavos
                )
            )

        else:
            conexao.execute(
                """
                UPDATE orcamentos
                SET valor_centavos = ?
                WHERE mes = ?
                  AND ano = ?
                """,
                (
                    centavos,
                    mes,
                    ano
                )
            )

        conexao.commit()


# Produtos

def obter_produtos(mes, ano):
    with conectar_banco() as conexao:
        produtos_banco = conexao.execute(
            """
            SELECT
                id,
                nome,
                categoria,
                preco_centavos,
                quantidade,
                mes,
                ano,
                comprado
            FROM produtos
            WHERE mes = ?
              AND ano = ?
            ORDER BY comprado ASC, id DESC
            """,
            (
                mes,
                ano
            )
        ).fetchall()

    produtos = []

    for produto in produtos_banco:
        subtotal_centavos = (
            produto["preco_centavos"]
            * produto["quantidade"]
        )

        preco_edicao = (
            Decimal(
                produto["preco_centavos"]
            )
            / Decimal("100")
        )

        produtos.append(
            {
                "id": produto["id"],
                "nome": produto["nome"],
                "categoria": produto["categoria"],
                "preco_centavos": produto[
                    "preco_centavos"
                ],
                "quantidade": produto[
                    "quantidade"
                ],
                "comprado": bool(
                    produto["comprado"]
                ),
                "subtotal_centavos": (
                    subtotal_centavos
                ),
                "preco_formatado": formatar_reais(
                    produto["preco_centavos"]
                ),
                "preco_edicao": (
                    f"{preco_edicao:.2f}"
                    .replace(".", ",")
                ),
                "subtotal_formatado": formatar_reais(
                    subtotal_centavos
                )
            }
        )

    return produtos


# Resumo por categoria

def calcular_resumo_categorias(produtos):
    totais = {
        categoria: 0
        for categoria in CATEGORIAS
    }

    for produto in produtos:
        categoria = produto["categoria"]

        if categoria not in totais:
            categoria = "Outros"

        totais[categoria] += (
            produto["subtotal_centavos"]
        )

    total_geral = sum(
        totais.values()
    )

    resumo = []

    for categoria in CATEGORIAS:
        total_categoria = totais[categoria]

        if total_geral > 0:
            porcentagem = (
                total_categoria
                / total_geral
                * 100
            )
        else:
            porcentagem = 0

        resumo.append(
            {
                "nome": categoria,
                "total_centavos": total_categoria,
                "total_formatado": formatar_reais(
                    total_categoria
                ),
                "porcentagem": porcentagem
            }
        )

    resumo.sort(
        key=lambda item: item["total_centavos"],
        reverse=True
    )

    categorias_com_gasto = [
        categoria
        for categoria in resumo
        if categoria["total_centavos"] > 0
    ]

    if categorias_com_gasto:
        maior_categoria = (
            categorias_com_gasto[0]
        )
    else:
        maior_categoria = None

    return resumo, maior_categoria


# Página principal

@app.route("/")
def index():
    hoje = date.today()

    mes, ano = normalizar_mes_ano(
        request.args.get(
            "mes",
            hoje.month
        ),
        request.args.get(
            "ano",
            hoje.year
        )
    )

    produtos = obter_produtos(
        mes,
        ano
    )

    orcamento_centavos = (
        obter_orcamento_centavos(
            mes,
            ano
        )
    )

    gasto_centavos = sum(
        produto["subtotal_centavos"]
        for produto in produtos
    )

    restante_centavos = (
        orcamento_centavos
        - gasto_centavos
    )

    quantidade_comprados = sum(
        1
        for produto in produtos
        if produto["comprado"]
    )

    if orcamento_centavos > 0:
        porcentagem = (
            gasto_centavos
            / orcamento_centavos
            * 100
        )
    else:
        porcentagem = 0

    porcentagem_barra = min(
        max(porcentagem, 0),
        100
    )

    resumo_categorias, maior_categoria = (
        calcular_resumo_categorias(
            produtos
        )
    )

    mes_anterior_numero, ano_anterior = (
        mes_anterior(
            mes,
            ano
        )
    )

    proximo_mes_numero, proximo_ano = (
        proximo_mes(
            mes,
            ano
        )
    )

    return render_template(
        "index.html",

        produtos=produtos,

        quantidade_produtos=len(
            produtos
        ),

        quantidade_comprados=(
            quantidade_comprados
        ),

        orcamento=formatar_reais(
            orcamento_centavos
        ),

        gasto=formatar_reais(
            gasto_centavos
        ),

        restante=formatar_reais(
            restante_centavos
        ),

        porcentagem=porcentagem,
        porcentagem_barra=porcentagem_barra,

        resumo_categorias=resumo_categorias,
        maior_categoria=maior_categoria,

        mes=mes,
        ano=ano,

        nome_mes=MESES[mes],

        mes_anterior=mes_anterior_numero,
        ano_anterior=ano_anterior,

        proximo_mes=proximo_mes_numero,
        proximo_ano=proximo_ano
    )


# Alterar orçamento

@app.route(
    "/orcamento",
    methods=["POST"]
)
def atualizar_orcamento():
    valor = request.form.get(
        "orcamento",
        ""
    )

    mes, ano = normalizar_mes_ano(
        request.form.get("mes"),
        request.form.get("ano")
    )

    try:
        novo_orcamento = (
            texto_para_decimal(valor)
        )

        if novo_orcamento >= 0:
            salvar_orcamento(
                novo_orcamento,
                mes,
                ano
            )

    except InvalidOperation:
        pass

    return redirect(
        url_for(
            "index",
            mes=mes,
            ano=ano
        )
    )


# Adicionar produto

@app.route(
    "/produto",
    methods=["POST"]
)
def adicionar_produto():
    nome = request.form.get(
        "produto",
        ""
    ).strip()

    categoria = request.form.get(
        "categoria",
        "Outros"
    ).strip()

    preco_texto = request.form.get(
        "preco",
        ""
    )

    quantidade_texto = request.form.get(
        "quantidade",
        "1"
    )

    mes, ano = normalizar_mes_ano(
        request.form.get("mes"),
        request.form.get("ano")
    )

    try:
        preco = texto_para_decimal(
            preco_texto
        )

        quantidade = int(
            quantidade_texto
        )

        if (
            nome
            and preco >= 0
            and quantidade >= 1
        ):
            preco_centavos = (
                decimal_para_centavos(
                    preco
                )
            )

            with conectar_banco() as conexao:
                conexao.execute(
                    """
                    INSERT INTO produtos (
                        nome,
                        categoria,
                        preco_centavos,
                        quantidade,
                        mes,
                        ano,
                        comprado
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                    """,
                    (
                        nome,
                        categoria,
                        preco_centavos,
                        quantidade,
                        mes,
                        ano
                    )
                )

                conexao.commit()

    except (
        InvalidOperation,
        ValueError
    ):
        pass

    return redirect(
        url_for(
            "index",
            mes=mes,
            ano=ano
        )
    )


# Marcar como comprado

@app.route(
    "/produto/<int:produto_id>/comprado",
    methods=["POST"]
)
def alternar_comprado(produto_id):
    mes, ano = normalizar_mes_ano(
        request.form.get("mes"),
        request.form.get("ano")
    )

    with conectar_banco() as conexao:
        produto = conexao.execute(
            """
            SELECT comprado
            FROM produtos
            WHERE id = ?
            """,
            (produto_id,)
        ).fetchone()

        if produto is not None:
            novo_estado = (
                0 if produto["comprado"] else 1
            )

            conexao.execute(
                """
                UPDATE produtos
                SET comprado = ?
                WHERE id = ?
                """,
                (
                    novo_estado,
                    produto_id
                )
            )

            conexao.commit()

    return redirect(
        url_for(
            "index",
            mes=mes,
            ano=ano
        )
    )


# Editar produto

@app.route(
    "/produto/<int:produto_id>/editar",
    methods=["POST"]
)
def editar_produto(produto_id):
    nome = request.form.get(
        "produto",
        ""
    ).strip()

    categoria = request.form.get(
        "categoria",
        "Outros"
    ).strip()

    preco_texto = request.form.get(
        "preco",
        ""
    )

    quantidade_texto = request.form.get(
        "quantidade",
        "1"
    )

    mes, ano = normalizar_mes_ano(
        request.form.get("mes"),
        request.form.get("ano")
    )

    try:
        preco = texto_para_decimal(
            preco_texto
        )

        quantidade = int(
            quantidade_texto
        )

        if (
            nome
            and preco >= 0
            and quantidade >= 1
        ):
            preco_centavos = (
                decimal_para_centavos(
                    preco
                )
            )

            with conectar_banco() as conexao:
                conexao.execute(
                    """
                    UPDATE produtos
                    SET
                        nome = ?,
                        categoria = ?,
                        preco_centavos = ?,
                        quantidade = ?
                    WHERE id = ?
                    """,
                    (
                        nome,
                        categoria,
                        preco_centavos,
                        quantidade,
                        produto_id
                    )
                )

                conexao.commit()

    except (
        InvalidOperation,
        ValueError
    ):
        pass

    return redirect(
        url_for(
            "index",
            mes=mes,
            ano=ano
        )
    )


# Excluir produto

@app.route(
    "/produto/<int:produto_id>/excluir",
    methods=["POST"]
)
def excluir_produto(produto_id):
    mes, ano = normalizar_mes_ano(
        request.form.get("mes"),
        request.form.get("ano")
    )

    with conectar_banco() as conexao:
        conexao.execute(
            """
            DELETE FROM produtos
            WHERE id = ?
            """,
            (produto_id,)
        )

        conexao.commit()

    return redirect(
        url_for(
            "index",
            mes=mes,
            ano=ano
        )
    )


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)