import pandas as pd
from datetime import datetime
import numpy as np

def crearDfCliente(df_cli):

    df_cli=df_cli.copy()
    
    df_cli_group = (
        df_cli.groupby(
            ["ADU-PAT-PED"],
            as_index=False
        )["VALOR EN DOLARES"]
        .sum()
    )
    
    return df_cli_group

def crearDfDS(df_ds):

    df_ds=df_ds.copy()

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

    df_ds["DS PAT-PED-HTSNICO"] = (
        df_ds["ADU-PAT-PED-HTSNICO"]
        .str.split("-", n=1)
        .str[1]
    )
    
    return df_ds


def creacionDatosBasicosCross(df_ds):
    
    df_ds = df_ds.copy()
    
    df_ds_group = (
        df_ds.groupby(
            ["DS PAT-PED", "PEDIMENTO", "ADU-PAT-PED","CLAVE PED","FECHA PAGO 551"],
            as_index=False
        )["VAL USD"]
        .sum()
    )

    df_ds_group_fechas = (
        df_ds[
            ["ADU-PAT-PED", "FECHAENTRADA506", "FECHAPRESENTACION506"]
        ]
        .drop_duplicates()
    )

    df_ds_group_AF = (
        df_ds[
            ["ADU-PAT-PED", "AF"]
        ]
        .drop_duplicates()
    )    


    df_ds_group = df_ds_group.merge(
        df_ds_group_fechas[
            ["ADU-PAT-PED", "FECHAENTRADA506", "FECHAPRESENTACION506"]
        ],
        on="ADU-PAT-PED",
        how="left"
    )

    df_ds_group["FECHA ENTRADA O PRESENTACIÓN"] = np.where(
        df_ds_group["CLAVE PED"].str.startswith("1"),
        df_ds_group["FECHAENTRADA506"],
        df_ds_group["FECHAPRESENTACION506"]
    )

    df_ds_group.drop(
        columns=["FECHAENTRADA506", "FECHAPRESENTACION506"],
        inplace=True
    )

    df_ds_group = df_ds_group.merge(
        df_ds_group_AF[
            ["ADU-PAT-PED", "AF"]
        ],
        on="ADU-PAT-PED",
        how="left"
    )    

    return df_ds_group


