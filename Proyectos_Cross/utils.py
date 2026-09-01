import pandas as pd
from datetime import datetime
import numpy as np
import os

ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ruta_homologadas = os.path.join(
    ruta_base,
    "datos",
    "UND HOMOLOGADAS.csv"
)
# pd.set_option("display.precision", 10)

# ruta= r"C:/Users/User/OneDrive/Proyecto/PYTHON/Proyecto HPH/CROSS X/inputs/"



def leer_csv(archivo):

    # with open(ruta, "r", encoding="utf-8") as f:
    #     encabezado = f.readline()
    
    encabezado = archivo.readline().decode("utf-8")
    archivo.seek(0)

    if encabezado.count("|") > max(encabezado.count(";"), encabezado.count(",")):
        separador = "|"
    elif encabezado.count(";") > encabezado.count(","):
        separador = ";"
    else:
        separador = ","

    return pd.read_csv(
        archivo,
        sep=separador,
        dtype=str
    )

def limpiar_campo(valor):

    if valor is None:
        return ""

    return str(valor).strip()




def dataframe_excel(archivo_base, archivo_clientes):
    
    # df_ds = leer_csv(archivo_ds)

    # df_homo = leer_csv(ruta_homologadas)

    # df_v701 = leer_csv(archivo_v701)

    # df_v512 = leer_csv(archivo_v512)

    # df_v557 = leer_csv(archivo_v557)

    # df_cli_impo = leer_csv(archivo_cli_impo)

    # df_cli_expo = leer_csv(archivo_cli_expo)  

    # =====================================================
    # EXCEL PRINCIPAL
    # =====================================================

    df_ds = pd.read_excel(
        archivo_base,
        sheet_name="DS"
    )

    df_homo = pd.read_csv(
        ruta_homologadas,
        sep=";",
        encoding="utf-8"
    )
    
    df_v701 = pd.read_excel(
        archivo_base,
        sheet_name="701"
    )

    df_v512 = pd.read_excel(
        archivo_base,
        sheet_name="512"
    )

    df_v557 = pd.read_excel(
        archivo_base,
        sheet_name="557"
    )


    # =====================================================
    # EXCEL CLIENTES
    # =====================================================

    df_clientes = pd.read_excel(
        archivo_clientes
    )


    # =====================================================
    # SEPARAR IMPO / EXPO
    # =====================================================

    df_cli_impo = df_clientes[
        df_clientes["TIPO"] == "IMPO"
    ].copy()

    df_cli_expo = df_clientes[
        df_clientes["TIPO"] == "EXPO"
    ].copy()


    # =====================================================
    # RETORNAR
    # =====================================================

    return {
    "df_ds": df_ds,
    "df_homo": df_homo,
    "df_v701": df_v701,
    "df_v512": df_v512,
    "df_v557": df_v557,
    "df_cli_impo": df_cli_impo,
    "df_cli_expo": df_cli_expo
} 
    
# dfs = dataframe_csv()    


def iniciar_proceso(
    archivo_base,
    archivo_clientes
):

    global dfs

    dfs = dataframe_excel(
        archivo_base, 
        archivo_clientes
    )

    df_homo = homologa()
    
    # print("COLUMNAS DF_HOMO:", df_homo.columns.tolist())

    df_cli_impo = dataframe_cliente_impo()

    df_cli_expo = dataframe_cliente_expo()

    df_cli = dataframe_Cliente()

    df_ds = dataframe_DS()

    df_virgen = dataframe_DS_Virgen()

    return {
        "df_homo": df_homo,
        "df_cli_impo": df_cli_impo,
        "df_cli_expo": df_cli_expo,
        "df_cli": df_cli,
        "df_ds": df_ds,
        "df_virgen": df_virgen
    }



def homologa():
    
    df_homo = dfs["df_homo"]
    
    return df_homo     
    
