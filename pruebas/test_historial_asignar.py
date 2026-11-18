"""Historial: cambio invertible `lista_asignada` y reversión de `lista_agregada`."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cripta.controlador.GestorPartida import GestorPartida
from cripta.estructuras.Historial_Retroceso import Historial_Retroceso


def _revertir(historial: Historial_Retroceso) -> None:
    """Invierte el intervalo abierto con la lógica de producción."""
    gestor = GestorPartida.__new__(GestorPartida)
    historial.revertir_abierto(gestor._aplicar_reversion)


class PruebasHistorialAsignar(unittest.TestCase):
    def test_asignar_registra_y_revierte_la_posicion(self):
        """FR-016: asignar registra la posición y el retroceso la restaura."""
        h = Historial_Retroceso()
        lista = [0, 0, 0]
        h.abrir_intervalo()
        h.asignar(lista, 1, 2)
        self.assertEqual(lista, [0, 2, 0])
        _revertir(h)
        self.assertEqual(lista, [0, 0, 0])

    def test_mismo_valor_no_registra(self):
        """FR-037: asignar el mismo valor no deja cambios en el intervalo."""
        h = Historial_Retroceso()
        lista = [5, 6]
        h.abrir_intervalo()
        h.asignar(lista, 0, 5)
        self.assertEqual(len(h._abierto.cambios), 0)

    def test_varias_asignaciones_en_orden_inverso(self):
        """FR-016: varias asignaciones a la misma posición se revierten en orden inverso."""
        h = Historial_Retroceso()
        lista = [1, 1]
        h.abrir_intervalo()
        h.asignar(lista, 0, 2)
        h.asignar(lista, 1, 2)
        h.asignar(lista, 0, 0)
        self.assertEqual(lista, [0, 2])
        _revertir(h)
        self.assertEqual(lista, [1, 1])

    def test_lista_agregada_se_revierte_quitando_el_ultimo(self):
        """FR-037: `lista_agregada` se invierte con pop() del final, sin alterar el orden."""
        grande = list(range(10000))
        copia = list(grande)
        h = Historial_Retroceso()
        h.abrir_intervalo()
        h.agregar(grande, 10000)
        h.agregar(grande, 10001)
        self.assertEqual(len(grande), 10002)
        _revertir(h)
        self.assertEqual(grande, copia)

    def test_lista_agregada_no_recorre_la_lista(self):
        """FR-037: el retroceso del último elemento agregado no compara con los demás."""
        class Contador:
            comparaciones = 0

            def __eq__(self, otro):
                Contador.comparaciones += 1
                return self is otro

            __hash__ = object.__hash__

        lista = [Contador() for _ in range(10000)]
        h = Historial_Retroceso()
        nuevo = Contador()
        h.abrir_intervalo()
        h.agregar(lista, nuevo)
        Contador.comparaciones = 0
        _revertir(h)
        self.assertEqual(len(lista), 10000)
        self.assertEqual(Contador.comparaciones, 0)

    def test_cambios_existentes_siguen_funcionando(self):
        """FR-016: `atributo`, `lista_agregada` y `lista_quitada` no cambian."""
        class Objeto:
            valor = 1

        o = Objeto()
        lista = ["a", "b", "c"]
        h = Historial_Retroceso()
        h.abrir_intervalo()
        h.cambiar(o, "valor", 9)
        h.quitar(lista, "b")
        h.agregar(lista, "z")
        _revertir(h)
        self.assertEqual(o.valor, 1)
        self.assertEqual(lista, ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
