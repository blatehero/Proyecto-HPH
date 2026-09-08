import pandas as pd
from datetime import datetime
import numpy as np
from Proyectos_Cross.log import log

def crearDfCliente(df_cli):

    df_cli =df_cli.copy()
    
    # log(df_cli.to_string())
    
    columnas_group_cli = [
        "ADU-PAT-PED-HTSNICO"
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

    df_ds["DS PAT-PED-HTSNICO"] = (
        df_ds["ADU-PAT-PED-HTSNICO"]
        .str.split("-", n=1)
        .str[1]
    )


    return df_ds


def crearDfDSGroup(df_ds):

    df_ds=df_ds.copy()
    
    columnas_group = [
        "DS PAT-PED",
        "DS PAT-PED-HTSNICO",
        "ADU-PAT-PED",
        "ADU-PAT-PED-HTSNICO",
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



    # dato_buscar = "240-1902-6001887-8209000100"

    # df_filtrado = df_cli_group[
    #     df_cli_group["ADU-PAT-PED-HTSNICO"].astype(str) == dato_buscar
    # ]

    




    df_ds_group = df_ds_group.merge(
        df_cli_group[
            ["ADU-PAT-PED-HTSNICO", "VALOR EN DOLARES","UM NORMALIZADA","CANT_UMC_NEW_DETALLE"]
        ].rename(
            columns={
                "VALOR EN DOLARES": "BASE VALOR DOLARES",
                "CANT_UMC_NEW_DETALLE": "BASE CANTIDAD COMERCIAL",
                "UM NORMALIZADA": "BASE UNIDAD DE MEDIDA COMERCIAL"
            }
        ),
        left_on="ADU-PAT-PED-HTSNICO",
        right_on="ADU-PAT-PED-HTSNICO",
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


    cant_original = df_ds_group["CANT_UMC_NEW_DETALLE"]
    base_original = df_ds_group["BASE CANTIDAD COMERCIAL"]

    base_vacio = (
        base_original.isna() |
        (base_original.astype(str).str.strip() == "")
    )

    cant_texto = cant.isna() & ~(
        cant_original.isna() |
        (cant_original.astype(str).str.strip() == "")
    )

    base_texto = base.isna() & ~base_vacio


    resultado = np.empty(len(df_ds_group), dtype=object)

    # SI(Y(Y=AA;X=Z);0)
    resultado[(y == aa) & (x == z)] = 0

    # SI(Z="";X)
    # m = ~( (y == aa) & (x == z) ) & base.isna()
    # resultado[m] = df_ds_group.loc[m, "CANT_UMC_NEW_DETALLE"]

    # SI(Y<>AA;"REVISAR UM")
    # m = ~( (y == aa) & (x == z) ) & ~base.isna() & (y != aa)
    # resultado[m] = "REVISAR UM"



    # SI(BASE CANTIDAD COMERCIAL=""; CANT_UMC_NEW_DETALLE)
    m = ~( (y == aa) & (x == z) ) & base_vacio
    resultado[m] = df_ds_group.loc[m, "CANT_UMC_NEW_DETALLE"]


    # SI(O(ESTEXTO(CANTIDAD);ESTEXTO(BASE CANTIDAD));"REVISAR UM")
    m = (
        ~( (y == aa) & (x == z) )
        & ~base_vacio
        & (cant_texto | base_texto)
    )
    resultado[m] = "REVISAR UM"


    # SI(UNIDADES DIFERENTES;"REVISAR UM")
    m = (
        ~( (y == aa) & (x == z) )
        & ~base_vacio
        & ~(cant_texto | base_texto)
        & (y != aa)
    )
    resultado[m] = "REVISAR UM"


    # Diferencias numéricas
    # m = ~( (y == aa) & (x == z) ) & ~base.isna() & (y == aa)
    m = (~( (y == aa) & (x == z) )& ~base_vacio & ~(cant_texto | base_texto) & (y == aa))

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

    df_ds_group["ESTATUS USD A NIVEL HTSNICO"] = np.where(
        df_ds_group["REVISIÓN DE DUPLICADOS"] == "DUPLICADO",
        df_ds_group["CLAVES IMMEX"] + "-DUPLICADO",

        np.where(
            t.isna() | (t.astype(str).str.strip() == ""),
            df_ds_group["CLAVES IMMEX"] + "-HTSNICO FALTANTE EN BASE",

            np.where(
                (u >= -1) & (u <= 1),
                df_ds_group["CLAVES IMMEX"] + "-100% CORRECTO EN VALOR HTSNICO",

                np.where(
                    (t == 0) & (s > 1),
                    df_ds_group["CLAVES IMMEX"] + "-LE FALTA VALOR HTSNICO EN BASE",

                    np.where(
                        (((s / t) - 1) >= -0.01) &
                        (((s / t) - 1) <= 0.01),
                        df_ds_group["CLAVES IMMEX"] + "-99% CORRECTO EN VALOR HTSNICO",

                        np.where(
                            t > s,
                            df_ds_group["CLAVES IMMEX"] + "-LE SOBRA VALOR HTSNICO EN BASE",

                            np.where(
                                t < s,
                                df_ds_group["CLAVES IMMEX"] + "-LE FALTA VALOR HTSNICO EN BASE",
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

    df_ds_group["ESTATUS CANTIDAD COMERCIAL A NIVEL HTSNICO"] = np.where(
        df_ds_group["DIFERENCIA REAL UND"] == "REVISAR UM",
        df_ds_group["CLAVES IMMEX"] + "-REVISAR UM",

        np.where(
            df_ds_group["REVISIÓN DE DUPLICADOS UND"] == "DUPLICADO",
            df_ds_group["CLAVES IMMEX"] + "-DUPLICADO",

            np.where(
                z_vacio,
                df_ds_group["CLAVES IMMEX"] + "-HTSNICO FALTANTE EN BASE",

                np.where(
                    (ab >= -1) & (ab <= 1),
                    df_ds_group["CLAVES IMMEX"] + "-100% CORRECTO EN CANTIDAD HTSNICO",

                    # np.where(
                    #     # x > 1,
                    #     pd.to_numeric(x, errors="coerce").fillna(0) > 1,
                    #     df_ds_group["CLAVES IMMEX"] + "-LE FALTA CANTIDAD HTSNICO EN BASE",

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
                            df_ds_group["CLAVES IMMEX"] + "-99% CORRECTO EN CANTIDAD HTSNICO EN BASE",



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

                                df_ds_group["CLAVES IMMEX"] + "-LE SOBRA CANTIDAD HTSNICO EN BASE",

                                np.where(
                                    pd.to_numeric(z, errors="coerce").fillna(0) <
                                    pd.to_numeric(x, errors="coerce").fillna(0),

                                    df_ds_group["CLAVES IMMEX"] + "-LE FALTA CANTIDAD HTSNICO EN BASE",
                                    ""                        

                            
                                )
                            )
                        )
                    )
                )
            )
        )
    # )
    return df_ds_group    






def formatearColumnas(df_ds_group):
    
    df_ds_group=df_ds_group.copy()
    
    df_ds_group = (
        df_ds_group
        .rename(columns={ 
            "ADU-PAT-PED": "DS ADU-PAT-PED",
            "ADU-PAT-PED-HTSNICO": "DS ADU-PAT-PED-HTSNICO",
            "VAL USD":"DS VALOR DOLARES",
            "CANT_UMC_NEW_DETALLE":"DS CANTIDAD COMERCIAL",
            "UM NORMALIZADA":"DS UNIDAD DE MEDIDA COMERCIAL",
            "ESTATUS USD A NIVEL HTSNICO":"ESTATUS USD A NIVEL HTSNICO",
            "OBSERVACIONES GLOBALES YA CON R1 (ETIQUETA ANTERIOR)":"ESTATUS X USD A NIVEL GLOBAL DEL CROSS X PED",
            "ESTATUS CANTIDAD COMERCIAL A NIVEL HTSNICO":"ESTATUS CANTIDAD COMERCIAL A NIVEL HTSNICO"
        
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
            "DS PAT-PED-HTSNICO",        
            "DS ADU-PAT-PED",
            "DS ADU-PAT-PED-HTSNICO",        
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
            "ESTATUS USD A NIVEL HTSNICO",
            "ESTATUS CANTIDAD COMERCIAL A NIVEL HTSNICO"

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
    df_ds_v8=formatearColumnas(df_ds_v7)
    # exportarArchivo(df_ds_v10)
    
    return df_ds_v8