"""
# ============================================================
# SALAS
# ============================================================

datos = get(f"/criptas/{dungeon_id}/salas?pagina=2")

if datos is not None:
    print("\n=== SALAS ===")

    for sala in datos["salas"]:
        print(f"\nSala {sala['id']}: {sala['nombre']}")

        for direccion, salida in sala["salidas"].items():
            texto = f"  {direccion} -> Sala {salida['sala']}"

            if salida.get("cerrada"):
                texto += f" | CERRADA | Llave: {salida.get('llave')}"

            if salida.get("cierre_automatico") is not None:
                texto += (
                    f" | Cierre automático: "
                    f"{salida['cierre_automatico']}"
                )

            print(texto)


"""