def creacionColumnasDsVigen(df_ds_group,dataframe_DS_Virgen):

    df_ds_group=df_ds_group.copy()
    dataframe_DS_Virgen=dataframe_DS_Virgen.copy()

    df_v701 = dataframe_DS_Virgen["df_v701"]
    df_v557_pago_0 = dataframe_DS_Virgen["df_v557_pago_0"]
    df_v557_pago_5 = dataframe_DS_Virgen["df_v557_pago_5"]
    df_v557_pago_6 = dataframe_DS_Virgen["df_v557_pago_6"]
    df_v512_0 = dataframe_DS_Virgen["df_v512_0"]
    df_v512_1 = dataframe_DS_Virgen["df_v512_1"]
    df_v512_2 = dataframe_DS_Virgen["df_v512_2"]



    codigo = df_ds_group["CLAVE PED"].str[2:4]

    cond_clave_immex = [
        (
            codigo.isin(["AF", "F5", "BO"])
            |
            (
                (df_ds_group["AF"] == "AF")
                & (codigo != "A1")
            )
        ),
        codigo == "A1",
        codigo.isin(["IN", "RT", "V1", "A6", "H1", "F4", "A3", "V5"]),
        codigo.isin(["I1", "K1", "BA", "BM", "D1"])
    ]

    resultados = [
        "IMMEX AF",
        "NO IMMEX",
        "UNIVERSO IMMEX",
        "OTRAS CLAVES"
    ]

    df_ds_group["CLAVES IMMEX"] = np.select(
        cond_clave_immex,
        resultados,
        default=""
    )


    ###########################################################################################################################################

    df_ds_group = df_ds_group.merge(
        df_v701[
            ["ADU-PAT-PED", "ADU-PAT-PED ANTERIOR"]
        ].rename(
            columns={
                "ADU-PAT-PED ANTERIOR": "VAL6"
            }
        ),
        left_on="ADU-PAT-PED",
        right_on="ADU-PAT-PED",
        how="left"
    )

    df_ds_group = df_ds_group.merge(
        df_v701[
            ["ADU-PAT-PED ANTERIOR", "ADU-PAT-PED"]
        ].rename(
            columns={
                "ADU-PAT-PED": "VAL8"
            }
        ),
        left_on="ADU-PAT-PED",
        right_on="ADU-PAT-PED ANTERIOR",
        how="left"
    )

    df_ds_group.drop(columns=["ADU-PAT-PED ANTERIOR"], inplace=True)

    df_ds_group["VAL6"] = df_ds_group["VAL6"].fillna("NO ES R1")
    df_ds_group["VAL8"] = df_ds_group["VAL8"].fillna("NO TUVO R1")


    ###########################################################################################################################################

    # df_v557_pago_0
    # df_v557_pago_5
    # df_v557_pago_6

    df_ds_group = df_ds_group.merge(
        df_v557_pago_0[
            ["ADU-PAT-PED", "ImportePago"]
        ].rename(
            columns={
                "ImportePago": "VAL10"
            }
        ),
        left_on="ADU-PAT-PED",
        right_on="ADU-PAT-PED",
        how="left"
    )

    df_ds_group = df_ds_group.merge(
        df_v557_pago_5[
            ["ADU-PAT-PED", "ImportePago"]
        ].rename(
            columns={
                "ImportePago": "VAL11"
            }
        ),
        left_on="ADU-PAT-PED",
        right_on="ADU-PAT-PED",
        how="left"
    )

    df_ds_group = df_ds_group.merge(
        df_v557_pago_6[
            ["ADU-PAT-PED", "ImportePago"]
        ].rename(
            columns={
                "ImportePago": "VAL12"
            }
        ),
        left_on="ADU-PAT-PED",
        right_on="ADU-PAT-PED",
        how="left"
    )


    ###########################################################################################################################################

    df_ds_group = df_ds_group.merge(
        df_v512_0[
            [
                "ADU-PAT-PED",
                "ADU-PAT-PED ANTERIOR",
                "DocumentoOriginal" #,
                # "FechaOperacionOrig"
            ]
        ].rename(
            columns={
                "ADU-PAT-PED ANTERIOR": "VAL13",
                "DocumentoOriginal": "VAL14" #,
                # "FechaOperacionOrig": "VAL15"
            }
        ),
        on="ADU-PAT-PED",
        # right_on="ADU-PAT-PED",
        how="left"
    )

    indice_fecha = (
        df_v512_2
        .set_index("ADU-PAT-PED ANTERIOR")["FechaOperacionOrig"]
        .to_dict()
    )

    df_ds_group["VAL15"] = (
        df_ds_group["VAL13"]
        .fillna("")
        .astype(str)
        .apply(
            lambda x: "|".join(
                str(indice_fecha[c.strip()])
                for c in x.split("|")
                if c.strip() in indice_fecha
            )
            if x else ""
        )
    )


    df_ds_group["VAL13"] = df_ds_group["VAL13"].fillna("NO ES DESCARGA")
    df_ds_group["VAL14"] = df_ds_group["VAL14"].fillna("")
    df_ds_group["VAL15"] = df_ds_group["VAL15"].fillna("")



    df_ds_group = df_ds_group.merge(
        df_v512_1[
            [
                "ADU-PAT-PED ANTERIOR",
                "ADU-PAT-PED"
            ]
        ].rename(
            columns={
                "ADU-PAT-PED": "VAL17"
            }
        ),
        left_on="ADU-PAT-PED",
        right_on="ADU-PAT-PED ANTERIOR",
        how="left"
    )


    # ---------------------------------------------------------------------

    df_ds_group["VAL17"] = df_ds_group["VAL17"].fillna("NO DESCARGO")

    indice_clave_ped = (
        df_ds_group
        .set_index("ADU-PAT-PED")["CLAVE PED"]
        .to_dict()
    )

    claves_ped = (
        df_ds_group["VAL17"]
        .astype(str)
        .apply(
            lambda x: "|".join(
                indice_clave_ped[p.strip()]
                for p in x.split("|")
                if p.strip() in indice_clave_ped
            )
        )
    )

    df_ds_group["VAL17"] = np.where(
        df_ds_group["VAL17"] == "NO DESCARGO",
        "NO DESCARGO",
        df_ds_group["VAL17"] + " / " + claves_ped
    )


    # -----------------------------------------------------------------------

    df_ds_group.drop(columns=["ADU-PAT-PED ANTERIOR"], inplace=True)   
    
    return df_ds_group 



def mergeCliente_DS(df_ds_group, df_cli_group):

    df_ds_group=df_ds_group.copy()
    df_cli_group=df_cli_group.copy()
    
    df_ds_group = df_ds_group.merge(
        df_cli_group[
            ["ADU-PAT-PED", "VALOR EN DOLARES"]
        ].rename(
            columns={
                "VALOR EN DOLARES": "VAL22"
            }
        ),
        left_on="ADU-PAT-PED",
        right_on="ADU-PAT-PED",
        how="left"
    )


    dif_real = df_ds_group["VAL USD"] - df_ds_group["VAL22"].fillna(0)

    df_ds_group["VAL23"] = np.where(
        dif_real.between(-2, 2),
        0,
        dif_real
    )

    df_ds_group["VAL24"] = df_ds_group["VAL23"].abs()


    df_ds_group["VAL25"] = np.where(
        (df_ds_group["VAL22"].isna()) |
        (df_ds_group["VAL USD"] < 2),
        "",
        np.where(
            (
                (df_ds_group["VAL USD"] - df_ds_group["VAL24"] > -1)
                &
                (df_ds_group["VAL USD"] - df_ds_group["VAL24"] < 1)
                &
                (df_ds_group["VAL22"] > 3)
            ),
            "Duplicado",
            ""
        )
    )

    return df_ds_group


