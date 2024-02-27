from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
import sqlite3
from flask import jsonify


app = Flask(__name__)
app.secret_key = 'sistemaplanos'

class Cliente:
    def __init__(self, nome, numero, plano, barbeiro, data, valor, ativo=True):
        """
        Inicializa um objeto Cliente com as informações fornecidas.

        Parâmetros:
        - nome (str): Nome do cliente.
        - numero (str): Número de telefone do cliente.
        - plano (str): Tipo de plano do cliente.
        - barbeiro (str): barbeiro vinculado ao plano
        - data (str): Data de início do plano no formato 'dd-mm-yyyy'.
        - valor (float): Valor do plano.
        - ativo (bool): Indica se o plano está ativo (padrão é True).
        """
        self.nome = nome
        self.numero = numero
        self.plano = plano
        self.barbeiro = barbeiro
        # Tratamento de erro para a conversão da data
        try:
            self.data = datetime.strptime(data, '%d-%m-%Y').date()
        except ValueError:
            raise ValueError("Formato de data inválido. Utilize o formato 'dd-mm-yyyy'.")
        self.valor = float(valor)
        self.ativo = bool(ativo)
    
clientes = []

# Função para adicionar um cliente ao banco de dados
def adicionar_cliente(cliente):
    try:
        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()

        # Lógica para adicionar um cliente ao banco de dados
        cursor.execute('''
            INSERT INTO clientes (nome, numero, plano, barbeiro, data, valor, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cliente.nome, cliente.numero, cliente.plano, cliente.barbeiro,
              cliente.data.strftime('%d-%m-%Y'), float(cliente.valor), bool(cliente.ativo)))

        conn.commit()

    except Exception as e:
        print(f"Erro ao adicionar cliente: {e}")

    finally:
        conn.close()

# Rota principal
@app.route('/')
def index():
    return render_template('cliente_form1.html')

# Função para verificar se um cliente com o mesmo nome já existe
def cliente_existente(nome):
    try:
        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()

        # Verifica se já existe um cliente com o mesmo nome no banco de dados
        cursor.execute('SELECT COUNT(*) FROM clientes WHERE nome=?', (nome,))
        count = cursor.fetchone()[0]

        return count > 0

    except Exception as e:
        print(f"Erro ao verificar cliente existente: {e}")
        return False

    finally:
        conn.close()

# Convertendo valor para float para o sistema aceitar valores do usuario
def converter_para_float(valor):
    try:
        # Substitui ',' por '.' e converte para float com duas casas decimais
        valor_float = float(valor.replace(',', '.'))
        return round(valor_float, 2)  # Arredonda para duas casas decimais

    except ValueError:
        # Trata caso o valor não seja válido
        return None


# Rota para lidar com o formulário
@app.route('/adicionar_cliente', methods=['POST'])
def adicionar_cliente_route():
    try:
        # Coleta os dados do formulário
        nome = request.form['nome']
        numero = request.form['numero']
        plano = request.form['plano']
        barbeiro = request.form['barbeiro']
        data = request.form['data']
        valor = request.form['valor']

        # Verifica se o cliente com o mesmo nome já existe
        if cliente_existente(nome):
            flash('Já existe um cliente com o mesmo nome.', 'danger')
            return redirect(url_for('index'))
        

        # Converte o valor para float com duas casas decimais
        valor = converter_para_float(valor)

        # Verifica se a conversão foi bem-sucedida
        if valor is None:
            flash('Valor inválido. Utilize um formato numérico válido.', 'danger')
            return redirect(url_for('index'))

        # Converter a string 'data' para um objeto datetime
        data_datetime = datetime.strptime(data, '%d-%m-%Y').date()

        # Converte timedelta para string antes de concatenar
        vencimento_timedelta = timedelta(days=30)
        vencimento = data_datetime + vencimento_timedelta
        vencimento_str = vencimento.strftime('%d-%m-%Y')

        # Verifica se a data está no futuro
        if data_datetime > datetime.today().date():
            flash('A data do plano deve estar no passado.', 'danger')
            return redirect(url_for('index'))

        ativo = True  # Se está adicionando, presume-se que está ativo
        if datetime.today().date() > vencimento:
            ativo = False

        # Cria um objeto Cliente com os dados do formulário
        novo_cliente = Cliente(nome, numero, plano, barbeiro, data, float(valor), bool(ativo))


        # Adiciona o cliente ao banco de dados
        adicionar_cliente(novo_cliente)

        flash('Cliente adicionado com sucesso!', 'success')
        return redirect(url_for('index'))

    except ValueError:
        flash('Formato de data inválido. Utilize o formato "dd-mm-yyyy".', 'danger')
        return redirect(url_for('index'))

    except Exception as e:
        flash(f'Erro ao adicionar cliente: {e}', 'danger')
        return redirect(url_for('index'))


# Rota para visualizar a lista de clientes
@app.route('/lista_clientes')
def lista_clientes():
    try:
        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()

        # Busca todos os clientes no banco de dados
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()

        return render_template('cliente_form1.html', clientes=clientes)

    except Exception as e:
        print(f"Erro ao buscar lista de clientes: {e}")
        return render_template('error.html')

    finally:
        conn.close()

# Rota para obter a lista de clientes como JSON
@app.route('/get_clientes')
def get_clientes():
    try:
        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()

        # Busca todos os clientes no banco de dados
        cursor.execute('SELECT * FROM clientes')
        clientes = cursor.fetchall()

        return jsonify(clientes)

    except Exception as e:
        print(f"Erro ao buscar lista de clientes: {e}")
        return jsonify([])

    finally:
        conn.close()


# Rota para apagar um cliente
@app.route('/apagar_cliente/<nome>')
def apagar_cliente(nome):
    try:
        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()

        # Apaga o cliente do banco de dados
        cursor.execute('DELETE FROM clientes WHERE nome=?', (nome,))
        conn.commit()

        flash('Cliente apagado com sucesso!', 'success')
        return redirect(url_for('lista_clientes'))

    except Exception as e:
        Flask(f'Erro ao apagar cliente: {e}', 'danger')
        return render_template('error.html')

    finally:
        conn.close()

# Executa a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)