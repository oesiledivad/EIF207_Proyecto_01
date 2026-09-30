
from src.cripta.modelo.enemigo import Enemigo
from src.cripta.modelo.Tracker import Rastreador
from src.cripta.modelo.Guardian import Guardian
from src.cripta.modelo.Wandering import Errante
from src.cripta.dto.EnemigoDto import FichaEnemigo

@staticmethod
def ensamblarEnemigo(self,ficha):
        if isinstance(ficha, FichaEnemigo):
            comportamiento = FichaEnemigo.comportamiento
            if comportamiento == "guardian":
                return Guardian(
                    FichaEnemigo.id,
                    FichaEnemigo.vida,
                    FichaEnemigo.vida_max,
                    FichaEnemigo.ataque,
                    FichaEnemigo.defensa,
                    FichaEnemigo.velocidad,
                    FichaEnemigo.sala,
                    FichaEnemigo.tiempo_siguiente,
                    comportamiento
                )
            elif comportamiento == "errante":
                return Errante(
                    FichaEnemigo.id,
                    FichaEnemigo.vida,
                    FichaEnemigo.vida_max,
                    FichaEnemigo.ataque,
                    FichaEnemigo.defensa,
                    FichaEnemigo.velocidad,
                    FichaEnemigo.sala,
                    FichaEnemigo.tiempo_siguiente,
                    comportamiento
                )
            elif comportamiento == "rastreador":
                return Rastreador(
                    FichaEnemigo.id,
                    FichaEnemigo.vida,
                    FichaEnemigo.vida_max,
                    FichaEnemigo.ataque,
                    FichaEnemigo.defensa,
                    FichaEnemigo.velocidad,
                    FichaEnemigo.sala,
                    FichaEnemigo.tiempo_siguiente,
                    comportamiento
                )
            else:
                raise ValueError(f"Comportamiento desconocido: {comportamiento}")
        else:
            raise TypeError("El objeto proporcionado no es una instancia de FichaEnemigo")