def estatus_global_monto(df_ds_group):
    
    df_ds_group=df_ds_group.copy()
    
    # pd.set_option("display.max_columns", None)
    # =========================
    # VARIABLES AUXILIARES
    # =========================
    clave_immmex = df_ds_group["CLAVES IMMEX"]
    f4 = df_ds_group["VAL6"] != "NO ES R1"
    h4 = df_ds_group["VAL8"] != "NO TUVO R1"
    val_usd_ds = df_ds_group["VAL USD"]
    val_usd_cli = df_ds_group["VAL22"]      # V4
    dif_real = df_ds_group["VAL23"]           # W4
    duplicado = df_ds_group["VAL25"].eq("Duplicado")

    # Para la regla del 99%
    ratio = np.where(
        val_usd_cli.notna() & (val_usd_cli != 0),
        val_usd_ds / val_usd_cli - 1,
        np.nan
    )

    # =========================
    # CONDICIONES EN EL MISMO ORDEN DEL EXCEL
    # =========================
    condiciones = [

        # =========================================================
        # 1) DUPLICADO
        # =SI(Y4="DUPLICADO";A4&"-DUPLICADO";...)
        # =========================================================
        duplicado,

        # =========================================================
        # 2) ES R1 Y TUVO R1
        # =========================================================

        # V4=""
        (~duplicado) & f4 & h4 & val_usd_cli.isna(),

        # Y(V4<>"";W4>=-2;W4<=2)
        (~duplicado) & f4 & h4 & val_usd_cli.notna() & dif_real.between(-2, 2),

        # Y(V4<>"";U4/V4-1>=-1%;U4/V4-1<=1%)
        (~duplicado) & f4 & h4 & val_usd_cli.notna() & (ratio >= -0.01) & (ratio <= 0.01),

        # Y(V4<>"";V4>U4)
        (~duplicado) & f4 & h4 & val_usd_cli.notna() & (val_usd_cli > val_usd_ds),

        # Y(V4<>"";V4<U4)
        (~duplicado) & f4 & h4 & val_usd_cli.notna() & (val_usd_cli < val_usd_ds),

        # =========================================================
        # 3) F4 <> "NO ES R1"
        # =========================================================

        # V4=""
        (~duplicado) & f4 & (~h4) & val_usd_cli.isna(),

        # Y(V4<>"";W4>=-2;W4<=2)
        (~duplicado) & f4 & (~h4) & val_usd_cli.notna() & dif_real.between(-2, 2),

        # Y(V4<>"";U4/V4-1>=-1%;U4/V4-1<=1%)
        (~duplicado) & f4 & (~h4) & val_usd_cli.notna() & (ratio >= -0.01) & (ratio <= 0.01),

        # Y(V4<>"";V4>U4)
        (~duplicado) & f4 & (~h4) & val_usd_cli.notna() & (val_usd_cli > val_usd_ds),

        # Y(V4<>"";V4<U4)
        (~duplicado) & f4 & (~h4) & val_usd_cli.notna() & (val_usd_cli < val_usd_ds),


        # =========================================================
        # 4) TUVO R1
        # =========================================================

        # V4=""
        (~duplicado) & (~f4) & h4 & val_usd_cli.isna(),

        # Y(V4<>"";W4>=-2;W4<=2)
        (~duplicado) & (~f4) & h4 & val_usd_cli.notna() & dif_real.between(-2, 2),

        # Y(V4<>"";U4/V4-1>=-1%;U4/V4-1<=1%)
        (~duplicado) & (~f4) & h4 & val_usd_cli.notna() & (ratio >= -0.01) & (ratio <= 0.01),

        # Y(V4<>"";V4>U4)
        (~duplicado) & (~f4) & h4 & val_usd_cli.notna() & (val_usd_cli > val_usd_ds),

        # Y(V4<>"";V4<U4)
        (~duplicado) & (~f4) & h4 & val_usd_cli.notna() & (val_usd_cli < val_usd_ds),

        # =========================================================
        # 5) NORMAL
        # =========================================================

        # V4=""
        (~duplicado) & (~f4) & (~h4) & val_usd_cli.isna(),

        # Y(V4<>"";W4>=-2;W4<=2)
        (~duplicado) & (~f4) & (~h4) & val_usd_cli.notna() & dif_real.between(-2, 2),

        # Y(V4<>"";U4/V4-1>=-1%;U4/V4-1<=1%)
        (~duplicado) & (~f4) & (~h4) & val_usd_cli.notna() & (ratio >= -0.01) & (ratio <= 0.01),

        # Y(V4<>"";V4>U4)
        (~duplicado) & (~f4) & (~h4) & val_usd_cli.notna() & (val_usd_cli > val_usd_ds),

        # Y(V4<>"";V4<U4)
        (~duplicado) & (~f4) & (~h4) & val_usd_cli.notna() & (val_usd_cli < val_usd_ds),
    ]

    # =========================
    # RESULTADOS EN EL MISMO ORDEN
    # =========================
    resultados = [

        # 1) DUPLICADO
        clave_immmex + "-DUPLICADO",

        # 2) ES R1 Y TUVO R1
        clave_immmex + "-ES R1 Y TUVO A SU VEZ R1-PEDIMENTO FALTANTE EN BASE",
        clave_immmex + "-ES R1 Y TUVO A SU VEZ R1-100% CORRECTO EN VALOR",
        clave_immmex + "-ES R1 Y TUVO A SU VEZ R1-99% CORRECTO EN VALOR",
        clave_immmex + "-ES R1 Y TUVO A SU VEZ R1-LE SOBRA VALOR EN BASE",
        clave_immmex + "-ES R1 Y TUVO A SU VEZ R1-LE FALTA VALOR EN BASE",

        # 3) ES R1
        clave_immmex + "-ES R1-PEDIMENTO FALTANTE EN BASE",
        clave_immmex + "-ES R1-100% CORRECTO EN VALOR",
        clave_immmex + "-ES R1-99% CORRECTO EN VALOR",
        clave_immmex + "-ES R1-LE SOBRA VALOR EN BASE",
        clave_immmex + "-ES R1-LE FALTA VALOR EN BASE",

        # 4) TUVO R1
        clave_immmex + "-TUVO R1-PEDIMENTO FALTANTE EN BASE",
        clave_immmex + "-TUVO R1-100% CORRECTO EN VALOR",
        clave_immmex + "-TUVO R1-99% CORRECTO EN VALOR",
        clave_immmex + "-TUVO R1-LE SOBRA VALOR EN BASE",
        clave_immmex + "-TUVO R1-LE FALTA VALOR EN BASE",

        # 5) NORMAL
        clave_immmex + "-PEDIMENTO FALTANTE EN BASE",
        clave_immmex + "-100% CORRECTO EN VALOR",
        clave_immmex + "-99% CORRECTO EN VALOR",
        clave_immmex + "-LE SOBRA VALOR EN BASE",
        clave_immmex + "-LE FALTA VALOR EN BASE",
    ]

    # =========================
    # COLUMNA FINAL
    # =========================
    df_ds_group["VAL26"] = np.select(condiciones, resultados, default="")


    dic = df_ds_group.set_index("ADU-PAT-PED")["VAL26"]

    df_ds_group["VAL7"] = (
        df_ds_group["VAL6"]
        .map(dic)
        .fillna("NO SE REQUIERE")
    )


    df_ds_group["VAL9"] = (
        df_ds_group["VAL8"]
        .map(dic)
        .fillna("NO SE REQUIERE")
    )
    
    return df_ds_group



