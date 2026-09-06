import pandas as pd
from datetime import datetime
import numpy as np


def crearDfCliente(df_cli):

    df_cli =df_cli.copy()
    
    columnas_group_cli = [
        "HPH ADU-PAT-PED-HTS-SEC"
    ]

    detalle_umc_cli = (
        df_cli.groupby(
            columnas_group_cli + ["UM NORMALIZADA"],
            as_index=False
        )["CANT_UMC_NEW"]
        .sum()
    )

    detalle_umc_cli = (
        detalle_umc_cli.groupby(columnas_group_cli, as_index=False)
        .agg({
            "CANT_UMC_NEW": lambda x: " & ".join(x.astype(str))
        })
        .rename(columns={"CANT_UMC_NEW": "CANT_UMC_NEW_DETALLE"})
    )

    df_cli_group = (
        df_cli.groupby(columnas_group_cli, as_index=False)
        .agg({
            "VALOR EN DOLARES": "sum",
            "CANT_UMC_NEW": "sum",
            "UM NORMALIZADA": lambda x: " & ".join(dict.fromkeys(x.astype(str)))
        })
    )

    df_cli_group = df_cli_group.merge(
        detalle_umc_cli,
        on=columnas_group_cli,
        how="left"
    )
    
    return df_cli_group


def crearDfDS(df_ds):

    df_ds = df_ds.copy()


    df_ds["DS PAT-PED"] = (
        df_ds["ADU-PAT-PED"]
        .str.split("-", n=1)
        .str[1]
    )

    df_ds["DS PAT-PED-HTS"] = (
        df_ds["ADU-PAT-PED-HTS"]
        .str.split("-", n=1)
        .str[1]
    )


    return df_ds


def crearDfDSGroup(df_ds):

    df_ds=df_ds.copy()
    
    columnas_group = [
        "DS PAT-PED",
        "DS PAT-PED-HTS",
        "ADU-PAT-PED",
        "ADU-PAT-PED-HTS-SEC",
        "CLAVE PED",
        "FECHA PAGO 551"
    ]

    detalle_umc = (
        df_ds.groupby(
            columnas_group + ["UM NORMALIZADA"],
            as_index=False
        )["CANT_UMC_NEW"]
        .sum()
    )

    detalle_umc = (
        detalle_umc.groupby(columnas_group, as_index=False)
        .agg({
            "CANT_UMC_NEW": lambda x: " & ".join(x.astype(str))
        })
        .rename(columns={"CANT_UMC_NEW": "CANT_UMC_NEW_DETALLE"})
    )

    df_ds_group = (
        df_ds.groupby(columnas_group, as_index=False)
        .agg({
            "VAL USD": "sum",
            "CANT_UMC_NEW": "sum",
            "UM NORMALIZADA": lambda x: " & ".join(dict.fromkeys(x.astype(str)))
        })
    )

    df_ds_group = df_ds_group.merge(
        detalle_umc,
        on=columnas_group,
        how="left"
    )

    return df_ds_group


