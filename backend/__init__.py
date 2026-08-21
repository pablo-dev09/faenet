"""
FaeNet Backend
==============

Pacote principal do backend Flask da rede social academica FaeNet.

Este pacote expoe a factory ``create_app`` usada por ``app.py`` para criar
a instancia da aplicacao de forma testavel e desacoplada do entrypoint
de producao (gunicorn / wsgi).
"""