def obs_globales_r1(df_ds_group):
    
    df_ds_group=df_ds_group.copy()
    # ===========================================================
    # VARIABLES
    # ===========================================================

    e4 = df_ds_group["CLAVE PED"]
    g4 = df_ds_group["VAL7"]
    i4 = df_ds_group["VAL9"]
    m4 = df_ds_group["VAL13"]
    z4 = df_ds_group["VAL26"]

    # ===========================================================
    # FUNCIÓN PARA OBTENER EL ESTATUS
    # (Replica los SUSTITUIR + TEXTODESPUES de Excel)
    # ===========================================================

    def obtener_estatus(col):

        return (
            col.fillna("")
            .astype(str)
            .str.replace("-ES R1 Y TUVO A SU VEZ R1", "", regex=False)
            .str.replace("-TUVO R1", "", regex=False)
            .str.replace("-ES R1", "", regex=False)
            .str.split("-", n=1)
            .str[-1]
            .str.strip()
        )

    estatus_g = obtener_estatus(g4)
    estatus_i = obtener_estatus(i4)
    estatus_z = obtener_estatus(z4)

    # Texto después del "-" SIN eliminar las etiquetas
    estatus_original = (
        z4.fillna("")
        .astype(str)
        .str.split("-", n=1)
        .str[-1]
        .str.strip()
    )

    # ===========================================================
    # MÁSCARAS DE VACÍO (Excel "" = NaN o "")
    # ===========================================================

    vacio_z = z4.isna() | (z4 == "")
    no_vacio_z = ~vacio_z

    vacio_g = g4.isna() | (g4 == "")
    no_vacio_g = ~vacio_g

    vacio_i = i4.isna() | (i4 == "")
    no_vacio_i = ~vacio_i

    # ===========================================================
    # CONDICIONES PRINCIPALES
    # ===========================================================

    usa_i = (
        (i4 != "NO SE REQUIERE")
        & no_vacio_z
    )

    usa_g = (
        (i4 == "NO SE REQUIERE")
        & (g4 != "NO SE REQUIERE")
        & no_vacio_z
    )

    correcto_i = estatus_i.eq("100% CORRECTO EN VALOR")
    correcto_g = estatus_g.eq("100% CORRECTO EN VALOR")
    correcto_z = estatus_z.eq("100% CORRECTO EN VALOR")

    # ===========================================================
    # CONSTRUCCIÓN DE A
    # ===========================================================

    A = np.select(

        [

            # -------------------------------------------------
            # VAL9
            # -------------------------------------------------

            usa_i & correcto_i & correcto_z,

            usa_i & correcto_i & (~correcto_z),

            usa_i & (~correcto_i) & (~correcto_z),

            # -------------------------------------------------
            # VAL7
            # -------------------------------------------------

            usa_g & correcto_g & correcto_z,

            usa_g & (~correcto_g) & correcto_z,

            usa_g & (~correcto_z)

        ],

        [

            "ORIGINAL Y R1 100% CORRECTOS",

            "EL ORIGINAL TIENE EL ESTATUS DE: "
            + estatus_original
            + " PERO SU R1 ESTA 100% CORRECTO",

            "NI EL ORIGINAL NI EL R1 ESTAN CORRECTOS",

            "ORIGINAL Y R1 100% CORRECTOS",

            "ESTE R1 ESTA 100% BIEN PERO SU ORIGINAL: "
            + g4.fillna("").astype(str),

            "NI EL R1 NI EL ORIGINAL ESTAN BIEN, R1 CON ESTATUS:"
            + estatus_original
            + " Y ORIGINAL CON ESTATUS "
            + g4.fillna("").astype(str)

        ],

        default=""

    )

    # ===========================================================
    # SI A QUEDÓ VACÍO -> ESTATUS ORIGINAL
    # ===========================================================

    A = np.where(

        (A == "") | pd.isna(A),

        estatus_original,

        A

    )

    # ===========================================================
    # REGLA FINAL DEL PEDIMENTO
    # ===========================================================

    tipo = e4.fillna("").astype(str).str[2:4]

    condicion_anexo = (

        (m4 != "NO ES DESCARGA")
        & ~(m4.isna() | (m4 == ""))
        & tipo.isin(["F5", "A3", "F4"])

    )

    resultado = np.where(

        condicion_anexo,

        tipo
        + "-"
        + A
        + "-SE SUGIERE MONTAR EL PEDIMENTO "
        + m4.fillna("").astype(str)
        + " PARA ANEXO 30",

        A

    )

    df_ds_group["VAL27"] = resultado    
    
    return df_ds_group