def extraerDSCrossxPedMerge(df_ds_group, df_ped):
    
    # ruta= r"C:/Users/User/OneDrive/Proyecto/PYTHON/Proyecto HPH/CROSS X/outputs/"
    # df_ped = utils.leer_csv(ruta + "CROSS X PED.csv")
    
    df_ds_group=df_ds_group.copy()
    df_ped=df_ped.copy()
    
    df_ped = df_ped[
        [
            "DS ADU-PAT-PED",
            "CLAVES IMMEX",
            "FECHA PAGO",
            "FECHA ENTRADA O PRESENTACIÓN",
            "ID AF?",
            "TIPO Y CLAVE",
            "SI EL PEDIMENTO DE LA COLUMNA 'T' ES R1, A QUIEN RECTIFICÓ?",
            "ESTATUS DEL PEDIMENTO A QUIEN RECTIFICO DE LA COLUMNA 'F'?",
            "SI EL PEDIMENTO DE LA COLUMNA 'T' TUVO R1, CUÁL FUE EL NÚMERO DE R1?",
            "ESTATUS DEL PEDIMENTO R1 DE LA COLUMNA H",
            "ESTIMACIÓN APROX DE IGI  6 FP 0",
            "ESTIMACIÓN APROX DE IGI 6 FP 5",
            "ESTIMACIÓN APROX DE IGI 6 FP 6",
            "SI EL PEDIMENTO DE LA COLUMNA 'T' ES DESCARGA ESPECIFICA, A QUIÉN DESCARGO?",
            "SI EL PEDIMENTO DE LA COLUMNA 'Q' TUVO DESCARGAR ESPECIFICA, EN QUE PEDIMENTO SE DESCARGO?",
            "OBSERVACIONES GLOBALES YA CON R1 (ETIQUETA ANTERIOR)",
        ]
    ].rename(
        columns={
            "SI EL PEDIMENTO DE LA COLUMNA 'T' ES R1, A QUIEN RECTIFICÓ?": "SI EL PEDIMENTO DE LA COLUMNA 'Q' ES R1, A QUIEN RECTIFICÓ?",
            "SI EL PEDIMENTO DE LA COLUMNA 'T' TUVO R1, CUÁL FUE EL NÚMERO DE R1?": "SI EL PEDIMENTO DE LA COLUMNA 'Q' TUVO R1, CUÁL FUE EL NÚMERO DE R1?",
            "SI EL PEDIMENTO DE LA COLUMNA 'T' ES DESCARGA ESPECIFICA, A QUIÉN DESCARGO?":"SI EL PEDIMENTO DE LA COLUMNA 'Q' ES DESCARGA ESPECIFICA, A QUIÉN DESCARGO?"
        }
    )


    df_ds_group = df_ds_group.merge(
        df_ped,
        left_on="ADU-PAT-PED",
        right_on="DS ADU-PAT-PED",
        how="left"
    )

    df_ds_group.drop(columns=["DS ADU-PAT-PED"], inplace=True)


    return df_ds_group


def mergeCliente_DS(df_ds_group, df_cli_group):

    df_ds_group=df_ds_group.copy()
    df_cli_group=df_cli_group.copy()

    df_ds_group = df_ds_group.merge(
        df_cli_group[
            ["HPH ADU-PAT-PED-HTS-SEC", "VALOR EN DOLARES","UM NORMALIZADA","CANT_UMC_NEW_DETALLE"]
        ].rename(
            columns={
                "VALOR EN DOLARES": "BASE VALOR DOLARES",
                "CANT_UMC_NEW_DETALLE": "BASE CANTIDAD COMERCIAL",
                "UM NORMALIZADA": "BASE UNIDAD DE MEDIDA COMERCIAL"
            }
        ),
        left_on="ADU-PAT-PED-HTS-SEC",
        right_on="HPH ADU-PAT-PED-HTS-SEC",
        how="left"
    )


    dif_real = df_ds_group["VAL USD"] - df_ds_group["BASE VALOR DOLARES"].fillna(0)

    df_ds_group["DIFERENCIA REAL"] = np.where(
        dif_real.between(-1, 1),
        0,
        dif_real
    )

    df_ds_group["DIFERENCIA ABSOLUTA"] = df_ds_group["DIFERENCIA REAL"].abs()


    df_ds_group["REVISIÓN DE DUPLICADOS"] = np.where(
        (df_ds_group["BASE VALOR DOLARES"].isna()) |
        (df_ds_group["VAL USD"] < 2),
        "",
        np.where(
            (
                (df_ds_group["VAL USD"] - df_ds_group["DIFERENCIA ABSOLUTA"] > -1)
                &
                (df_ds_group["VAL USD"] - df_ds_group["DIFERENCIA ABSOLUTA"] < 1)
                &
                (df_ds_group["BASE VALOR DOLARES"] > 3)
            ),
            "DUPLICADO",
            ""
        )
    )


    return df_ds_group


def ordenar(valor):
    if pd.isna(valor):
        return valor
    return " & ".join(sorted(str(valor).split(" & ")))



