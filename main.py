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



@app.route('/submissao_caso_teste', methods=['POST'])
def realiza_submissao_por_caso():
    body_json = request.json

    with open("entradas.txt", "w") as arquivo_entradas:
        entradas = body_json.get("entradas").split('\n')
        for linha in range(len(entradas)):
            arquivo_entradas.write(f"{entradas[linha]}\n")

    linhas_inicio = ['import sys\n',
                     f'sys.stdin = open("entradas.txt", "r")\n']

    codigo = ''.join(linhas_inicio) + body_json.get("codigoResposta")

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


    return {
        'entrada': body_json.get("entradas"),
        'saida': ''.join(out),
        'status': 'ok',
        'tempo': fim - inicio
    }


app.run()