def obtener_estatus(col):

    return (
        col.fillna("")
           .astype(str)
           .str.replace("-ES R1 Y TUVO A SU VEZ R1", "", regex=False)
           .str.replace("-TUVO R1", "", regex=False)
           .str.replace("-ES R1", "", regex=False)
           .str.split("-", n=1)
           .str[-1]
           .str.strip()
    )

def obs_globales_r1_etiqueta_anterior(df_ds_group):
    
    df_ds_group=df_ds_group.copy()
    # ===========================================================
    # VARIABLES
    # ===========================================================

    a4 = df_ds_group["CLAVES IMMEX"]          # <-- Reemplazar por el nombre real de la columna
    g4 = df_ds_group["VAL7"]
    i4 = df_ds_group["VAL9"]
    z4 = df_ds_group["VAL26"]

    # ===========================================================
    # FUNCIÓN PARA LIMPIAR EL ESTATUS
    # ===========================================================



    estatus_g = obtener_estatus(g4)
    estatus_i = obtener_estatus(i4)
    estatus_z = obtener_estatus(z4)

    # ===========================================================
    # VACÍOS (Excel "" = NaN o "")
    # ===========================================================

    vacio_z = z4.isna() | (z4 == "")
    no_vacio_z = ~vacio_z

    # ===========================================================
    # CONDICIONES
    # ===========================================================

    usa_i = (
        (i4 != "NO SE REQUIERE")
        & no_vacio_z
    )

    usa_g = (
        (i4 == "NO SE REQUIERE")
        & (g4 != "NO SE REQUIERE")
        & no_vacio_z
    )

    correcto_i = estatus_i.eq("100% CORRECTO EN VALOR")
    correcto_g = estatus_g.eq("100% CORRECTO EN VALOR")
    correcto_z = estatus_z.eq("100% CORRECTO EN VALOR")

    # ===========================================================
    # VAL28
    # ===========================================================

    val28 = np.select(

        [

            # ------------------------------------------
            # BLOQUE VAL9
            # ------------------------------------------

            usa_i & correcto_i & correcto_z,

            usa_i & correcto_i & (~correcto_z),

            usa_i & (~correcto_i) & (~correcto_z),

            # ------------------------------------------
            # BLOQUE VAL7
            # ------------------------------------------

            usa_g & correcto_g & correcto_z,

            usa_g & (~correcto_g) & correcto_z,

            usa_g & (~correcto_z)

        ],

        [

            "ORIGINAL Y R1 100% CORRECTOS",

            "EL ORIGINAL TIENE EL ESTATUS DE: "
            + z4.fillna("").astype(str)
            + " PERO SU R1 ESTA 100% CORRECTO",

            a4.fillna("").astype(str)
            + "-NI EL ORIGINAL NI EL R1 ESTAN CORRECTOS",

            "ORIGINAL Y R1 100% CORRECTOS",

            "ESTE R1 ESTA 100% BIEN PERO SU ORIGINAL: "
            + g4.fillna("").astype(str),

            "NI EL R1 NI EL ORIGINAL ESTAN BIEN, R1 CON ESTATUS:"
            + z4.fillna("").astype(str)
            + " Y ORIGINAL CON ESTATUS "
            + g4.fillna("").astype(str)

        ],

        default=""

    )

    # ===========================================================
    # SI QUEDÓ VACÍO -> DEVOLVER Z4
    # ===========================================================

    val28 = np.where(

        (val28 == "") | pd.isna(val28),

        z4.fillna("").astype(str),

        val28

    )

    # ===========================================================
    # RESULTADO
    # ===========================================================

    df_ds_group["VAL28"] = val28
    
    return df_ds_group