def revDuplicadoUND(df_ds_group):
    
    df_ds_group=df_ds_group.copy()
    
    x = df_ds_group["CANT_UMC_NEW_DETALLE"].apply(ordenar)
    y = df_ds_group["UM NORMALIZADA"].apply(ordenar)
    z = df_ds_group["BASE CANTIDAD COMERCIAL"].apply(ordenar)
    aa = df_ds_group["BASE UNIDAD DE MEDIDA COMERCIAL"].apply(ordenar)

    cant = pd.to_numeric(df_ds_group["CANT_UMC_NEW_DETALLE"], errors="coerce")
    base = pd.to_numeric(df_ds_group["BASE CANTIDAD COMERCIAL"], errors="coerce")

    resultado = np.empty(len(df_ds_group), dtype=object)

    # SI(Y(Y=AA;X=Z);0)
    resultado[(y == aa) & (x == z)] = 0

    # SI(Z="";X)
    m = ~( (y == aa) & (x == z) ) & base.isna()
    resultado[m] = df_ds_group.loc[m, "CANT_UMC_NEW_DETALLE"]

    # SI(Y<>AA;"REVISAR UM")
    m = ~( (y == aa) & (x == z) ) & ~base.isna() & (y != aa)
    resultado[m] = "REVISAR UM"

    # Diferencias numéricas
    m = ~( (y == aa) & (x == z) ) & ~base.isna() & (y == aa)

    dif = cant - base

    resultado[m & dif.between(-1, 1)] = 0
    resultado[m & ~dif.between(-1, 1)] = dif[m & ~dif.between(-1, 1)]

    df_ds_group["DIFERENCIA REAL UND"] = resultado


    df_ds_group["DIFERENCIA ABSOLUTA UND"] = pd.to_numeric(df_ds_group["DIFERENCIA REAL UND"], errors="coerce").abs().fillna(df_ds_group["DIFERENCIA REAL UND"])

    x = pd.to_numeric(df_ds_group["CANT_UMC_NEW_DETALLE"], errors="coerce")
    z = pd.to_numeric(df_ds_group["BASE CANTIDAD COMERCIAL"], errors="coerce")
    ac = pd.to_numeric(df_ds_group["DIFERENCIA ABSOLUTA UND"], errors="coerce")

    df_ds_group["REVISIÓN DE DUPLICADOS UND"] = np.where(
        x.isna() | z.isna() | (z == "") | (x <= 2),
        "",
        np.where(
            ((x - ac) > -1) &
            ((x - ac) < 1) &
            (z > 3),
            "DUPLICADO",
            ""
        )
    )
    
    return df_ds_group


def estatusUDS(df_ds_group):

    df_ds_group=df_ds_group.copy()

    s = pd.to_numeric(df_ds_group["VAL USD"], errors="coerce")
    t = pd.to_numeric(df_ds_group["BASE VALOR DOLARES"], errors="coerce")
    u = pd.to_numeric(df_ds_group["DIFERENCIA REAL"], errors="coerce")

    df_ds_group["ESTATUS USD A NIVEL SEC"] = np.where(
        df_ds_group["REVISIÓN DE DUPLICADOS"] == "DUPLICADO",
        df_ds_group["CLAVES IMMEX"] + "-DUPLICADO",

        np.where(
            t.isna() | (t.astype(str).str.strip() == ""),
            df_ds_group["CLAVES IMMEX"] + "-SECUENCIA FALTANTE EN BASE",

            np.where(
                (u >= -1) & (u <= 1),
                df_ds_group["CLAVES IMMEX"] + "-100% CORRECTO EN VALOR SEC",

                np.where(
                    (t == 0) & (s > 1),
                    df_ds_group["CLAVES IMMEX"] + "-LE FALTA VALOR SEC EN BASE",

                    np.where(
                        (((s / t) - 1) >= -0.01) &
                        (((s / t) - 1) <= 0.01),
                        df_ds_group["CLAVES IMMEX"] + "-99% CORRECTO EN VALOR SEC",

                        np.where(
                            t > s,
                            df_ds_group["CLAVES IMMEX"] + "-LE SOBRA VALOR SEC EN BASE",

                            np.where(
                                t < s,
                                df_ds_group["CLAVES IMMEX"] + "-LE FALTA VALOR SEC EN BASE",
                                ""
                            )
                        )
                    )
                )
            )
        )
    )  
    
    return df_ds_group    



