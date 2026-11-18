"""Descarga una captura completa sin sobrescribir el paquete histórico.

Uso: uv run python herramientas/descargar_paquete_offline.py --destino datos_entrega
La carpeta de destino debe ser nueva; las versiones se validan antes de publicarla.
"""
import argparse
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'src'))
from cripta.adaptadores.Network_Adapter import NetworkAdapter
from cripta.adaptadores.Guardar_Llamadas_API import Guardar_Llamadas_API
from cripta.adaptadores.Diagnostico_Red import configurar_registro_red
from cripta.servicio.CriptaService import CriptaService


def _agregar_unicos(destino, valores):
    for valor in valores:
        if valor and valor not in destino:
            destino.append(valor)


def descargar(destino, red=None):
    destino = Path(destino).resolve()
    if destino.exists():
        raise FileExistsError(f'El destino ya existe: {destino}. Use una carpeta nueva.')
    destino.parent.mkdir(parents=True, exist_ok=True)
    red = red if red is not None else NetworkAdapter()
    with tempfile.TemporaryDirectory(prefix='.descarga-cripta-', dir=destino.parent) as temporal:
        guardador = Guardar_Llamadas_API(temporal)
        catalogo_version = red.get_catalog_version()
        guardador.get_catalog_version(catalogo_version)
        criptas = red.crypta_list()
        guardador.crypta_list(criptas)
        total = 0
        for numero, resumen in enumerate(criptas['criptas']):
            if numero:
                total += red.requests_made
                red.reiniciar_partida()
            cid = resumen['id']
            detalles = red.crypta_details(cid)
            red.fijar_presupuesto(detalles['presupuesto_solicitudes'])
            guardador.crypta_details(cid, detalles)
            guardador.get_crypta_version(cid, {'version': detalles['version']})
            salas = []
            pagina = 1
            while True:
                datos = red.list_rooms(cid, pagina)
                guardador.list_rooms(cid, pagina, datos)
                salas.extend(s['id'] for s in datos['salas'])
                if pagina >= datos['total_paginas']:
                    break
                pagina += 1
            if (len(salas) != detalles['salas_total']
                    or any(sala in salas[:i] for i, sala in enumerate(salas))):
                raise ValueError(f'Esqueleto incompleto o con ids repetidos en {cid}')
            llaves = red.key_locations(cid)
            guardador.key_locations(cid, llaves)
            tipos = []
            _agregar_unicos(tipos, [x['id'] for x in llaves['llaves']])
            for i in range(0, len(salas), 10):
                lote = salas[i:i+10]
                contenido = red.room_content(cid, lote)
                if [e['sala'] for e in contenido['contenido']] != lote:
                    if any(s not in [e['sala'] for e in contenido['contenido']] for s in lote):
                        raise ValueError(f'Contenido incompleto en {cid}: {lote}')
                guardador.room_content(cid, lote, contenido)
                _agregar_unicos(tipos, CriptaService._tipos_de(contenido['contenido']))
                for entrada in contenido['contenido']:
                    for enemigo in entrada.get('enemigos', []):
                        _agregar_unicos(tipos, enemigo.get('suelta', []))
            resueltos = []
            while True:
                pendientes = [t for t in tipos if t not in resueltos]
                if not pendientes:
                    break
                lote = pendientes[:10]
                fichas = red.catalog(lote)
                if any(t not in [f['id'] for f in fichas['entidades']] for t in lote):
                    raise ValueError(f'Fichas incompletas en {cid}: {lote}')
                guardador.catalog(lote, fichas)
                _agregar_unicos(resueltos, lote)
                for ficha in fichas['entidades']:
                    _agregar_unicos(tipos, ficha.get('suelta', []))
            if red.get_crypta_version(cid)['version'] != detalles['version']:
                raise ValueError(f'La versión de {cid} cambió durante la descarga; repita la captura.')
            print(f"{cid}: {len(salas)} salas completas, {red.requests_made}/{detalles['presupuesto_solicitudes']} solicitudes", flush=True)
        if red.get_catalog_version() != catalogo_version:
            raise ValueError('El catálogo cambió durante la descarga; repita la captura.')
        total += red.requests_made
        Path(temporal).rename(destino)
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino', type=Path, default=RAIZ/'datos_entrega')
    args = parser.parse_args()
    configurar_registro_red(RAIZ/'partidas')
    print(f'Solicitudes totales: {descargar(args.destino)}')


if __name__ == '__main__':
    main()