def actividad_empresa(df_ds_group):
    
    df_ds_group=df_ds_group.copy()
    # ===========================================================
    # VARIABLES
    # ===========================================================

    a4 = df_ds_group["CLAVES IMMEX"]      # <-- Reemplazar por el nombre real
    ab4 = df_ds_group["VAL28"]  # O el nombre de la columna correspondiente

    # ===========================================================
    # EVITAR NaN
    # ===========================================================

    a4_txt = a4.fillna("").astype(str)
    ab4_txt = ab4.fillna("").astype(str)

    # ===========================================================
    # CONDICIONES
    # ===========================================================

    es_immex = a4_txt.isin(["UNIVERSO IMMEX", "IMMEX AF"])

    contiene_100 = ab4_txt.str.contains("100%", regex=False, na=False)

    tiene_dos_puntos = ab4_txt.str.contains(":", regex=False, na=False)

    texto_antes = np.where(
        tiene_dos_puntos,
        ab4_txt.str.split(":", n=1).str[0].str.strip(),
        ""
    )

    # ===========================================================
    # MENSAJE BASE
    # ===========================================================

    mensaje = np.select(

        [

            ab4_txt.eq("UNIVERSO IMMEX-NI EL ORIGINAL NI EL R1 ESTAN CORRECTOS"),

            texto_antes == "EL ORIGINAL TIENE EL ESTATUS DE",

            texto_antes == "ESTE R1 ESTA 100% BIEN PERO SU ORIGINAL",

            texto_antes == "NI EL R1 NI EL ORIGINAL ESTAN BIEN, R1 CON ESTATUS"

        ],

        [

            "CORREGIR R1 Y OPTATIVAMENTE SU ORIGINAL",

            "TUVO R1 100% BIEN, OPTATIVO SUBIR ORIGINAL, SI SE QUIERE SUBIR CORREGIRLO",

            "SOLAMENTE SI SE OPTA POR SUBIR EL ORIGINAL, SE REQUERIRA SU CORRECCIÓN, PERO TUVO R1 Y EL R1 ESTA 100% BIEN",

            "PROPORCIONAR AL MENOS EL R1 CORREGIDO Y OPTATIVAMENTE TAMBIEN SU ORIGINAL"

        ],

        default=""

    )

    # ===========================================================
    # REGLA ESPECIAL IMMEX
    # ===========================================================

    val29 = np.where(

        es_immex
        &
        (~contiene_100)
        &
        (mensaje == ""),

        "SE REQUIERE CORRECIÓN CON BASE EN OBSERVACIÓN COLUMNA ANTERIOR",

        mensaje

    )

    # ===========================================================
    # RESULTADO
    # ===========================================================

    df_ds_group["VAL29"] = val29


    fechas = (
        df_ds_group["VAL15"]
        .fillna("")
        .astype(str)
        .str.split("|")
    )

    fecha_limite = pd.Timestamp("2014-12-31")

    mask_anterior_2015 = fechas.apply(
        lambda x: any(
            pd.to_datetime(f.strip(), dayfirst=True, errors="coerce") <= fecha_limite
            for f in x
            if f.strip()
        )
    )

    indice_val29 = (
        df_ds_group
        .set_index("ADU-PAT-PED")["VAL29"]
        .to_dict()
    )

    df_ds_group["VAL16"] = np.where(
        fechas.str.join("").eq(""),
        "",
        np.where(
            mask_anterior_2015,
            "ORIGINAL ANTERIOR AL 2015",
            df_ds_group["VAL13"]
                .map(indice_val29)
                .fillna("PEDIMENTO NO ENCONTRADO EN DS 551")
        )
    )
    
    return df_ds_group    


# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================

def buscar_original(clave, indice_originales):
    """
    Devuelve el VAL22 y VAL23 del pedimento original.
    """
    dato = indice_originales.get(clave)

    if dato is None:
        return "", ""

    return dato["VAL22"], dato["VAL23"]


def texto(v):
    if pd.isna(v):
        return ""
    return str(v).strip()


def estado_valor(valor, inclusivo=False):
    """
    Devuelve:
        correcto
        sobra
        falta

    inclusivo=True  -> [-1,1]
    inclusivo=False -> (-1,1)
    """

    valor = pd.to_numeric(valor, errors="coerce")

    if pd.isna(valor):
        return "correcto"

    if inclusivo:
        if -1 <= valor <= 1:
            return "correcto"
    else:
        if -1 < valor < 1:
            return "correcto"

    if valor <= -1:
        return "sobra"

    return "falta"


# ==========================================================
# LÓGICA PRINCIPAL
# ==========================================================

