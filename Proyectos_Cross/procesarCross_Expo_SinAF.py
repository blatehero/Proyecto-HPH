import pandas as pd
from datetime import datetime
import numpy as np
from Proyectos_Cross.log import log



def pedimentoAF(df_ds):
    
    df_ds=df_ds.copy()

    df_ds_AF = df_ds[["ADU-PAT-PED", "CLAVE PED","AF"]]
    df_ds_AF["CLAVE PED_NEW"] = df_ds_AF["CLAVE PED"].astype(str).str[:4]
    df_ds_AF["LLAVE"] = df_ds_AF["ADU-PAT-PED"].astype(str) + "-" + df_ds_AF["CLAVE PED_NEW"].astype(str)

    return df_ds_AF



def listaCliente(df_cli,origen, claves):

    df_cli=df_cli.copy()
    # origen=origen.copy()
    # claves=claves.copy()


    df_cli_filtrado = df_cli[
        (df_cli["ORIGEN"] == origen) &
        (df_cli["CLAVE"].isin(claves))
    ]


    if origen=="IMPO":
        df_cli_filtrado = df_cli_filtrado[["NUMERO_PARTE","ADU-PAT-PED","ADU-PAT-PED-HTS", "CLAVE","VALOR EN DOLARES","FECHA_PAGO","FRACCION"]]
        df_cli_filtrado["LLAVE"] = df_cli_filtrado["ADU-PAT-PED"].astype(str) + "-1-" + df_cli_filtrado["CLAVE"].astype(str)
        df_cli_filtrado["FRACCION"] = df_cli_filtrado["ADU-PAT-PED-HTS"].astype(str).str.split("-").str[-1]
        df_cli_filtrado = df_cli_filtrado.drop(columns=["ADU-PAT-PED-HTS"])
    
    if origen=="EXPO":
        df_cli_filtrado = df_cli_filtrado[["NUMERO_PARTE","ADU-PAT-PED","ADU-PAT-PED-HTS", "CLAVE","VALOR EN DOLARES","FECHA_PAGO","FRACCION"]]
        df_cli_filtrado["LLAVE"] = df_cli_filtrado["ADU-PAT-PED"].astype(str) + "-2-" + df_cli_filtrado["CLAVE"].astype(str)
        df_cli_filtrado["FRACCION"] = df_cli_filtrado["ADU-PAT-PED-HTS"].astype(str).str.split("-").str[-1]
        df_cli_filtrado = df_cli_filtrado.drop(columns=["ADU-PAT-PED-HTS"])
    
    
    return df_cli_filtrado


