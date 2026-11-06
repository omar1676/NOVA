"""
Prediccion de la demanda mensual de cada modelo (apartado 6.10).

Lo que se predice: los pares de demanda de un modelo en un mes (pedidos no
cancelados, el mismo criterio que la matriz modelo x mes de la fase 3).

Variables de entrada, todas conocidas ANTES de que empiece el mes que se predice:
  pares_mes_anterior     pares del modelo en el mes anterior (t-1)
  media_3_meses_previos  media de los meses t-1, t-2 y t-3
  mes_seno, mes_coseno   el mes del ano (1 a 12) como un punto de un circulo:
                         asi diciembre y enero quedan cerca, como en el calendario
  modelo_...             el modelo en columnas de 0 y 1 (one-hot): el numero de
                         un modelo es una etiqueta, no una cantidad
Los pares del propio mes, y los de los meses siguientes, nunca son una entrada.

Separacion por fecha, nunca al azar:
  historial      los 3 primeros meses: no tienen 3 meses previos, solo dan datos
  entrenamiento  los meses siguientes, hasta el anterior a la evaluacion
  evaluacion     los ultimos 3 meses (config.MESES_EVALUACION)

Dos metodos:
  A. baseline: el mes que viene se piden los mismos pares que este mes
  B. LinearRegression de scikit-learn, entrenada SOLO con los meses de entrenamiento

Evaluacion a un mes vista: para predecir septiembre ya se conoce agosto (ha
terminado), igual que lo sabria NOVA el 1 de septiembre. Los dos metodos usan
la misma informacion, y la regresion no se vuelve a entrenar con agosto.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

import config
from analiticas import de_demanda, no_calculable

VARIABLES = ["pares_mes_anterior", "media_3_meses_previos", "mes_seno", "mes_coseno"]


def demanda_mensual(lineas_enriquecidas, fecha_corte):
    """
    Pares de demanda de cada modelo en cada mes: una fila por modelo y mes.
    - Solo meses completos antes de la fecha de corte: un mes a medias
      pareceria una caida de la demanda.
    - Un modelo sin pedidos en un mes del periodo tiene 0 pares (es un recuento).
      Antes del primer mes con pedidos y despues del ultimo no se inventa ninguno.
    """
    demanda = de_demanda(lineas_enriquecidas)
    demanda = demanda[demanda["fecha_pedido"] < fecha_corte]
    demanda = demanda.assign(mes=demanda["fecha_pedido"].dt.to_period("M"))
    # El mes de la fecha de corte todavia no ha terminado
    demanda = demanda[demanda["mes"] < fecha_corte.to_period("M")]
    if len(demanda) == 0:
        return pd.DataFrame({"nombre_modelo": [], "mes": [], "pares": []})

    pares = demanda.groupby(["nombre_modelo", "mes"])["cantidad"].sum()
    meses = pd.period_range(demanda["mes"].min(), demanda["mes"].max(), freq="M")
    todas = pd.MultiIndex.from_product([sorted(demanda["nombre_modelo"].unique()), meses],
                                       names=["nombre_modelo", "mes"])
    return pares.reindex(todas, fill_value=0).reset_index(name="pares")


def anadir_variables(demanda):
    """
    Las variables de entrada de cada fila. shift(1) es "el mes anterior del
    mismo modelo": todas salen de meses anteriores, nunca del propio mes.
    """
    tabla = demanda.sort_values(["nombre_modelo", "mes"]).reset_index(drop=True)
    pares_del_modelo = tabla.groupby("nombre_modelo")["pares"]
    tabla["pares_mes_anterior"] = pares_del_modelo.shift(1)
    tabla["media_3_meses_previos"] = (pares_del_modelo.shift(1) + pares_del_modelo.shift(2)
                                      + pares_del_modelo.shift(3)) / 3
    tabla["numero_mes"] = tabla["mes"].dt.month
    tabla["mes_seno"] = np.sin(2 * np.pi * tabla["numero_mes"] / 12)
    tabla["mes_coseno"] = np.cos(2 * np.pi * tabla["numero_mes"] / 12)
    # drop_first: con las 12 columnas, una siempre se deduce de las otras 11 y
    # la regresion lineal no tendria una solucion unica. El primer modelo queda
    # como referencia (su efecto va en la constante).
    columnas_modelo = pd.get_dummies(tabla["nombre_modelo"], prefix="modelo", drop_first=True, dtype=int)
    return pd.concat([tabla, columnas_modelo], axis=1)


def separar_por_fecha(tabla):
    """Cada fila a su conjunto, segun su mes. Los ultimos meses son la evaluacion."""
    meses = sorted(tabla["mes"].unique())
    evaluacion = meses[-config.MESES_EVALUACION:]
    tabla = tabla.copy()
    tabla["conjunto"] = np.where(tabla["mes"].isin(evaluacion), "evaluacion",
                                 np.where(tabla["media_3_meses_previos"].isna(), "historial", "entrenamiento"))
    return tabla


def mae(real, prediccion):
    """Error absoluto medio: cuantos pares se equivoca de media, sin mirar si se pasa o se queda corto."""
    real = np.asarray(real, dtype=float)
    prediccion = np.asarray(prediccion, dtype=float)
    return float(np.mean(np.abs(real - prediccion)))


def rmse(real, prediccion):
    """Raiz del error cuadratico medio: como el MAE, pero un error grande pesa mucho mas que varios pequenos."""
    real = np.asarray(real, dtype=float)
    prediccion = np.asarray(prediccion, dtype=float)
    return float(np.sqrt(np.mean((real - prediccion) ** 2)))


def periodo(meses):
    """'2025-08 a 2026-07' (o '-' si no hay meses)."""
    meses = sorted(meses)
    return f"{meses[0]} a {meses[-1]}" if meses else "-"


def mejora(mae_regresion, rmse_regresion, mae_baseline, rmse_baseline):
    """Si la regresion mejora la referencia, dicho en palabras (los dos errores, menos es mejor)."""
    mejor_mae = mae_regresion < mae_baseline
    mejor_rmse = rmse_regresion < rmse_baseline
    if mejor_mae and mejor_rmse:
        return "sí: menos error en MAE y en RMSE"
    if not mejor_mae and not mejor_rmse:
        return "no: más error (o el mismo) en MAE y en RMSE"
    return "solo en una métrica: " + ("MAE sí, RMSE no" if mejor_mae else "RMSE sí, MAE no")


def predecir_demanda(lineas_enriquecidas, fecha_corte):
    """
    Construye la demanda mensual, entrena la regresion y compara los dos
    metodos en los meses de evaluacion. Devuelve un diccionario de tablas.
    Con menos de config.MINIMO_MESES_PREDICCION meses, todo es NO CALCULABLE
    salvo la propia demanda mensual (que es descriptiva).
    """
    demanda = demanda_mensual(lineas_enriquecidas, fecha_corte)
    meses = demanda["mes"].nunique()
    if meses < config.MINIMO_MESES_PREDICCION:
        motivo = (f"hay {meses} meses completos de demanda y hacen falta al menos "
                  f"{config.MINIMO_MESES_PREDICCION} (3 de historial, 6 o más de entrenamiento "
                  f"y {config.MESES_EVALUACION} de evaluación)")
        if meses == 0:
            tabla = no_calculable("no hay ningún mes completo de demanda antes de la fecha de corte")
        else:
            tabla = pd.DataFrame({"nombre_modelo": demanda["nombre_modelo"], "anio_mes": demanda["mes"].astype(str),
                                  "pares": demanda["pares"]})
        return {"demanda_mensual_modelo": tabla, "predicciones": no_calculable(motivo),
                "metricas_prediccion": no_calculable(motivo), "errores_por_modelo": no_calculable(motivo),
                "coeficientes_regresion": no_calculable(motivo)}

    tabla = separar_por_fecha(anadir_variables(demanda))
    columnas = VARIABLES + [c for c in tabla.columns if c.startswith("modelo_")]
    entrenamiento = tabla[tabla["conjunto"] == "entrenamiento"]
    evaluacion = tabla[tabla["conjunto"] == "evaluacion"]

    # B. Regresion lineal: sin hiperparametros que ajustar, asi nada se elige mirando la evaluacion
    regresion = LinearRegression().fit(entrenamiento[columnas], entrenamiento["pares"])

    predicciones = pd.DataFrame({
        "nombre_modelo": evaluacion["nombre_modelo"],
        "anio_mes": evaluacion["mes"].astype(str),
        "pares_reales": evaluacion["pares"],
        # A. Baseline: los pares del mes anterior, tal cual
        "baseline": evaluacion["pares_mes_anterior"],
        # Una recta puede dar pares negativos; no se pueden pedir menos de 0 pares
        "regresion": np.clip(regresion.predict(evaluacion[columnas]), 0, None).round(1),
    }).reset_index(drop=True)
    predicciones["error_baseline"] = predicciones["pares_reales"] - predicciones["baseline"]
    predicciones["error_regresion"] = (predicciones["pares_reales"] - predicciones["regresion"]).round(1)

    real = predicciones["pares_reales"]
    errores = {
        "baseline": (mae(real, predicciones["baseline"]), rmse(real, predicciones["baseline"])),
        "regresion": (mae(real, predicciones["regresion"]), rmse(real, predicciones["regresion"])),
    }
    metricas = pd.DataFrame([
        {"metodo": "baseline", "descripcion": "pares del mes anterior",
         "mae": round(errores["baseline"][0], 2), "rmse": round(errores["baseline"][1], 2),
         "mejora_al_baseline": "es la referencia"},
        {"metodo": "regresion", "descripcion": "LinearRegression: " + ", ".join(VARIABLES) + " y modelo one-hot",
         "mae": round(errores["regresion"][0], 2), "rmse": round(errores["regresion"][1], 2),
         "mejora_al_baseline": mejora(*errores["regresion"], *errores["baseline"])},
    ])
    metricas["filas_evaluacion"] = len(predicciones)
    metricas["periodo_entrenamiento"] = periodo(entrenamiento["mes"].astype(str).unique())
    metricas["periodo_evaluacion"] = periodo(evaluacion["mes"].astype(str).unique())
    metricas["filas_entrenamiento"] = len(entrenamiento)

    return {
        "demanda_mensual_modelo": pd.DataFrame({
            "nombre_modelo": tabla["nombre_modelo"], "anio_mes": tabla["mes"].astype(str),
            "pares": tabla["pares"], "pares_mes_anterior": tabla["pares_mes_anterior"],
            "media_3_meses_previos": tabla["media_3_meses_previos"].round(2),
            "numero_mes": tabla["numero_mes"], "conjunto": tabla["conjunto"]}),
        "predicciones": predicciones,
        "metricas_prediccion": metricas,
        "errores_por_modelo": errores_por_modelo(predicciones),
        "coeficientes_regresion": pd.DataFrame({
            "variable": ["constante"] + columnas,
            "coeficiente": [round(float(regresion.intercept_), 3)] + [round(float(c), 3) for c in regresion.coef_],
        }),
    }


def errores_por_modelo(predicciones):
    """MAE y RMSE de cada metodo para cada modelo de zapatilla, y cual se equivoca menos (por MAE)."""
    filas = []
    for nombre, grupo in predicciones.groupby("nombre_modelo"):
        real = grupo["pares_reales"]
        mae_baseline = mae(real, grupo["baseline"])
        mae_regresion = mae(real, grupo["regresion"])
        filas.append({
            "nombre_modelo": nombre,
            "pares_reales_evaluacion": int(real.sum()),
            "mae_baseline": round(mae_baseline, 2),
            "rmse_baseline": round(rmse(real, grupo["baseline"]), 2),
            "mae_regresion": round(mae_regresion, 2),
            "rmse_regresion": round(rmse(real, grupo["regresion"]), 2),
            "menos_error": ("regresion" if mae_regresion < mae_baseline
                            else "baseline" if mae_baseline < mae_regresion else "empate"),
        })
    return pd.DataFrame(filas).sort_values("pares_reales_evaluacion", ascending=False).reset_index(drop=True)