def dataframe_cliente_impo():
    
    df_cli_impo = dfs["df_cli_impo"]
    df_homo = dfs["df_homo"]
    
    # print('mensaje')

    # df_cli_impo["FRACCION"] = df_cli_impo["FRACCION"].fillna("").astype(str).str.split().str[0]
    df_cli_impo["FRACCION"] = df_cli_impo["FRACCION"].fillna("").astype(str).str[:8]
    df_cli_impo["NICO"] = (df_cli_impo["NICO"].fillna("").astype(str).str.replace(" ", "", regex=False))
    df_cli_impo["ADU-PAT-PED"] = (df_cli_impo["ADU-PAT-PED"].fillna("").astype(str).str.replace(" ", "", regex=False))
    df_cli_impo["SECUENCIA"] = (df_cli_impo["SECUENCIA"].fillna("").astype(str).str.replace(" ", "", regex=False))
    # df_cli_impo["CANTIDAD COMERCIAL"] = pd.to_numeric(df_cli_impo["CANTIDAD COMERCIAL"].astype(str).str.replace(",", "", regex=False),errors="coerce")
    df_cli_impo["CANTIDAD COMERCIAL"] = pd.to_numeric(df_cli_impo["CANTIDAD COMERCIAL"].astype(str).str.replace(",", "", regex=False), errors="coerce")


    df_cli_impo = df_cli_impo.merge(
        df_homo[
            ["Unit of Entry", "UM NORMALIZADA", "EQUIVALENTE"]
        ],  
        left_on="UNIDAD MEDIDA COMERCIAL",
        right_on="Unit of Entry",
        how="left"
    )
    
    df_cli_impo["CANT_UMC_NEW"] = (
        pd.to_numeric(df_cli_impo["CANTIDAD COMERCIAL"], errors="coerce")
        *
        pd.to_numeric(df_cli_impo["EQUIVALENTE"], errors="coerce")
    )    


    df_cli_impo["ADU-PAT-PED-HTS"] = (df_cli_impo["ADU-PAT-PED"].astype(str)+ "-"+ df_cli_impo["FRACCION"].astype(str))
    df_cli_impo["ADU-PAT-PED-HTSNICO"] = (df_cli_impo["ADU-PAT-PED-HTS"].astype(str)+ df_cli_impo["NICO"].fillna("").astype(str))
    df_cli_impo["HPH ADU-PAT-PED-HTS-SEC"] = (df_cli_impo["ADU-PAT-PED-HTS"].astype(str)+ "-"+ df_cli_impo["SECUENCIA"].astype(str))

    df_cli_impo.drop(
        columns=[
            "ADUANA",
            "PATENTE",
            # "FRACCION",
            "NICO",
            "SECUENCIA",
            "UNIDAD MEDIDA COMERCIAL",
            "CANTIDAD COMERCIAL"
        ],
        inplace=True
    )
    
    df_cli_impo.drop(columns=["Unit of Entry"], inplace=True)
    df_cli_impo.drop(columns=["EQUIVALENTE"], inplace=True)    



    # df_cli_impo["VALOR EN DOLARES"] = pd.to_numeric(
    #     df_cli_impo["VALOR EN DOLARES"].str.replace(",", "", regex=False),
    #     errors="coerce"
    # )

    df_cli_impo["VALOR EN DOLARES"] = pd.to_numeric(
        df_cli_impo["VALOR EN DOLARES"]
        .astype(str)
        .str.replace(",", "", regex=False),
        errors="coerce"
    )



    
    return df_cli_impo