def listaTomar(df_cli_filtrado,df_cli,df_ds_AF):

    df_cli_filtrado=df_cli_filtrado.copy()
    df_cli=df_cli.copy()
    df_ds_AF=df_ds_AF.copy()

    df_gp = df_cli_filtrado[["ADU-PAT-PED", "LLAVE"]].drop_duplicates()
    df_ds_AF_gp = df_ds_AF[["ADU-PAT-PED", "LLAVE","AF","CLAVE PED"]].drop_duplicates()
    
    # df_gp[df_gp["ADU-PAT-PED"].duplicated(keep=False)].sort_values("ADU-PAT-PED")        
    df_gp = df_gp.merge(
        df_ds_AF_gp[["LLAVE","CLAVE PED" ,"AF"]],
        on="LLAVE",
        how="left"
    )    
    
    df_gp = df_gp[df_gp["AF"].isna()]
            
    clave = df_gp["CLAVE PED"].astype(str)

    # Todos empiezan en 1
    df_gp["ETIQUETA"] = 1

    # Solo TUVO
    mask_tuvo = clave.str.contains("TUVO", case=False, na=False)

    # Extraer ADU únicamente de los TUVO
    ultimo_adu = (
        clave[mask_tuvo]
        .str.findall(r"\d{3}-\d{4}-\d{7}")
        .str[-1]
    )

    # Validar contra df_cli
    adu_cli = set(
        df_cli["ADU-PAT-PED"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    df_gp.loc[mask_tuvo, "ETIQUETA"] = (
        ultimo_adu.isin(adu_cli).map({True: 0, False: 1})
    )
    
    df_gp = df_gp[df_gp["ETIQUETA"] == 1]
    
    return df_gp


def listaTomarR1(df_cli_filtrado,df_ds_AF,df_gp_rs):

    df_cli_filtrado=df_cli_filtrado.copy()
    df_ds_AF=df_ds_AF.copy()
    df_gp_rs=df_gp_rs.copy()


    df_gp = df_cli_filtrado[["ADU-PAT-PED"]].drop_duplicates()
    df_ds_AF_gp = df_ds_AF[["ADU-PAT-PED","AF","CLAVE PED"]].drop_duplicates()
    
    # df_gp[df_gp["ADU-PAT-PED"].duplicated(keep=False)].sort_values("ADU-PAT-PED")        
    df_gp = df_gp.merge(
        df_ds_AF_gp[["ADU-PAT-PED" ,"CLAVE PED","AF"]],
        on="ADU-PAT-PED",
        how="left"
    )    
    
    df_gp = df_gp[df_gp["AF"].isna()]
    
    
    
    df_gp = df_gp[
    df_gp["CLAVE PED"].str.startswith(("2-RT-", "2-V1-"), na=False) &
    ~df_gp["CLAVE PED"].str.contains("TUVO", case=False, na=False)
]


    # ultimo_adu = df_gp["CLAVE PED"].str.findall(r"\d{3}-\d{4}-\d{7}").str[-1]

    # df_gp = df_gp[
    #     ~ultimo_adu.isin(df_gp_rs["ADU-PAT-PED"])
    # ]

    ultimo_adu = df_gp["CLAVE PED"].str.findall(r"\d{3}-\d{4}-\d{7}").str[-1]

    # Identificar los que existen en df_gp_rs
    coincidentes = df_gp_rs[df_gp_rs["ADU-PAT-PED"].isin(ultimo_adu)]

    # De los encontrados, identificar cuáles tienen TUVO
    tiene_tuvo = coincidentes["CLAVE PED"].str.contains(
        "TUVO",
        case=False,
        na=False
    )

    # ADU encontrados SIN TUVO
    adu_sin_tuvo = coincidentes.loc[
        ~tiene_tuvo,
        "ADU-PAT-PED"
    ]


    # Quitar de df_gp solo los que fueron encontrados SIN TUVO
    df_gp = df_gp[
        ~ultimo_adu.isin(adu_sin_tuvo)
    ]


    # Quitar de df_gp_rs los encontrados CON TUVO
    df_gp_rs = df_gp_rs[
        ~(
            df_gp_rs["ADU-PAT-PED"].isin(coincidentes.loc[tiene_tuvo, "ADU-PAT-PED"])
            &
            df_gp_rs["CLAVE PED"].str.contains("TUVO", case=False, na=False)
        )
    ]
                    
    return df_gp,df_gp_rs
        


def numeroParteLimpio(df_cli_final):

    df_cli_final=df_cli_final.copy()

    df_cli_final["NUMERO_PARTE_LIMPIO"] = df_cli_final["NUMERO_PARTE"]
    df_cli_final["NUMERO_PARTE_LIMPIO"] = df_cli_final["NUMERO_PARTE_LIMPIO"].str.strip()
    df_cli_final["NUMERO_PARTE_LIMPIO"] = df_cli_final["NUMERO_PARTE_LIMPIO"].astype(str).str.replace(r"[^A-Za-z0-9]", "", regex=True)

    mask = df_cli_final["NUMERO_PARTE_LIMPIO"].str.match(r"^0\d+$")

    df_cli_final.loc[mask, "NUMERO_PARTE_LIMPIO"] = pd.to_numeric(
        df_cli_final.loc[mask, "NUMERO_PARTE_LIMPIO"]
    ) * 1    
    
    return df_cli_final    




def agruparResultado(df_cli_final):

    df_cli_final=df_cli_final.copy()

    df_equivalencia = (
        df_cli_final[
            ["NUMERO_PARTE_LIMPIO", "NUMERO_PARTE"]
        ]
        .drop_duplicates("NUMERO_PARTE_LIMPIO")
    )


    df_equivalencia_2 = (
        df_cli_final
        .groupby(
            ["NUMERO_PARTE_LIMPIO", "DESCRIPCION_MERCADERIA"]
        )
        .size()
        .reset_index(name="CANTIDAD")
        .sort_values(
            ["NUMERO_PARTE_LIMPIO", "CANTIDAD"],
            ascending=[True, False]
        )
        .drop_duplicates(
            "NUMERO_PARTE_LIMPIO",
            keep="first"
        )
        [["NUMERO_PARTE_LIMPIO", "DESCRIPCION_MERCADERIA"]]
    )




    df_cli_final["FECHA_PAGO"] = pd.to_datetime(df_cli_final["FECHA_PAGO"], dayfirst=True)

    df_resumen = (
        df_cli_final
        .groupby(["NUMERO_PARTE_LIMPIO", "FRACCION"], as_index=False)
        .agg(
            
            # NUMERO_PARTE=("NUMERO_PARTE", lambda x: "/".join(x.dropna().astype(str).unique())),
            CLAVE=("CLAVE", lambda x: "/".join(x.dropna().astype(str).unique())),
            REGISTROS_FRACCION=("FRACCION", "size"),
            VALOR_DOLARES_FRACCION=("VALOR EN DOLARES", "sum"),
            FECHA_MIN=("FECHA_PAGO", "min"),
            FECHA_MAX=("FECHA_PAGO", "max")
        )
    )


    df_resumen["FRACCIONES_UNICAS"] = (
        df_resumen.groupby("NUMERO_PARTE_LIMPIO")["FRACCION"]
        .transform("nunique")
    )

    # df_resumen["REGISTROS_TOTAL"] = (
    #     df_resumen.groupby("NUMERO_PARTE_LIMPIO")["REGISTROS_FRACCION"]
    #     .transform("sum")
    # )

    df_resumen["VALOR_DOLARES_TOTAL"] = (
        df_resumen.groupby("NUMERO_PARTE_LIMPIO")["VALOR_DOLARES_FRACCION"]
        .transform("sum")
    )

    df_resumen = df_resumen.merge(
        df_equivalencia,
        on="NUMERO_PARTE_LIMPIO",
        how="left"
    )

    df_resumen = df_resumen.merge(
        df_equivalencia_2,
        on="NUMERO_PARTE_LIMPIO",
        how="left"
    )

    return df_resumen    




def calcularColumnas(df_resumen):

    df_resumen = df_resumen.copy()

    df_resumen["FECHA_MIN"] = pd.to_datetime(df_resumen["FECHA_MIN"])
    df_resumen["FECHA_MAX"] = pd.to_datetime(df_resumen["FECHA_MAX"])

    df_resumen["REVISAR_FRACCION"] = ""

    for parte, idx in df_resumen.groupby("NUMERO_PARTE_LIMPIO").groups.items():
        if len(idx) < 2:
            continue

        fechas_min = df_resumen.loc[idx, "FECHA_MIN"]
        fechas_max = df_resumen.loc[idx, "FECHA_MAX"]

        for i in idx:
            if df_resumen.loc[i, "FRACCIONES_UNICAS"] == 2:
                cruza = (
                    (fechas_min < df_resumen.loc[i, "FECHA_MAX"]) &
                    (fechas_max > df_resumen.loc[i, "FECHA_MIN"])
                )
                cruza.loc[i] = False

                if cruza.any():
                    df_resumen.loc[i, "REVISAR_FRACCION"] = "REVISAR FRACCION"    



    df_resumen["2_DIGITOS_FRACCION"] = df_resumen["FRACCION"].astype(str).str[:2]
    
    conteo = df_resumen.groupby("NUMERO_PARTE_LIMPIO")["2_DIGITOS_FRACCION"].transform(
        lambda x: (x.astype(str) == "98").sum()
    )
    df_resumen["REGLA_MAS_DE_UNA_FRACCION"] = conteo.ge(2).map({True: "SI", False: ""})


    df_resumen["CONCATENADO"] = df_resumen["NUMERO_PARTE"] + "-" + df_resumen["FRACCION"]

    return df_resumen


def formatearColumnas(df_resumen):

    df_resumen = df_resumen.copy()

    df_resumen = df_resumen.rename(columns={
        "NUMERO_PARTE": "BASE MATERIAL NP CLIENTE",
        "NUMERO_PARTE_LIMPIO": "HPH NP LIMPIO",
        "FRACCION": "BASE HPH HTS",
        "CLAVE": "BASE HPH TOPE-CLAVE X NP",
        "VALOR_DOLARES_TOTAL": "BASE HPH VALOR USD GLOBAL",
        "VALOR_DOLARES_FRACCION": "BASE HPH VALOR USD POR NP Y HTS",
        "FRACCIONES_UNICAS": "CANTIDAD DE FRACCIONES POR NUM PTE",
        "REGISTROS_FRACCION": "CANT DE REGISTROS DE NP Y FRACC EN BASE",
        "FECHA_MIN": "BASE HPH PRIMERA FECHA DE PAGO DE ACUERDO AL NP Y HTS",
        "FECHA_MAX": "BASE HPH ULTIMA FECHA DE PAGO DE ACUERDO AL NP Y HTS",
        "DESCRIPCION_MERCADERIA": "BASE DESCRIPCION X NP",
        "REVISAR_FRACCION": "CONVERGENCIA PARA 2 FRACCIONES?",
        "2_DIGITOS_FRACCION": "PRIMEROS 2 DIGITOS DE FRACCION",
        "REGLA_MAS_DE_UNA_FRACCION": "REGLA OCTAVA MAS DE UNA FRACCIÓN",
        "CONCATENADO": "CONCATENADO BASE MATERIAL NP CLIENTE + BASE HPH HTS"
    })

    # ORDEN EXACTO DEL BLOQUE DE ARRIBA
    orden_columnas = [
        "BASE MATERIAL NP CLIENTE",
        "HPH NP LIMPIO",
        "BASE HPH HTS",
        "BASE HPH TOPE-CLAVE X NP",
        "BASE HPH VALOR USD GLOBAL",
        "BASE HPH VALOR USD POR NP Y HTS",
        "CANTIDAD DE FRACCIONES POR NUM PTE",
        "CANT DE REGISTROS DE NP Y FRACC EN BASE",
        "BASE HPH PRIMERA FECHA DE PAGO DE ACUERDO AL NP Y HTS",
        "BASE HPH ULTIMA FECHA DE PAGO DE ACUERDO AL NP Y HTS",
        "BASE DESCRIPCION X NP",
        "CONVERGENCIA PARA 2 FRACCIONES?",
        "PRIMEROS 2 DIGITOS DE FRACCION",
        "REGLA OCTAVA MAS DE UNA FRACCIÓN",
        "CONCATENADO BASE MATERIAL NP CLIENTE + BASE HPH HTS"
    ]

    df_resumen = df_resumen[orden_columnas]

    return df_resumen



def ejecutar_proceso(dfs,df_ped):
    
    """
    Ejecuta el proceso completo de transformación de datos.
    """

    df_ds = dfs["df_ds"]
    # dataframe_DS_Virgen = dfs["df_virgen"]
    df_cli=dfs["df_cli"]  
    
    log(df_cli.columns.tolist())
    
    # print("COLUMNAS DF_CLI:")
    # print(df_cli.columns.tolist())
    
    #1 CREACION DEL DATAFRAME DE IMPO/EXPO

    df_ds_AF = pedimentoAF(df_ds)
    # df_cliente_impo=listaCliente(df_cli,"IMPO", ["IN", "V1"])
    df_cliente_expo=listaCliente(df_cli,"EXPO", ["RT", "V1"])
    df_gp_rs=listaTomar(df_cliente_expo,df_cli,df_ds_AF)

    #2 CREACION DEL DATAFRAME DE DE R1 PARA CORRECCION DE IMPO/EXPO
    # df_cliente_impo_r1=listaCliente(df_cli,"IMPO", ["R1"])
    df_cliente_expo_r1=listaCliente(df_cli,"EXPO", ["R1"])
    df_gp_rs_r1,df_gp_rs_vf=listaTomarR1(df_cliente_expo_r1,df_ds_AF,df_gp_rs)


    #3 UNIFICACION DEL RESULTADO, ESTO SOLO SI SE CORRE CORRECION DE R1 SI NO NO ES NECESARIO EJECUTAR
    df_final = pd.concat([
        df_gp_rs_r1[["ADU-PAT-PED"]],
        df_gp_rs_vf[["ADU-PAT-PED"]]
    ])


    #4 DE ACUERDO A LA SITUACION ANTERIOR SE CORREO CON R1 ES NECEASRIO QUE SEA COMO EN LA OPCION A, CASO CONTRARIO USAR LA OPCION B

    # A
    df_cli_final = df_cli[df_cli["ADU-PAT-PED"].isin(df_final["ADU-PAT-PED"])]

    # B
    # df_cli_final = df_cli[df_cli["ADU-PAT-PED"].isin(df_gp_rs["ADU-PAT-PED"])]

    # ---------------------------------------------------------------------------------


    #5 CREACION DE LAS COLUMNAS A CONSIDERAR PARA EL PROCESO

    df_cli_final = df_cli_final[
        df_cli_final["ADU-PAT-PED"].isin(df_cli_final["ADU-PAT-PED"])
    ][["ADU-PAT-PED","FRACCION", "CLAVE","VALOR EN DOLARES" ,"FECHA_PAGO","NUMERO_PARTE","DESCRIPCION_MERCADERIA"]]


    #6 FUNCIONES A EJECUTAR PROCESO

    df_cli_final_v1=numeroParteLimpio(df_cli_final)
    df_cli_final_v2=agruparResultado(df_cli_final_v1)
    df_cli_final_v3=calcularColumnas(df_cli_final_v2)
    df_cli_final_v4=formatearColumnas(df_cli_final_v3)

    # 31084 
    # df_ds=crearDfDS(df_ds)
    # df_cli_group=crearDfCliente(df_cli)
    # df_ds_v2=crearDfDSGroup(df_ds)
    # df_ds_v3=extraerDSCrossxPedMerge(df_ds_v2,df_ped)
    # df_ds_v4=mergeCliente_DS(df_ds_v3,df_cli_group)
    # df_ds_v5=revDuplicadoUND(df_ds_v4)
    # df_ds_v6=estatusUDS(df_ds_v5)
    # df_ds_v7=estatusUND(df_ds_v6)
    # df_ds_v8=estatusPedimentoAux1(df_ds_v7)
    # df_ds_v9=estatusPedimentoAux2(df_ds_v8)
    # df_ds_v10=llavePedValor(df_ds_v9)
    # df_ds_v10=formatearColumnas(df_ds_v10)

    
    return df_cli_final_v4