# Evidencias del dashboard (fase 6)

Capturas del 9 de noviembre de 2026 (las `refresco_*`, repetidas el 10 de noviembre con el código final), hechas con **Microsoft Edge** (modo sin
ventana, controlado con Playwright desde una carpeta temporal; Playwright no es
una dependencia del proyecto). La aplicación es `app_dashboard.py`, servida con
`streamlit run` en `localhost`.

- **Tamaños:** escritorio de 1440 px de ancho; móvil de 390 × 844, con
  `is_mobile` y pantalla táctil.
- **Cómo se abrió cada vista:** con su dirección, por ejemplo
  `?origen=Sintéticos+limpios&pestana=Clientes`.
- **Qué se comprobó en cada captura:**
  - que la pestaña seleccionada fuese la pedida;
  - que no hubiera ninguna excepción de Streamlit;
  - que no hubiera errores de JavaScript.

  En las 37 capturas que se hicieron, todo estaba bien.

| Archivo | Qué muestra |
|---|---|
| `escritorio_sint_1_direccion.png` … `escritorio_sint_6_prediccion.png` | las seis pestañas con los datos SINTÉTICOS limpios |
| `escritorio_sint_1_direccion_filtrada.png` | cuatro filtros elegidos en la barra lateral, con clics: modelo SINT Runner, talla 42, Custom y entregado. Resultado: 31 de 900 pedidos, 370 pares y 56.133,71 € confirmados, las mismas cifras que `filtros.calcular_filtrado` en la consola |
| `escritorio_acc_1_direccion.png` … `escritorio_acc_6_prediccion.png` | las seis pestañas con la exportación de PRUEBA de Acceso a Datos. RFM, KMeans y la predicción salen como NO CALCULABLE; la conciliación da 28 de 28 cifras iguales a SQL |
| `escritorio_errores_1_direccion.png` | los sintéticos con errores: «Datos inválidos» y ninguna cifra publicada |
| `escritorio_errores_5_calidad.png` | su pestaña Calidad: BLOQUEADO; 3 bloqueantes, 14 recuperables y 4 advertencias; tablas y columnas afectadas; filas rechazadas y registro |
| `movil_sint_1_direccion.png` … `movil_sint_6_prediccion.png` | las seis pestañas en el móvil: las columnas se apilan y las pestañas se desplazan |
| `movil_errores_1_direccion.png` | el bloqueo en el móvil |
| `refresco_1_sin_cambios.png` | R5: tras 60 s sin tocar nada, «Sin cambios». Cambia la hora de comprobación y las cifras no cambian |
| `refresco_2_pedido_nuevo.png` | R1: a los 60 s de exportar un pedido de 2 líneas, se pasa de 12 a 13 pedidos y de 4.796,00 € a 5.035,97 € |
| `refresco_3_csv_ausente.png` | R4: sin `pedidos.csv`, «Error de carga», el aviso y ninguna cifra |
| `refresco_3b_desactualizado.png` | el último resultado válido, que solo se ve si se pide, rotulado DESACTUALIZADO con su hora |
| `refresco_4_recuperacion.png` | se vuelve a exportar `pedidos.csv` y, a los 60 s, vuelven las cifras |
| `caso_k_0_carga_inicial.png` … `caso_k_3_ciclo_3.png` | caso K (13/11, versión candidata): el dashboard abierto durante tres ciclos de 60 s con la exportación de PRUEBA, sin tocar el navegador. Cambia la hora de comprobación en cada ciclo, el estado es «Sin cambios» y las cifras no cambian. El registro de la sesión está en `caso_k_registro.txt` |

Las capturas `refresco_*` se hicieron con una COPIA de `entrada_acc/` en una
carpeta temporal: los CSV originales de Acceso a Datos no se tocaron. El
navegador no recargó ni pulsó nada entre un paso y otro; solo esperó a que el
fragmento de 60 s se ejecutara solo.

El detalle está en `../../dashboard.md`.