def estatusUND(df_ds_group):
    
    df_ds_group=df_ds_group.copy()

    ab = pd.to_numeric(df_ds_group["DIFERENCIA REAL UND"], errors="coerce")


    x = pd.to_numeric(df_ds_group["CANT_UMC_NEW_DETALLE"], errors="coerce").where(
        pd.to_numeric(df_ds_group["CANT_UMC_NEW_DETALLE"], errors="coerce").notna(),
        df_ds_group["CANT_UMC_NEW_DETALLE"]
    )

    z = pd.to_numeric(df_ds_group["BASE CANTIDAD COMERCIAL"], errors="coerce").where(
        pd.to_numeric(df_ds_group["BASE CANTIDAD COMERCIAL"], errors="coerce").notna(),
        df_ds_group["BASE CANTIDAD COMERCIAL"]
    )


    z_vacio = z.isna() | (df_ds_group["BASE CANTIDAD COMERCIAL"].astype(str).str.strip() == "")

    df_ds_group["ESTATUS CANTIDAD COMERCIAL A NIVEL SEC"] = np.where(
        df_ds_group["DIFERENCIA REAL UND"] == "REVISAR UM",
        df_ds_group["CLAVES IMMEX"] + "-REVISAR UM",

        np.where(
            df_ds_group["REVISIÓN DE DUPLICADOS UND"] == "DUPLICADO",
            df_ds_group["CLAVES IMMEX"] + "-DUPLICADO",

            np.where(
                z_vacio,
                df_ds_group["CLAVES IMMEX"] + "-SECUENCIA FALTANTE EN BASE",

                np.where(
                    (ab >= -1) & (ab <= 1),
                    df_ds_group["CLAVES IMMEX"] + "-100% CORRECTO EN CANTIDAD SEC",

                    np.where(
                        # x > 1,
                        pd.to_numeric(x, errors="coerce").fillna(0) > 1,
                        df_ds_group["CLAVES IMMEX"] + "-LE FALTA CANTIDAD SEC EN BASE",

                        # np.where(
                        #     (((x / z) - 1) >= -0.01) &
                        #     (((x / z) - 1) <= 0.01),
                        #     df_ds_group["CLAVES IMMEX"] + "-99% CORRECTO EN CANTIDAD HTS EN BASE",

                        np.where(
                            (
                                (
                                    pd.to_numeric(x, errors="coerce").fillna(0) /
                                    pd.to_numeric(z, errors="coerce").replace(0, np.nan)
                                ) - 1 >= -0.01
                            ) &
                            (
                                (
                                    pd.to_numeric(x, errors="coerce").fillna(0) /
                                    pd.to_numeric(z, errors="coerce").replace(0, np.nan)
                                ) - 1 <= 0.01
                            ),
                            df_ds_group["CLAVES IMMEX"] + "-99% CORRECTO EN CANTIDAD SEC EN BASE",



                            # np.where(
                            #     z > x,
                            #     df_ds_group["CLAVES IMMEX"] + "-LE SOBRA CANTIDAD HTS EN BASE",

                            #     np.where(
                            #         z < x,
                            #         df_ds_group["CLAVES IMMEX"] + "-LE FALTA CANTIDAD HTS EN BASE",
                            #         ""
                            
                            np.where(
                                pd.to_numeric(z, errors="coerce").fillna(0) >
                                pd.to_numeric(x, errors="coerce").fillna(0),

                                df_ds_group["CLAVES IMMEX"] + "-LE SOBRA CANTIDAD SEC EN BASE",

                                np.where(
                                    pd.to_numeric(z, errors="coerce").fillna(0) <
                                    pd.to_numeric(x, errors="coerce").fillna(0),

                                    df_ds_group["CLAVES IMMEX"] + "-LE FALTA CANTIDAD SEC EN BASE",
                                    ""                        

                            
                                )
                            )
                        )
                    )
                )
            )
        )
    )


    return df_ds_group    