def dataframe_cliente_expo():
    
    df_cli_expo = dfs["df_cli_expo"]
    df_homo = dfs["df_homo"]

    
    # df_cli_expo["FRACCION"] = df_cli_expo["FRACCION"] .fillna("").astype(str).str.split().str[0]
    df_cli_expo["FRACCION"] = df_cli_expo["FRACCION"].fillna("").astype(str).str[:8]
    df_cli_expo["NICO"] = (df_cli_expo["NICO"].fillna("").astype(str).str.replace(" ", "", regex=False))
    df_cli_expo["ADU-PAT-PED"] = (df_cli_expo["ADU-PAT-PED"].fillna("").astype(str).str.replace(" ", "", regex=False))
    df_cli_expo["SECUENCIA"] = (df_cli_expo["SECUENCIA"].fillna("").astype(str).str.replace(" ", "", regex=False))    
    # df_cli_expo["CANTIDAD COMERCIAL"] = pd.to_numeric(df_cli_expo["CANTIDAD COMERCIAL"].astype(str).str.replace(",", "", regex=False),errors="coerce")
    df_cli_expo["CANTIDAD COMERCIAL"] = pd.to_numeric(df_cli_expo["CANTIDAD COMERCIAL"].astype(str).str.replace(",", "", regex=False), errors="coerce")


    df_cli_expo = df_cli_expo.merge(
        df_homo[
            ["Unit of Entry", "UM NORMALIZADA", "EQUIVALENTE"]
        ],  
        left_on="UNIDAD MEDIDA COMERCIAL",
        right_on="Unit of Entry",
        how="left"
    )


    df_cli_expo["CANT_UMC_NEW"] = (
        pd.to_numeric(df_cli_expo["CANTIDAD COMERCIAL"], errors="coerce")
        *
        pd.to_numeric(df_cli_expo["EQUIVALENTE"], errors="coerce")
    )


    df_cli_expo["ADU-PAT-PED-HTS"] = (df_cli_expo["ADU-PAT-PED"].astype(str)+ "-"+ df_cli_expo["FRACCION"].astype(str))
    df_cli_expo["ADU-PAT-PED-HTSNICO"] = (df_cli_expo["ADU-PAT-PED-HTS"].astype(str)+ df_cli_expo["NICO"].fillna("").astype(str))
    df_cli_expo["HPH ADU-PAT-PED-HTS-SEC"] = (df_cli_expo["ADU-PAT-PED-HTS"].astype(str)+ "-"+ df_cli_expo["SECUENCIA"].astype(str))


    df_cli_expo.drop(
        columns=[
            "ADUANA",
            "PATENTE",
            # "FRACCION",
            "NICO",
            "SECUENCIA",
            "UNIDAD MEDIDA COMERCIAL",
            "CANTIDAD COMERCIAL"
        ],
        inplace=True
    )


    df_cli_expo.drop(columns=["Unit of Entry"], inplace=True)
    df_cli_expo.drop(columns=["EQUIVALENTE"], inplace=True)


    # df_cli_expo["VALOR EN DOLARES"] = pd.to_numeric(
    #     df_cli_expo["VALOR EN DOLARES"].str.replace(",", "", regex=False),
    #     errors="coerce"
    # )

    df_cli_expo["VALOR EN DOLARES"] = pd.to_numeric(
        df_cli_expo["VALOR EN DOLARES"]
        .astype(str)
        .str.replace(",", "", regex=False),
        errors="coerce"
    )



# VALOR COMERCIAL
    
    return df_cli_expo


def dataframe_Cliente():
    
    
    df_clie_impo =dataframe_cliente_impo()
    df_clie_expo =dataframe_cliente_expo()
    
    df_clie_impo["ORIGEN"] = "IMPO"
    df_clie_expo["ORIGEN"] = "EXPO"

    df_cli = pd.concat(
        [df_clie_impo, df_clie_expo],
        ignore_index=True
    )
    
    return df_cli
        
    