def evaluar(fila,indice_originales):

    immex = texto(fila["CLAVES IMMEX"]).upper()
    clave_ped = texto(fila["CLAVE PED"]).upper()
    val23 = fila["VAL23"]

    nombre = fila["CLAVES IMMEX"]

    # ------------------------------------------------------

    if immex in ("NO IMMEX", "OTRAS CLAVES"):
        return "NO IMMEX U OTRAS CLAVES. NO REQUIEREN ACTIVIDAD"

    # ------------------------------------------------------

    if immex == "GC":
        return f"{nombre}: ACCION REQUERIDA: PROPORCIONAR PDF DEL PEDIMENTO GC"

    # ------------------------------------------------------
    # Datos del original
    # ------------------------------------------------------

    clave_original = clave_ped[-16:]

    val22_original, val23_original = buscar_original(clave_original,indice_originales)

    original_existe = texto(val22_original) != ""

    # ------------------------------------------------------
    # Banderas
    # ------------------------------------------------------

    es_tuvo = "TUVO" in clave_ped
    es_r1 = "-R1-" in clave_ped

    r1_capturado = texto(fila["VAL22"]) != ""

    estado_original = estado_valor(val23_original, inclusivo=True)
    estado_r1 = estado_valor(val23, inclusivo=False)
    estado_r1_inclusivo = estado_valor(val23, inclusivo=True)

    # ======================================================
    # TUVO R1
    # ======================================================

    if es_tuvo:

        if r1_capturado:
            return (
                f"{nombre}: ESTE PED TUVO R1 PERO ESTÁ CAPTURADO. "
                "ACCION REQUERIDA: ASEGURARSE DE ELIMINARLO O DE QUE "
                "EL SOFTWARE NO LO TOME EN CUENTA PARA DESCARGAR"
            )

        if not original_existe:
            return (
                f"{nombre}: ESTE PED TUVO R1, "
                "PERO SU R1 ES FALTANTE EN BASE"
            )

        if estado_original == "sobra":
            return (
                f"{nombre}: ESTE PED TUVO R1, "
                "PERO A SU R1 LE SOBRA VALOR EN BASE"
            )

        if estado_original == "falta":
            return (
                f"{nombre}: ESTE PED TUVO R1, "
                "PERO A SU R1 LE FALTA VALOR EN BASE"
            )

        return (
            f"{nombre}: ESTE PED TUVO R1 "
            "Y SU R1 ESTÁ 100% CORRECTO"
        )

    # ======================================================
    # ES R1
    # ======================================================

    if es_r1:

        # ----------------------------------------------
        # NO CAPTURADO
        # ----------------------------------------------

        if not r1_capturado:

            if not original_existe:
                return (
                    f"{nombre}: PEDIMENTO R1 FALTANTE EN BASE. "
                    "Y TAMBIEN SU ORIGINAL, POR LO QUE NO PODEMOS "
                    "INTENTAR CREARLO A PARTIR DE ÉL. "
                    "ACCION REQUERIDA: PROPORCIONAR EL ARCHIVO "
                    "ELECTRÓNICO DE ESTE R1 O BIEN EL PDF "
                    "Y LAS FACTURAS DE ESTE PEDIMENTO PARA CAPTURA"
                )

            if estado_original != "correcto":
                return (
                    f"{nombre}: R1 FALTANTE Y SU ORIGINAL "
                    "TIENE ERROR EN VALOR USD POR LO QUE NO SE "
                    "PUEDE INTENTAR CREAR DESDE EL ORIGINAL. "
                    "ACCION REQUERIDA: PROPORCIONAR EL ARCHIVO "
                    "ELECTRÓNICO O BIEN EL PDF DEL PEDIMENTO "
                    "Y SUS FACTURAS PARA CAPTURA"
                )

            return (
                f"{nombre}: ES R1 100% CORRECTO EN VALOR"
            )

        # ----------------------------------------------
        # CAPTURADO
        # ----------------------------------------------

        if estado_r1_inclusivo == "correcto":
            return (
                f"{nombre}: ES R1 100% CORRECTO EN VALOR"
            )

        if estado_r1_inclusivo == "sobra":
            return (
                f"{nombre}: LE SOBRA VALOR EN BASE. "
                "ACCION REQUERIDA: PROPORCIONAR "
                "ARCHIVO ELECTRÓNICO O BIEN EL PDF "
                "DEL PEDIMENTO Y SUS FACTURAS "
                "PARA CORRECCIÓN"
            )

        return (
            f"{nombre}: LE FALTA VALOR EN BASE. "
            "ACCION REQUERIDA: PROPORCIONAR "
            "ARCHIVO ELECTRÓNICO O BIEN EL PDF "
            "DEL PEDIMENTO Y SUS FACTURAS "
            "PARA CORRECCIÓN"
        )

    # ======================================================
    # NO ES R1
    # ======================================================

    if not r1_capturado:
        return (
            f"{nombre}: FALTANTE EN BASE. "
            "ACCION REQUERIDA: PROPORCIONAR "
            "ARCHIVO ELECTRÓNICO O BIEN PDF "
            "DEL PEDIMENTO CON SUS FACTURAS "
            "PARA CAPTURAR EN ANEXO 24"
        )

    if estado_r1 == "correcto":
        return f"{nombre}: 100% CORRECTO EN USD"

    if estado_r1 == "sobra":
        return (
            f"{nombre}: LE SOBRA VALOR EN BASE. "
            "ACCION REQUERIDA: PROPORCIONAR "
            "ARCHIVO ELECTRÓNICO O BIEN EL PDF "
            "DEL PEDIMENTO Y SUS FACTURAS "
            "PARA CORRECCIÓN"
        )

    return (
        f"{nombre}: LE FALTA VALOR EN BASE. "
        "ACCION REQUERIDA: PROPORCIONAR "
        "ARCHIVO ELECTRÓNICO O BIEN EL PDF "
        "DEL PEDIMENTO Y SUS FACTURAS "
        "PARA CORRECCIÓN"
    )




def obc_accion_requerida(df_ds_group):

    df_ds_group=df_ds_group.copy()
    # ==========================================================
    # ÍNDICE DE BÚSQUEDA (reemplaza los BUSCARV)
    # ADU-PAT-PED es único
    # ==========================================================

    indice_originales = (
        df_ds_group.set_index("ADU-PAT-PED")[["VAL22", "VAL23"]]
        .to_dict("index")
    )


    # ==========================================================
    # RESULTADO
    # ==========================================================

    df_ds_group["VAL30"] = df_ds_group.apply(evaluar,indice_originales=indice_originales, axis=1)    
    
    return df_ds_group


