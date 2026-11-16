"""Pruebas del modelo de resolubilidad (historia US1).

Cada prueba arma su propio esqueleto mínimo con ids genéricos: ningún dato
de una cripta concreta vive aquí (FR-029).
"""
import copy
import inspect
import unittest

from cripta.dto.Partida_dto import DetallesCripta, SalaModelo, SalidaVecina
from cripta.dto.Verificacion_dto import UbicacionLlave
from cripta.estructuras.Ordenamientos import ordenar
from cripta.modelo import Resolubilidad
from cripta.modelo.Resolubilidad import verificar


def salida(direccion: str, destino: int, llave: str = "", cierre: int | None = None) -> SalidaVecina:
    """Arma una salida; con `llave` queda cerrada."""
    return SalidaVecina(
        direccion=direccion, sala_id=destino, nombre="", cerrada=bool(llave), llave=llave,
        transitable=True, es_salida_final=False, tiene_enemigos=False, tiene_objetos=False,
        cierre_automatico=cierre,
    )


def sala(id_: int, *salidas: SalidaVecina) -> SalaModelo:
    """Arma una sala con las salidas dadas."""
    return SalaModelo(id=id_, nombre=f"s{id_}", descripcion="", salidas=list(salidas))


def detalles(inicial: int, destino: int, llave_salida: str) -> DetallesCripta:
    """Arma los parámetros de la cripta que usa el modelo."""
    return DetallesCripta(
        id="prueba", version="v1", salas_total=0, sala_inicial=inicial, sala_salida=destino,
        llave_salida=llave_salida, inventario_max=10, presupuesto_solicitudes=0,
        jugador_vida_max=30, jugador_ataque=6, jugador_defensa=2, jugador_velocidad=100,
    )


def ubic(llave: str, sala_id: int, enemigo: str | None = None) -> UbicacionLlave:
    return UbicacionLlave(llave=llave, sala=sala_id, enemigo=enemigo)


def resumen(resultado) -> list[tuple]:
    """Orden de llaves como tuplas comparables."""
    return [(o.llave, o.sala, o.enemigo, o.ronda) for o in resultado.orden_llaves]


def nombres(resultado) -> list[str]:
    return [o.llave for o in resultado.orden_llaves]