def dataframe_DS():
    
    df_ds = dfs["df_ds"]
    df_homo = dfs["df_homo"]
    
    
    # df_ds["CANT UMC"] = pd.to_numeric(
    #     df_ds["CANT UMC"].str.replace(",", "", regex=False),
    #     errors="coerce"
    # )

    # df_ds["VAL USD"] = pd.to_numeric(
    #     df_ds["VAL USD"].str.replace(",", "", regex=False),
    #     errors="coerce"
    # )

    df_ds["CANT UMC"] = pd.to_numeric(
        df_ds["CANT UMC"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

    df_ds["VAL USD"] = pd.to_numeric(
        df_ds["VAL USD"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )



    df_ds = df_ds.merge(
        df_homo[
            ["Unit of Entry", "UM NORMALIZADA", "EQUIVALENTE"]
        ],  
        left_on="UMC TEXTO",
        right_on="Unit of Entry",
        how="left"
    )



    df_ds["CANT_UMC_NEW"] = (
        pd.to_numeric(df_ds["CANT UMC"], errors="coerce")
        *
        pd.to_numeric(df_ds["EQUIVALENTE"], errors="coerce")
    )

    df_ds["VAL USD"] = pd.to_numeric(
        df_ds["VAL USD"],
        errors="coerce"
    )


    df_ds.drop(columns=["Unit of Entry"], inplace=True)
    # df_ds.drop(columns=["EQUIVALENTE"], inplace=True)


    
    return df_ds



def dataframe_DS_Virgen():
    
    df_v701 = dfs["df_v701"]
    df_v512 = dfs["df_v512"]
    df_v557 = dfs["df_v557"]
    
    df_v701["ADU-PAT-PED"] = (df_v701["SeccionAduanera"].astype(str)+ "-"+ df_v701["Patente"].astype(str)+ "-"+ df_v701["Pedimento"].astype(str))
    df_v701["ADU-PAT-PED ANTERIOR"] = (df_v701["SeccionAduaneraAnterior"].astype(str) + "-" + df_v701["PatenteAnterior"].astype(str)+ "-"+ df_v701["PedimentoAnterior"].astype(str))

    df_v701.drop(
        columns=[
            "Patente",
            "Pedimento",
            "SeccionAduanera",
            "PedimentoAnterior",
            "PatenteAnterior",
            "SeccionAduaneraAnterior"
        ],
        inplace=True
    )


    #######################################################################################################################################################################

    df_v512 = df_v512[
        pd.to_numeric(df_v512["UnidadMedida"], errors="coerce").notna() &
        pd.to_numeric(df_v512["MercanciaDescargada"], errors="coerce").notna() &
        (pd.to_numeric(df_v512["UnidadMedida"], errors="coerce") != 0) &
        (pd.to_numeric(df_v512["MercanciaDescargada"], errors="coerce") != 0)
    ]


    df_v512["ADU-PAT-PED"] = (df_v512["SeccionAduanera"].astype(str)+ "-"+ df_v512["Patente"].astype(str)+ "-"+ df_v512["Pedimento"].astype(str))
    df_v512["ADU-PAT-PED ANTERIOR"] = (df_v512["SeccionAduaneraDespOrig"].astype(str) + "-" + df_v512["PatenteAduanalOrig"].astype(str)+ "-"+ df_v512["PedimentoOriginal"].astype(str))

    print("UnidadMedida vacíos:", df_v512["UnidadMedida"].isna().sum())
    print("MercanciaDescargada vacíos:", df_v512["MercanciaDescargada"].isna().sum())

    df_v512.drop(
        columns=[
            "Patente",
            "Pedimento",
            "SeccionAduanera",
            "PatenteAduanalOrig",
            "PedimentoOriginal",
            "SeccionAduaneraDespOrig",
            "UnidadMedida",
            "MercanciaDescargada"
        ],
        inplace=True
    )

    df_v512 = df_v512.drop_duplicates()


    df_v512_0 = (
        df_v512.groupby(
            "ADU-PAT-PED",
            as_index=False
        )
        .agg({
            "ADU-PAT-PED ANTERIOR":
                lambda x: "|".join(x.astype(str).unique()),
            "DocumentoOriginal":
                lambda x: "|".join(x.astype(str).unique()),
            "FechaOperacionOrig":
                lambda x: "|".join(x.astype(str).unique())
        })
    )


    df_v512_1 = (
        df_v512.groupby(
            "ADU-PAT-PED ANTERIOR",
            as_index=False
        )
        .agg({
            "ADU-PAT-PED":
                lambda x: "|".join(x.astype(str).unique())
        })
    )
    
    df_v512_2 = (
        df_v512.groupby(
            "ADU-PAT-PED ANTERIOR",
            as_index=False
        )
        .agg({
            "FechaOperacionOrig":
                lambda x: " | ".join(x.astype(str).unique())
        })
    )


    #######################################################################################################################################################################


    df_v557["ADU-PAT-PED"] = (df_v557["SeccionAduanera"].astype(str)+ "-"+ df_v557["Patente"].astype(str)+ "-"+ df_v557["Pedimento"].astype(str))

    df_v557["ClaveContribucion"] = pd.to_numeric(df_v557["ClaveContribucion"],errors="coerce")
    df_v557["FormaPago"] = pd.to_numeric(df_v557["FormaPago"],errors="coerce")
    df_v557["ImportePago"] = pd.to_numeric(df_v557["ImportePago"],errors="coerce")


    df_v557_pago_0 = (
        df_v557[
            (df_v557["ClaveContribucion"] == 6)
            &
            (
                (df_v557["FormaPago"] == 0)
                |
                (df_v557["FormaPago"].isna())
            )
        ]
        .groupby("ADU-PAT-PED", as_index=False)["ImportePago"]
        .sum()
    )


    df_v557_pago_5 = (
        df_v557[
            (df_v557["ClaveContribucion"] == 6)
            &
            (df_v557["FormaPago"] == 5)
        ]
        .groupby("ADU-PAT-PED", as_index=False)["ImportePago"]
        .sum()
    )

    df_v557_pago_6 = (
        df_v557[
            (df_v557["ClaveContribucion"] == 6)
            &
            (df_v557["FormaPago"] == 6)
        ]
        .groupby("ADU-PAT-PED", as_index=False)["ImportePago"]
        .sum()
    )    
    
    
    return {
    "df_v701": df_v701,
    "df_v512": df_v512,
    "df_v512_0": df_v512_0,
    "df_v512_1": df_v512_1,
    "df_v512_2": df_v512_2,    
    "df_v557": df_v557,
    "df_v557_pago_0": df_v557_pago_0,
    "df_v557_pago_5": df_v557_pago_5,
    "df_v557_pago_6": df_v557_pago_6
}  