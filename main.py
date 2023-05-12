from __future__ import print_function
from flask import Flask, make_response, jsonify, request
import time

import os
import subprocess
import sys


def run(cmd):
    os.environ['PYTHONUNBUFFERED'] = "1"
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                            )
    stdout = []
    stderr = []
    mix = []
    while proc.poll() is None:
        line = proc.stdout.readline()
        if line != "":
            stdout.append(line)
            mix.append(line)
            print(line, end='')

        line = proc.stderr.readline()
        if line != "":
            stderr.append(line)
            mix.append(line)
            print(line, end='')

    return proc.returncode, stdout, stderr, mix


app = Flask('Online Judge')

dict_erros = {
    'Divisão por zero': 'ZeroDivisionError',
    'Índice não encontrado': 'IndexError',
    'Erro de sintáxe': 'SyntaxError',
    'Variável não definida': 'NameError',
    'Erro de tipo': 'TypeError',
    'Erro de valor': 'ValueError',
    'Erro de sistema operacional': 'OSError',
    'Exceção não encontrada': 'Exception'
}


def cria_blocos_except(dict_erros: dict):
    string_retornada = ''

    for key in dict_erros.keys():
        string_retornada += f"except {dict_erros[key]} as err:\n\tprint('{key}', end='')\n"

    return string_retornada


@app.route('/submissao_caso_teste', methods=['POST'], )
def realiza_submissao_por_caso():
    body_json = request.json

    with open("entradas.txt", "w") as arquivo_entradas:
        entradas = body_json.get("entradas").split('\n')
        for linha in range(len(entradas)):
            arquivo_entradas.write(f"{entradas[linha]}\n")

    linhas_inicio = ['import sys\n',
                     f'sys.stdin = open("entradas.txt", "r")\n']

    codigoRespostaComTryExcept = 'try:\n\t' + '\n\t'.join(body_json.get("codigoResposta").split('\n')) \
                                 + '\n' + cria_blocos_except(dict_erros)

    codigo = ''.join(linhas_inicio) + codigoRespostaComTryExcept

    with open('arquivo_codigo', "w") as my_file:
        for linha in range(len(codigo)):
            my_file.write(codigo[linha])
        my_file.close()

    inicio = time.time()
    code, out, err, mix = run([sys.executable, './arquivo_codigo'])
    fim = time.time()

    with open("saidas.txt", "w") as arquivo_saidas:
        for linha in range(len(out)):
            arquivo_saidas.write(out[linha])

    dict_retornado = {
        'entrada': body_json.get("entradas"),
        'saida': ''.join(out),
        'status': 'OK',
        'error': '',
        'tempo': fim - inicio
    }

    # verificando erros em codigo
    if len(out) > 0 and out[-1] in dict_erros.keys():
        dict_retornado['error'] = dict_retornado['saida']
        dict_retornado['saida'] = ''
        dict_retornado['status'] = out[-1]
        dict_retornado['tempo'] = 0

    # verificando erros de apresentacao da saida
    elif dict_retornado['saida'][:-1] != body_json['saida']:
        dict_retornado['status'] = 'Saída incorreta'


    return dict_retornado


app.run()