class PruebasResolubilidad(unittest.TestCase):
    def test_us1_1_unica_llave_salida(self):
        """FR-006, FR-007: una sola llave de salida alcanzable; el orden es solo ella."""
        salas = [
            sala(1, salida("E", 2)),
            sala(2, salida("N", 3, "LS")),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(nombres(r), ["LS"])

    def test_us1_2_llaves_encadenadas(self):
        """FR-007: tres llaves encadenadas; cada una va tras las necesarias e incluye la de salida."""
        salas = [
            sala(1, salida("E", 2, "A")),
            sala(2, salida("E", 3, "B")),
            sala(3, salida("E", 4, "C")),
            sala(4),
        ]
        ubicaciones = [ubic("C", 3), ubic("B", 2), ubic("A", 1)]
        r = verificar(detalles(1, 4, "C"), salas, ubicaciones)
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(nombres(r), ["A", "B", "C"])
        self.assertEqual([o.ronda for o in r.orden_llaves], [0, 1, 2])

    def test_us1_3_llave_innecesaria_incluida(self):
        """FR-007: una llave obtenible que no hace falta para ganar aparece en el orden."""
        salas = [
            sala(1, salida("E", 2), salida("N", 3, "LS")),
            sala(2),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 1), ubic("EXTRA", 2)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(sorted_copia(nombres(r)), ["EXTRA", "LS"])

    def test_us1_4_apendice_b_orden_determinista(self):
        """FR-008: varios órdenes válidos; ejecuciones repetidas y entradas permutadas dan lo mismo."""
        def armar(invertir: bool):
            salas = [
                sala(1, salida("E", 2), salida("N", 3)),
                sala(2, salida("E", 4)),
                sala(3, salida("N", 5, "S")),
                sala(4),
                sala(5),
            ]
            ubicaciones = [ubic("Z", 2), ubic("A", 3), ubic("S", 4)]
            if invertir:
                salas.reverse()
                for s in salas:
                    s.salidas.reverse()
                ubicaciones.reverse()
            return salas, ubicaciones

        salas, ubicaciones = armar(False)
        primero = verificar(detalles(1, 5, "S"), salas, ubicaciones)
        segundo = verificar(detalles(1, 5, "S"), salas, ubicaciones)
        permutado = verificar(detalles(1, 5, "S"), *armar(True))
        self.assertEqual(primero.estado, "resoluble")
        # Misma ronda: gana la ubicación de menor id de sala, no la llave de menor id.
        self.assertEqual(nombres(primero), ["Z", "A", "S"])
        self.assertEqual(resumen(primero), resumen(segundo))
        self.assertEqual(resumen(primero), resumen(permutado))

    def test_us1_5_apendice_b_llave_de_enemigo_errante(self):
        """FR-002, FR-004: la llave de un enemigo se ubica en la sala publicada y se reporta con su enemigo."""
        salas = [
            sala(1, salida("E", 2)),
            sala(2, salida("N", 3, "LS")),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2, "enemigo_1")])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(resumen(r), [("LS", 2, "enemigo_1", 1)])

    def test_borde_llave_salida_en_sala_inicial(self):
        """FR-006, FR-007: llave de salida en la sala inicial; ronda 0 y entra con las demás."""
        salas = [
            sala(1, salida("E", 2, "LS")),
            sala(2),
        ]
        r = verificar(detalles(1, 2, "LS"), salas, [ubic("X", 1), ubic("LS", 1)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(resumen(r), [("LS", 1, None, 0), ("X", 1, None, 0)])

    def test_borde_llave_que_no_llega_a_la_sala_de_salida(self):
        """FR-006: la llave de salida se obtiene pero ninguna puerta con ella llega a la sala de salida."""
        salas = [
            sala(1, salida("E", 3, "LS")),
            sala(2),
            sala(3),
        ]
        r = verificar(detalles(1, 2, "LS"), salas, [ubic("LS", 1)])
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual(r.reporte.motivo, "puerta_sin_destino")
        self.assertEqual(r.orden_llaves, [])

    def test_borde_llave_de_salida_inobtenible(self):
        """FR-006: si la llave de salida no se obtiene, el motivo es la llave inobtenible."""
        salas = [
            sala(1, salida("E", 2, "A")),
            sala(2, salida("E", 3, "LS")),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2), ubic("A", 3)])
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual(r.reporte.motivo, "llave_salida_inobtenible")

    def test_borde_varias_puertas_con_la_misma_llave(self):
        """FR-007: todas las puertas que exigen la misma llave se abren al obtenerla."""
        salas = [
            sala(1, salida("E", 2, "K"), salida("N", 3, "K")),
            sala(2),
            sala(3, salida("N", 4, "LS")),
            sala(4),
        ]
        ubicaciones = [ubic("K", 1), ubic("X", 2), ubic("LS", 3)]
        r = verificar(detalles(1, 4, "LS"), salas, ubicaciones)
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(sorted_copia(nombres(r)), ["K", "LS", "X"])

    def test_borde_llave_de_region_exige_otra_llave(self):
        """FR-003, FR-007: una llave tras una puerta aparece después de la que la abre."""
        salas = [
            sala(1, salida("E", 2, "A")),
            sala(2, salida("E", 3, "LS")),
            sala(3),
        ]
        ubicaciones = [ubic("LS", 2), ubic("A", 1)]
        r = verificar(detalles(1, 3, "LS"), salas, ubicaciones)
        self.assertEqual(nombres(r), ["A", "LS"])

    def test_borde_llave_inobtenible_no_aparece(self):
        """FR-007: en una cripta resoluble, una llave que no se puede obtener no entra al orden."""
        salas = [
            sala(1, salida("N", 2, "LS")),
            sala(2),
            sala(9),
        ]
        r = verificar(detalles(1, 2, "LS"), salas, [ubic("LS", 1), ubic("PERDIDA", 9)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(nombres(r), ["LS"])

    def test_trampas_y_cierres_no_bloquean(self):
        """FR-005: `cierre_automatico` no cambia el veredicto ni el orden."""
        def armar(cierre):
            salas = [
                sala(1, salida("E", 2, cierre=cierre)),
                sala(2, salida("N", 3, "LS", cierre=cierre)),
                sala(3),
            ]
            return verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2)])

        sin = armar(None)
        con = armar(3)
        self.assertEqual(con.estado, "resoluble")
        self.assertEqual(resumen(con), resumen(sin))

    def test_salidas_dirigidas(self):
        """FR-003: una puerta cerrada en un solo lado no se infiere en el lado contrario."""
        salas = [
            sala(1, salida("E", 2)),
            sala(2, salida("O", 1, "K"), salida("N", 3, "LS")),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2), ubic("K", 3)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(nombres(r), ["LS", "K"])

    def test_llave_con_varias_ubicaciones(self):
        """FR-002, FR-008: se obtiene en la ubicación alcanzada primero y, con empate, en la de menor sala."""
        # La sala 3 se alcanza antes que la 5.
        salas = [
            sala(1, salida("E", 3), salida("N", 6, "S")),
            sala(3, salida("E", 5)),
            sala(5),
            sala(6),
        ]
        r = verificar(detalles(1, 6, "S"), salas, [ubic("S", 5), ubic("S", 3)])
        self.assertEqual(resumen(r), [("S", 3, None, 1)])

        # Empate de ronda entre las salas 4 y 2: gana la de menor id.
        salas = [
            sala(1, salida("E", 4), salida("N", 2), salida("S", 6, "S")),
            sala(2),
            sala(4),
            sala(6),
        ]
        r = verificar(detalles(1, 6, "S"), salas, [ubic("S", 4), ubic("S", 2)])
        self.assertEqual(resumen(r), [("S", 2, None, 1)])

    def test_no_modifica_entradas_ni_contiene_datos_de_cripta(self):
        """FR-027, FR-029: las entradas no cambian y el modelo no contiene ids de una cripta."""
        salas = [
            sala(2, salida("E", 3, "B"), salida("O", 1)),
            sala(1, salida("E", 2, "A")),
            sala(3),
        ]
        ubicaciones = [ubic("B", 2), ubic("A", 1), ubic("A", 3)]
        copia_salas = copy.deepcopy(salas)
        copia_ubicaciones = copy.deepcopy(ubicaciones)
        verificar(detalles(1, 3, "B"), salas, ubicaciones)
        self.assertEqual(salas, copia_salas)
        self.assertEqual(ubicaciones, copia_ubicaciones)

        with open(inspect.getsourcefile(Resolubilidad), encoding="utf-8") as archivo:
            texto = archivo.read()
        self.assertNotIn("cripta-", texto)
        self.assertNotIn("itm_llave", texto)

    def test_estadisticas_de_la_exploracion(self):
        """FR-024: cada sala se encola una vez y cada salida se examina una vez."""
        salas = [
            sala(1, salida("E", 2), salida("N", 3, "A")),
            sala(2, salida("O", 1), salida("E", 3, "A")),
            sala(3, salida("E", 4, "LS")),
            sala(4),
            sala(7, salida("E", 1)),   # no alcanzable: no se examina
        ]
        r = verificar(detalles(1, 4, "LS"), salas, [ubic("A", 2), ubic("LS", 3)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(r.estadisticas.salas_encoladas, 4)
        self.assertEqual(r.estadisticas.salidas_examinadas, 5)
        self.assertEqual(r.estadisticas.llaves_obtenidas, 2)

    def test_datos_invalidos_no_son_verificables(self):
        """FR-001, FR-022: sala inicial inexistente o salida cerrada sin llave no dan veredicto."""
        r = verificar(detalles(9, 2, "LS"), [sala(1), sala(2)], [])
        self.assertEqual(r.estado, "no_verificable")
        self.assertTrue(r.motivo_no_verificable)
        self.assertIsNone(r.estadisticas)

        sin_llave = SalidaVecina(
            direccion="E", sala_id=2, nombre="", cerrada=True, llave="", transitable=True,
            es_salida_final=False, tiene_enemigos=False, tiene_objetos=False,
        )
        r = verificar(detalles(1, 2, "LS"), [sala(1, sin_llave), sala(2)], [])
        self.assertEqual(r.estado, "no_verificable")
        self.assertTrue(r.motivo_no_verificable)

    def test_salida_a_sala_inexistente_se_ignora_con_aviso(self):
        """FR-001: una salida a una sala que no existe se ignora y deja una advertencia."""
        salas = [
            sala(1, salida("E", 2), salida("N", 99)),
            sala(2, salida("N", 3, "LS")),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(len(r.advertencias), 1)

    def test_sala_duplicada_gana_la_primera(self):
        """FR-001: con una sala repetida se usa la primera y la segunda se descarta."""
        salas = [
            sala(1, salida("E", 2)),
            sala(2, salida("N", 3, "LS")),
            sala(2),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2)])
        self.assertEqual(r.estado, "resoluble")

    def test_ubicacion_en_sala_inexistente_se_descarta(self):
        """FR-002: una ubicación en una sala que no existe se descarta con advertencia."""
        salas = [sala(1, salida("N", 2, "LS")), sala(2)]
        r = verificar(detalles(1, 2, "LS"), salas, [ubic("LS", 1), ubic("FUERA", 77)])
        self.assertEqual(r.estado, "resoluble")
        self.assertEqual(nombres(r), ["LS"])
        self.assertEqual(len(r.advertencias), 1)


def puerta_tupla(p) -> tuple:
    """Puerta bloqueada como tupla comparable."""
    return (p.sala_origen, p.direccion, p.sala_destino, p.llave)


def ciclos_resumen(resultado) -> list[list[tuple]]:
    """Ciclos del reporte como listas de (llave, sala, enemigo, puerta)."""
    return [
        [(p.llave, p.sala, p.enemigo, puerta_tupla(p.puerta)) for p in c.pasos]
        for c in resultado.reporte.ciclos
    ]


def bloqueada(resultado, llave: str):
    """Entrada de `llaves_inobtenibles` de una llave, o None."""
    for b in resultado.reporte.llaves_inobtenibles:
        if b.llave == llave:
            return b
    return None


class PruebasReporteBloqueo(unittest.TestCase):
    """Pruebas del reporte de bloqueo (historia US2)."""

    def test_us2_1_apendice_b_ciclo_de_llave_salida(self):
        """FR-012: llave_salida tras la unica puerta que ella abre; ciclo de longitud 1."""
        salas = [
            sala(1, salida("E", 2, "LS")),
            sala(2, salida("N", 3, "LS")),
            sala(3),
        ]
        r = verificar(detalles(1, 3, "LS"), salas, [ubic("LS", 2)])
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual(r.reporte.motivo, "llave_salida_inobtenible")
        self.assertEqual(ciclos_resumen(r), [[("LS", 2, None, (1, "E", 2, "LS"))]])
        self.assertEqual(bloqueada(r, "LS").causa, "en_ciclo")

    def test_us2_2_ciclo_de_dos_llaves(self):
        """FR-012: A tras una puerta que exige B y B tras una puerta que exige A."""
        salas = [
            sala(1, salida("E", 2, "B"), salida("N", 3, "A"), salida("S", 4, "A")),
            sala(2), sala(3), sala(4),
        ]
        r = verificar(detalles(1, 4, "A"), salas, [ubic("A", 2), ubic("B", 3)])
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual(ciclos_resumen(r), [[
            ("A", 2, None, (1, "E", 2, "B")),
            ("B", 3, None, (1, "N", 3, "A")),
        ]])

    def test_us2_3_reporte_completo(self):
        """FR-009, FR-010, FR-011: llaves inobtenibles, frontera, y sala y enemigo de cada llave."""
        salas = [
            sala(1, salida("E", 2, "B"), salida("N", 3, "A"), salida("S", 6, "A")),
            sala(2, salida("S", 5)),
            sala(3), sala(5), sala(6),
        ]
        ubicaciones = [ubic("A", 2), ubic("B", 3), ubic("C", 5, "en1")]
        r = verificar(detalles(1, 6, "A"), salas, ubicaciones)
        self.assertEqual(r.estado, "no_resoluble")
        rep = r.reporte
        self.assertEqual([b.llave for b in rep.llaves_inobtenibles], ["A", "B", "C"])
        self.assertEqual([puerta_tupla(p) for p in rep.frontera], [
            (1, "N", 3, "A"), (1, "S", 6, "A"), (1, "E", 2, "B"),
        ])
        c = bloqueada(r, "C")
        self.assertEqual([(u.sala, u.enemigo) for u in c.ubicaciones], [(5, "en1")])
        self.assertEqual(c.causa, "depende_de")
        self.assertEqual(c.depende_de, "B")
        self.assertEqual(bloqueada(r, "A").causa, "en_ciclo")

    def test_us2_4_ciclo_determinista(self):
        """FR-013: repetir y permutar las entradas da el mismo ciclo, inicio y sentido."""
        def armar(invertir: bool):
            salas = [
                sala(1, salida("E", 2, "B"), salida("N", 3, "A"), salida("S", 4, "A")),
                sala(2), sala(3), sala(4),
            ]
            ubicaciones = [ubic("A", 2), ubic("B", 3)]
            if invertir:
                salas.reverse()
                for s in salas:
                    s.salidas.reverse()
                ubicaciones.reverse()
            return salas, ubicaciones

        salas, ubicaciones = armar(False)
        primero = verificar(detalles(1, 4, "A"), salas, ubicaciones)
        segundo = verificar(detalles(1, 4, "A"), salas, ubicaciones)
        permutado = verificar(detalles(1, 4, "A"), *armar(True))
        self.assertEqual(ciclos_resumen(primero), ciclos_resumen(segundo))
        self.assertEqual(ciclos_resumen(primero), ciclos_resumen(permutado))
        self.assertEqual(primero.reporte.ciclos[0].pasos[0].llave, "A")

    def test_us2_5_varios_ciclos_ordenados(self):
        """FR-012, FR-013: ciclos disjuntos, cada uno desde su llave menor y ordenados por ella."""
        salas = [
            sala(1, salida("E", 2, "D"), salida("W", 3, "C"), salida("N", 4, "B"),
                 salida("S", 5, "A"), salida("U", 6)),
            sala(2), sala(3), sala(4), sala(5), sala(6), sala(7),
        ]
        # C y D en las salas bajas, A y B en las altas: el orden sale de las llaves, no de las salas.
        ubicaciones = [ubic("C", 2), ubic("D", 3), ubic("A", 4), ubic("B", 5)]
        r = verificar(detalles(1, 7, "A"), salas, ubicaciones)
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual([[p.llave for p in c.pasos] for c in r.reporte.ciclos], [["A", "B"], ["C", "D"]])

    def test_borde_llave_sin_ubicacion(self):
        """FR-011: una llave que una puerta exige y nadie publica queda con causa sin_ubicacion."""
        salas = [sala(1, salida("E", 2, "X")), sala(2)]
        r = verificar(detalles(1, 2, "X"), salas, [])
        self.assertEqual(r.estado, "no_resoluble")
        x = bloqueada(r, "X")
        self.assertEqual(x.causa, "sin_ubicacion")
        self.assertEqual(x.ubicaciones, [])
        self.assertEqual(r.reporte.ciclos, [])

    def test_borde_varias_ubicaciones_desconectadas(self):
        """FR-011: con varias ubicaciones y ninguna alcanzable se listan todas."""
        salas = [sala(1, salida("E", 2, "X")), sala(2), sala(8), sala(9)]
        r = verificar(detalles(1, 2, "X"), salas, [ubic("X", 9), ubic("X", 8, "en2")])
        x = bloqueada(r, "X")
        self.assertEqual(x.causa, "sala_desconectada")
        self.assertEqual([(u.sala, u.enemigo) for u in x.ubicaciones], [(8, "en2"), (9, None)])

    def test_borde_ubicacion_invalida(self):
        """FR-011: una llave publicada solo en una sala inexistente queda con causa ubicacion_invalida."""
        salas = [sala(1, salida("E", 2, "X")), sala(2)]
        r = verificar(detalles(1, 2, "X"), salas, [ubic("X", 77)])
        x = bloqueada(r, "X")
        self.assertEqual(x.causa, "ubicacion_invalida")
        self.assertEqual([u.sala for u in x.ubicaciones], [77])

    def test_borde_alternativas_no_generan_ciclo_aparte(self):
        """FR-012: A tras puertas de B y C; se reporta el ciclo A, B y no A, C aparte (research D6)."""
        salas = [
            sala(1, salida("E", 2, "B"), salida("N", 2, "C")),
            sala(2, salida("E", 3, "A"), salida("N", 4, "A")),
            sala(3), sala(4), sala(5),
        ]
        r = verificar(detalles(1, 5, "A"), salas, [ubic("A", 2), ubic("B", 3), ubic("C", 4)])
        self.assertEqual(r.estado, "no_resoluble")
        self.assertEqual(ciclos_resumen(r), [[
            ("A", 2, None, (1, "E", 2, "B")),
            ("B", 3, None, (2, "E", 3, "A")),
        ]])
        c = bloqueada(r, "C")
        self.assertEqual(c.causa, "depende_de")
        self.assertEqual(c.depende_de, "A")

    def test_reporte_misma_exploracion(self):
        """FR-025, FR-024: con K llaves encadenadas y bloqueo al final no se explora por llave."""
        k = 20
        salas = []
        ubicaciones = []
        for j in range(1, k + 1):
            salas.append(sala(j, salida("E", j + 1, f"K{j:02d}")))
            ubicaciones.append(ubic(f"K{j:02d}", j))
        salas.append(sala(k + 1, salida("E", k + 2, "LS")))
        salas.append(sala(k + 2))
        r = verificar(detalles(1, k + 2, "LS"), salas, ubicaciones)
        self.assertEqual(r.estado, "no_resoluble")
        total_salidas = k + 1
        self.assertEqual(r.estadisticas.salidas_examinadas, total_salidas)
        self.assertLess(r.estadisticas.salidas_examinadas, k * total_salidas)
        self.assertEqual(r.estadisticas.salas_encoladas, k + 2)


def sorted_copia(valores: list[str]) -> list[str]:
    """Copia ordenada de ids de prueba (solo para comparar en las pruebas)."""
    return ordenar(list(valores))


if __name__ == "__main__":
    unittest.main()