def formatearColumnas(df_ds_group):
    
    df_ds_group=df_ds_group.copy()
        
    df_ds_group = (
        df_ds_group
        .rename(columns={
            "FECHA PAGO 551": "FECHA PAGO",
            "AF": "ID AF?",
            "CLAVE PED": "TIPO Y CLAVE",
            "VAL6": "SI EL PEDIMENTO DE LA COLUMNA 'T' ES R1, A QUIEN RECTIFICÓ?",
            "VAL7": "ESTATUS DEL PEDIMENTO A QUIEN RECTIFICO DE LA COLUMNA 'F'?",
            "VAL8": "SI EL PEDIMENTO DE LA COLUMNA 'T' TUVO R1, CUÁL FUE EL NÚMERO DE R1?",
            "VAL9": "ESTATUS DEL PEDIMENTO R1 DE LA COLUMNA H",
            "VAL10": "ESTIMACIÓN APROX DE IGI  6 FP 0",
            "VAL11": "ESTIMACIÓN APROX DE IGI 6 FP 5",
            "VAL12": "ESTIMACIÓN APROX DE IGI 6 FP 6",
            "VAL13": "SI EL PEDIMENTO DE LA COLUMNA 'T' ES DESCARGA ESPECIFICA, A QUIÉN DESCARGO?",
            "VAL14": "CLAVE  ORIGINAL",
            "VAL15": "FECHA DEL ORIGINAL DESCARGADO 512",
            "VAL16": "ESTATUS DEL ORIGINAL DESCARGADO",
            "VAL17": "SI EL PEDIMENTO DE LA COLUMNA 'Q' TUVO DESCARGAR ESPECIFICA, EN QUE PEDIMENTO SE DESCARGO?",
            "PEDIMENTO": "DS PEDIMENTO",
            "ADU-PAT-PED": "DS ADU-PAT-PED",
            "VAL USD": "DS VALOR DOLARES",
            "VAL22": "BASE VALOR DOLARES",
            "VAL23": "DIFERENCIA REAL",
            "VAL24": "DIFERENCIA ABSOLUTA",
            "VAL25": "REVISION DE DUPLICADOS",
            "VAL26": "USD ESTATUS A NIVEL GLOBAL",
            "VAL27": "OBSERVACIONES GLOBALES YA CON R1",
            "VAL28": "OBSERVACIONES GLOBALES YA CON R1 (ETIQUETA ANTERIOR)",
            "VAL29": "ACTIVIDAD PARA LA EMPRESA",
            "VAL30": "OBSERVACIONES CON ACCIÓN REQUERIDA O NO"
        })
        [
        [
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
            "CLAVE  ORIGINAL",
            "FECHA DEL ORIGINAL DESCARGADO 512",
            "ESTATUS DEL ORIGINAL DESCARGADO",
            "SI EL PEDIMENTO DE LA COLUMNA 'Q' TUVO DESCARGAR ESPECIFICA, EN QUE PEDIMENTO SE DESCARGO?",
            "DS PAT-PED",
            "DS PEDIMENTO",
            "DS ADU-PAT-PED",
            "DS VALOR DOLARES",
            "BASE VALOR DOLARES",
            "DIFERENCIA REAL",
            "DIFERENCIA ABSOLUTA",
            "REVISION DE DUPLICADOS",
            "USD ESTATUS A NIVEL GLOBAL",
            "OBSERVACIONES GLOBALES YA CON R1",
            "OBSERVACIONES GLOBALES YA CON R1 (ETIQUETA ANTERIOR)",
            "ACTIVIDAD PARA LA EMPRESA",
            "OBSERVACIONES CON ACCIÓN REQUERIDA O NO"

        ]
        ]
    )

    return df_ds_group

# def exportarArchivo(df_ds_group):
    
#     df_ds_group.to_excel("outputs/CROSS X PED.xlsx", index=False)
    
    

def ejecutar_proceso(dfs):
    
    """
    Ejecuta el proceso completo de transformación de datos.
    """

    df_ds = dfs["df_ds"]
    dataframe_DS_Virgen = dfs["df_virgen"]
    df_cli=dfs["df_cli"]  
        
    df_ds=crearDfDS(df_ds)
    df_cli_group=crearDfCliente(df_cli)
    df_ds_v2=creacionDatosBasicosCross(df_ds)
    df_ds_v3=creacionColumnasDsVigen(df_ds_v2,dataframe_DS_Virgen)
    df_ds_v4=mergeCliente_DS(df_ds_v3,df_cli_group)
    df_ds_v5=estatus_global_monto(df_ds_v4)
    df_ds_v6=obs_globales_r1(df_ds_v5)
    df_ds_v7=obs_globales_r1_etiqueta_anterior(df_ds_v6)
    df_ds_v8=actividad_empresa(df_ds_v7)
    df_ds_v9=obc_accion_requerida(df_ds_v8)
    df_ds_v10=formatearColumnas(df_ds_v9)
    # exportarArchivo(df_ds_v10)
    
    return df_ds_v10