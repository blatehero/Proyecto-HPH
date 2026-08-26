import pandas as pd
from datetime import datetime
import numpy as np
# pd.set_option("display.precision", 10)

ruta= r"C:/Users/User/OneDrive/Proyecto/PYTHON/Proyecto HPH/CROSS X/inputs/"

# def leer_csv(ruta):

#     with open(ruta, "r", encoding="utf-8") as f:
#         encabezado = f.readline()

#     separador = ";" if encabezado.count(";") > encabezado.count(",") else ","

#     return pd.read_csv(
#         ruta,
#         sep=separador,
#         dtype=str
#     )

def leer_csv(ruta):

    with open(ruta, "r", encoding="utf-8") as f:
        encabezado = f.readline()

    if encabezado.count("|") > max(encabezado.count(";"), encabezado.count(",")):
        separador = "|"
    elif encabezado.count(";") > encabezado.count(","):
        separador = ";"
    else:
        separador = ","

    return pd.read_csv(
        ruta,
        sep=separador,
        dtype=str
    )

def limpiar_campo(valor):

    if valor is None:
        return ""

    return str(valor).strip()




def dataframe_csv():
    
    df_ds = leer_csv(ruta + "DS - METHODE.csv")

    df_homo = leer_csv(ruta + "UND HOMOLOGADAS.csv")

    df_v701 = leer_csv(ruta + "DS VIRGEN 701.csv")

    df_v512 = leer_csv(ruta + "DS VIRGEN 512.csv")

    df_v557 = leer_csv(ruta + "DS VIRGEN 557.csv")

    df_cli_impo = leer_csv(ruta + "CLIENTE_IMPO - METHODE.csv")

    df_cli_expo = leer_csv(ruta + "CLIENTE_EXPO - METHODE.csv")    

    return {
    "df_ds": df_ds,
    "df_homo": df_homo,
    "df_v701": df_v701,
    "df_v512": df_v512,
    "df_v557": df_v557,
    "df_cli_impo": df_cli_impo,
    "df_cli_expo": df_cli_expo
} 
    
dfs = dataframe_csv()    

def homologa():
    
    df_homo = dfs["df_homo"]
    
    return df_homo     
    
def dataframe_cliente_impo():
    
    df_cli_impo = dfs["df_cli_impo"]
    df_homo = dfs["df_homo"]
    

    # df_cli_impo["FRACCION"] = df_cli_impo["FRACCION"].fillna("").astype(str).str.split().str[0]
    df_cli_impo["FRACCION"] = df_cli_impo["FRACCION"].fillna("").astype(str).str[:8]
    df_cli_impo["NICO"] = (df_cli_impo["NICO"].fillna("").astype(str).str.replace(" ", "", regex=False))
    df_cli_impo["ADU-PAT-PED"] = (df_cli_impo["ADU-PAT-PED"].fillna("").astype(str).str.replace(" ", "", regex=False))
    df_cli_impo["SECUENCIA"] = (df_cli_impo["SECUENCIA"].fillna("").astype(str).str.replace(" ", "", regex=False))
    df_cli_impo["CANTIDAD COMERCIAL"] = pd.to_numeric(df_cli_impo["CANTIDAD COMERCIAL"].str.replace(",", "", regex=False),errors="coerce")


    df_cli_impo = df_cli_impo.merge(
        df_homo[
            ["Unit of Entry", "UM NORMALIZADA", "EQUIVALENTE"]
        ],  
        left_on="UNIDAD MEDIDA COMERNCIAL",
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
            "UNIDAD MEDIDA COMERNCIAL",
            "CANTIDAD COMERCIAL"
        ],
        inplace=True
    )
    
    df_cli_impo.drop(columns=["Unit of Entry"], inplace=True)
    df_cli_impo.drop(columns=["EQUIVALENTE"], inplace=True)    



    df_cli_impo["VALOR EN DOLARES"] = pd.to_numeric(
        df_cli_impo["VALOR EN DOLARES"].str.replace(",", "", regex=False),
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
    df_cli_expo["CANTIDAD COMERCIAL"] = pd.to_numeric(df_cli_expo["CANTIDAD COMERCIAL"].str.replace(",", "", regex=False),errors="coerce")


    df_cli_expo = df_cli_expo.merge(
        df_homo[
            ["Unit of Entry", "UM NORMALIZADA", "EQUIVALENTE"]
        ],  
        left_on="UNIDAD MEDIDA COMERNCIAL",
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
            "UNIDAD MEDIDA COMERNCIAL",
            "CANTIDAD COMERCIAL"
        ],
        inplace=True
    )


    df_cli_expo.drop(columns=["Unit of Entry"], inplace=True)
    df_cli_expo.drop(columns=["EQUIVALENTE"], inplace=True)


    df_cli_expo["VALOR EN DOLARES"] = pd.to_numeric(
        df_cli_expo["VALOR EN DOLARES"].str.replace(",", "", regex=False),
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
    
    
    df_ds["CANT UMC"] = pd.to_numeric(
        df_ds["CANT UMC"].str.replace(",", "", regex=False),
        errors="coerce"
    )

    df_ds["VAL USD"] = pd.to_numeric(
        df_ds["VAL USD"].str.replace(",", "", regex=False),
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