def estatusPedimentoAux1(df_ds_group):

    df_ds_group=df_ds_group.copy()



    t_vacio = (
        df_ds_group["BASE VALOR DOLARES"].isna() |
        (df_ds_group["BASE VALOR DOLARES"].astype(str).str.strip() == "")
    )

    z_vacio = (
        df_ds_group["BASE CANTIDAD COMERCIAL"].isna() |
        (df_ds_group["BASE CANTIDAD COMERCIAL"].astype(str).str.strip() == "")
    )

    v = pd.to_numeric(df_ds_group["DIFERENCIA ABSOLUTA"], errors="coerce")
    ab = pd.to_numeric(df_ds_group["DIFERENCIA ABSOLUTA UND"], errors="coerce")

    df_ds_group["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)"] = np.where(
        t_vacio | z_vacio,
        "SECUENCIA FALTANTE EN BASE",

        np.where(
            (v == 0) & (ab == 0),
            "SECUENCIA 100% CORRECTA EN DOLARES Y CANTIDAD",

            np.where(
                (v == 0) & (ab != 0),
                "SECUENCIA BIEN EN DOLARES Y MAL EN CANTIDAD",

                np.where(
                    (v != 0) & (ab == 0),
                    "SECUENCIA BIEN EN CANTIDAD Y MAL EN DOLARES",

                    np.where(
                        (v != 0) & (ab != 0),
                        "SECUENCIA REQUIERE CORRECCION",
                        ""
                    )
                )
            )
        )
    )
    
    estado_ok = "SECUENCIA 100% CORRECTA EN DOLARES Y CANTIDAD"

    # Obtener los ADU-PAT-PED donde TODAS las fracciones tienen el estado correcto
    pedimentos_ok = (
        df_ds_group
        .groupby("ADU-PAT-PED")["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)"]
        .apply(lambda x: (x == estado_ok).all())
    )

    # Quedarse solo con los ADU-PAT-PED válidos
    pedimentos_ok = pedimentos_ok[pedimentos_ok].index

    # Crear el nuevo DataFrame
    df_ped_aux = (
        df_ds_group[
            df_ds_group["ADU-PAT-PED"].isin(pedimentos_ok)
        ][
            [
                "ADU-PAT-PED",
                "ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)"
            ]
        ]
        .drop_duplicates()
        .reset_index(drop=True)
    )


    df_ds_group = df_ds_group.merge(
        df_ped_aux.rename(columns={
            "ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)": "ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)_aux"
        }),
        on="ADU-PAT-PED",
        how="left"
    )

    # df_ds_group = df_ds_group.merge(
    #     df_ped_aux,
    #     on="ADU-PAT-PED",
    #     how="left"
    # )
        
    return df_ds_group 


def estatusPedimentoAux2(df_ds_group): 

    df_ds_group=df_ds_group.copy()
    
    df_ds_group["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 2)"] = np.where(
        df_ds_group["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)_aux"] == "SECUENCIA 100% CORRECTA EN DOLARES Y CANTIDAD",
        "PEDIMENTO CON SECUENCIA 100% CORRECTOS DOLARES Y CANTIDAD",
        ""
    )

    df_ds_group.drop(columns=["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)_aux"], inplace=True)

    return df_ds_group


def estatusNivlPed(df_ds_group):

    df_ds_group=df_ds_group.copy()
    
    df_ds_group["ESTATUS SEC A NIVEL PEDIMENTO"] = np.where(
        df_ds_group["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 2)"].fillna("").str.strip() != "",
        df_ds_group["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 2)"],
        df_ds_group["ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)"]
    )


    # df_ds_group["LLAVE PED-VALORUSD"] = (
    #     df_ds_group["ADU-PAT-PED"].astype(str)
    #     + "-"
    #     + np.floor(pd.to_numeric(df_ds_group["VAL USD"], errors="coerce")).fillna(0).astype(int).astype(str)
    # )

    df_ds_group["LLAVE PED-VALORUSD"] = (
        df_ds_group["ADU-PAT-PED"].astype(str)
        + "-"
        + np.floor(
            pd.to_numeric(df_ds_group["VAL USD"], errors="coerce") + 1e-9
        ).fillna(0).astype(int).astype(str)
    )
        
    return df_ds_group


def formatearColumnas(df_ds_group):
    
    df_ds_group=df_ds_group.copy()

    df_ds_group = (
        df_ds_group
        .rename(columns={
            "ADU-PAT-PED": "DS ADU-PAT-PED",
            "ADU-PAT-PED-HTS-SEC": "DS ADU-PAT-PED-HTS-SEC",
            "VAL USD":"DS VALOR DOLARES",
            "CANT_UMC_NEW_DETALLE":"DS CANTIDAD COMERCIAL",
            "UM NORMALIZADA":"DS UNIDAD DE MEDIDA COMERCIAL",
            "ESTATUS USD A NIVEL SEC":"ESTATUS USD A NIVEL SEC",
            "OBSERVACIONES GLOBALES YA CON R1 (ETIQUETA ANTERIOR)":"ESTATUS X USD A NIVEL GLOBAL DEL CROSS X PED",
            "ESTATUS CANTIDAD COMERCIAL A NIVEL SEC":"ESTATUS CANTIDAD COMERCIAL A NIVEL SEC"
        
        })
        [
        [
            "CLAVES IMMEX",
            "FECHA PAGO",
            "FECHA ENTRADA O PRESENTACIÓN",
            "ID AF?",
            "TIPO Y CLAVE",
            "SI EL PEDIMENTO DE LA COLUMNA 'Q' ES R1, A QUIEN RECTIFICÓ?",        
            "ESTATUS DEL PEDIMENTO A QUIEN RECTIFICO DE LA COLUMNA 'F'?",
            "SI EL PEDIMENTO DE LA COLUMNA 'Q' TUVO R1, CUÁL FUE EL NÚMERO DE R1?",        
            "ESTATUS DEL PEDIMENTO R1 DE LA COLUMNA H",
            "ESTIMACIÓN APROX DE IGI  6 FP 0",        
            "ESTIMACIÓN APROX DE IGI 6 FP 5",        
            "ESTIMACIÓN APROX DE IGI 6 FP 6",
            "SI EL PEDIMENTO DE LA COLUMNA 'Q' ES DESCARGA ESPECIFICA, A QUIÉN DESCARGO?",
            "SI EL PEDIMENTO DE LA COLUMNA 'Q' TUVO DESCARGAR ESPECIFICA, EN QUE PEDIMENTO SE DESCARGO?",
            "DS PAT-PED",
            "DS PAT-PED-HTS",        
            "DS ADU-PAT-PED",
            "DS ADU-PAT-PED-HTS-SEC",        
            "DS VALOR DOLARES",        
            "BASE VALOR DOLARES",        
            "DIFERENCIA REAL",
            "DIFERENCIA ABSOLUTA",
            "REVISIÓN DE DUPLICADOS",
            "DS CANTIDAD COMERCIAL",
            "DS UNIDAD DE MEDIDA COMERCIAL",
            "BASE CANTIDAD COMERCIAL",
            "BASE UNIDAD DE MEDIDA COMERCIAL",
            "DIFERENCIA REAL UND",
            "DIFERENCIA ABSOLUTA UND",
            "REVISIÓN DE DUPLICADOS UND",
            "ESTATUS X USD A NIVEL GLOBAL DEL CROSS X PED",
            "ESTATUS USD A NIVEL SEC",
            "ESTATUS CANTIDAD COMERCIAL A NIVEL SEC",
            "ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 1)",
            "ESTATUS SEC A NIVEL PEDIMENTO (AUXILIAR 2)",
            "ESTATUS SEC A NIVEL PEDIMENTO"

        ]
        ]
    )

    return df_ds_group    
    

def ejecutar_proceso(dfs,df_ped):
    
    """
    Ejecuta el proceso completo de transformación de datos.
    """

    df_ds = dfs["df_ds"]
    # dataframe_DS_Virgen = dfs["df_virgen"]
    df_cli=dfs["df_cli"]  
    
        
    df_ds=crearDfDS(df_ds)
    df_cli_group=crearDfCliente(df_cli)
    df_ds_v2=crearDfDSGroup(df_ds)
    df_ds_v3=extraerDSCrossxPedMerge(df_ds_v2,df_ped)
    df_ds_v4=mergeCliente_DS(df_ds_v3,df_cli_group)
    df_ds_v5=revDuplicadoUND(df_ds_v4)
    df_ds_v6=estatusUDS(df_ds_v5)
    df_ds_v7=estatusUND(df_ds_v6)
    df_ds_v8=estatusPedimentoAux1(df_ds_v7)
    df_ds_v9=estatusPedimentoAux2(df_ds_v8)    
    df_ds_v10=estatusNivlPed(df_ds_v9)
    df_ds_v11=formatearColumnas(df_ds_v10)
    # exportarArchivo(df_ds_v10)
    
    return df_ds_v11