import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import FuncFormatter

# ── Conexión ──────────────────────────────────────────────────────────────────
conexion = pymysql.connect(
    host="nas.latorreg.es",
    user="root",
    passwd="7365",
    database="futuretech_db"
)

df_centros     = pd.read_sql("SELECT * FROM Centro_Datos", conexion)
df_sectores    = pd.read_sql("SELECT * FROM Sector", conexion)
df_consumo     = pd.read_sql("SELECT * FROM Consumo_Energetico", conexion)
df_costes      = pd.read_sql("SELECT * FROM Costes_Operativos", conexion)
df_indicadores = pd.read_sql("SELECT * FROM Indicadores_Sostenibilidad", conexion)

conexion.close()

# ── Estilo dark mode ──────────────────────────────────────────────────────────
plt.style.use("dark_background")
mpl.rcParams.update({
    "figure.facecolor": "#0e1117",
    "axes.facecolor":   "#1a1d27",
    "axes.edgecolor":   "#3a3d4d",
    "axes.labelcolor":  "#c8ccd8",
    "axes.titlesize":   11,
    "axes.titlecolor":  "#e8eaf0",
    "axes.titlepad":    12,
    "xtick.color":      "#8a8fa8",
    "ytick.color":      "#8a8fa8",
    "xtick.labelsize":  8,
    "ytick.labelsize":  8,
    "grid.color":       "#2a2d3a",
    "grid.linewidth":   0.6,
    "legend.facecolor": "#1a1d27",
    "legend.edgecolor": "#3a3d4d",
    "legend.labelcolor":"#c8ccd8",
    "font.family":      "DejaVu Sans",
    "text.color":       "#c8ccd8",
})

PALETA_AZUL  = ["#4fc3f7", "#0288d1", "#01579b", "#b3e5fc", "#e1f5fe"]
PALETA_CORAL = ["#ef9a9a", "#e53935", "#b71c1c", "#ffcdd2", "#ffebee"]
PALETA_VERDE = ["#a5d6a7", "#388e3c", "#1b5e20", "#c8e6c9", "#e8f5e9"]

# ── Números sin notación científica ───────────────────────────────────────────
def fmt_numero(x, _):
    return f"{x:,.0f}".replace(",", ".")

formatter = FuncFormatter(fmt_numero)
pd.options.display.float_format = lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# ── Guardar figura ────────────────────────────────────────────────────────────
def guardar(nombre):
    plt.savefig(f"{nombre}.png", dpi=300, bbox_inches="tight",
                facecolor=mpl.rcParams["figure.facecolor"])

# ── Preparación ───────────────────────────────────────────────────────────────
df_consumo["fecha"] = pd.to_datetime(df_consumo["fecha"], errors="coerce")
df_costes["fecha"]  = pd.to_datetime(df_costes["fecha"],  errors="coerce")
df_consumo = df_consumo.dropna(subset=["fecha"])
df_costes  = df_costes.dropna(subset=["fecha"])
df_consumo["anio"] = df_consumo["fecha"].dt.year
df_costes["anio"]  = df_costes["fecha"].dt.year

sect_cent  = df_sectores[["id_sector", "id_centro", "nombre"]].rename(columns={"nombre": "sector"})
centros_nm = df_centros[["id_centro", "nombre"]].rename(columns={"nombre": "centro"})

df_consumo     = df_consumo.merge(sect_cent, on="id_sector", how="left").merge(centros_nm, on="id_centro", how="left")
df_costes      = df_costes.merge(sect_cent,  on="id_sector", how="left").merge(centros_nm, on="id_centro", how="left")
df_indicadores = df_indicadores.merge(centros_nm, on="id_centro", how="left")


# ══════════════════════════════════════════════════════════════════════════════
# 1. CONSUMO ENERGÉTICO
# ══════════════════════════════════════════════════════════════════════════════

consumo_anual      = df_consumo.groupby("anio")["kwh_consumidos"].sum()
consumo_por_centro = df_consumo.groupby("centro")["kwh_consumidos"].sum().sort_values(ascending=False)
consumo_por_fuente = df_consumo.groupby("fuente_energia")["kwh_consumidos"].sum()

print("=== Consumo Energético ===")
print(df_consumo["kwh_consumidos"].describe())
print("\nkWh por año:\n",    consumo_anual)
print("\nkWh por centro:\n", consumo_por_centro)
print("\nkWh por fuente:\n", consumo_por_fuente)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Consumo Energético", fontsize=15, fontweight="bold", y=1.02)
fig.patch.set_facecolor(mpl.rcParams["figure.facecolor"])

consumo_anual.plot(kind="bar", ax=axes[0], color=PALETA_AZUL[0], edgecolor="#0e1117", linewidth=0.5)
axes[0].set_title("kWh totales por año")
axes[0].set_xlabel("Año")
axes[0].set_ylabel("kWh")
axes[0].tick_params(axis="x", rotation=45)
axes[0].yaxis.set_major_formatter(formatter)
axes[0].yaxis.grid(True)
axes[0].set_axisbelow(True)

consumo_por_centro.plot(kind="barh", ax=axes[1], color=PALETA_AZUL[1], edgecolor="#0e1117", linewidth=0.5)
axes[1].set_title("kWh por centro")
axes[1].set_xlabel("kWh")
axes[1].xaxis.set_major_formatter(formatter)
axes[1].xaxis.grid(True)
axes[1].set_axisbelow(True)

wedges, texts, autotexts = axes[2].pie(
    consumo_por_fuente,
    labels=consumo_por_fuente.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=PALETA_AZUL[:len(consumo_por_fuente)],
    wedgeprops={"edgecolor": "#0e1117", "linewidth": 1.2}
)
for at in autotexts:
    at.set_fontsize(8)
    at.set_color("#0e1117")
axes[2].set_title("Distribución por fuente")

plt.tight_layout()
guardar("consumo_energetico")
plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# 2. COSTES OPERATIVOS
# ══════════════════════════════════════════════════════════════════════════════

coste_anual      = df_costes.groupby("anio")["coste_total"].sum()
coste_por_centro = df_costes.groupby("centro")["coste_total"].sum().sort_values(ascending=False)
desglose         = df_costes[["coste_energia", "coste_mantenimiento", "coste_personal"]].mean()

print("\n=== Costes Operativos ===")
print(df_costes[["coste_energia", "coste_mantenimiento", "coste_personal", "coste_total"]].describe())
print("\nCoste total por año:\n",  coste_anual)
print("\nMedia por categoría:\n",  desglose)
print("\nCoste total por centro:\n", coste_por_centro)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Costes Operativos", fontsize=15, fontweight="bold", y=1.02)
fig.patch.set_facecolor(mpl.rcParams["figure.facecolor"])

coste_anual.plot(kind="bar", ax=axes[0], color=PALETA_CORAL[0], edgecolor="#0e1117", linewidth=0.5)
axes[0].set_title("Coste total por año")
axes[0].set_xlabel("Año")
axes[0].set_ylabel("EUR")
axes[0].tick_params(axis="x", rotation=45)
axes[0].yaxis.set_major_formatter(formatter)
axes[0].yaxis.grid(True)
axes[0].set_axisbelow(True)

wedges, texts, autotexts = axes[1].pie(
    desglose,
    labels=["Energía", "Mantenimiento", "Personal"],
    autopct="%1.1f%%",
    startangle=90,
    colors=[PALETA_CORAL[0], "#ffd54f", PALETA_VERDE[0]],
    wedgeprops={"edgecolor": "#0e1117", "linewidth": 1.2}
)
for at in autotexts:
    at.set_fontsize(8)
    at.set_color("#0e1117")
axes[1].set_title("Desglose medio de costes")

coste_por_centro.plot(kind="barh", ax=axes[2], color=PALETA_CORAL[1], edgecolor="#0e1117", linewidth=0.5)
axes[2].set_title("Coste total por centro")
axes[2].set_xlabel("EUR")
axes[2].xaxis.set_major_formatter(formatter)
axes[2].xaxis.grid(True)
axes[2].set_axisbelow(True)

plt.tight_layout()
guardar("costes_operativos")
plt.show()


# ══════════════════════════════════════════════════════════════════════════════
# 3. SOSTENIBILIDAD
# ══════════════════════════════════════════════════════════════════════════════

huella_anual     = df_indicadores.groupby("anio")["huella_carbono"].mean()
ultimo_anio      = df_indicadores["anio"].max()
renovable_ultimo = df_indicadores[df_indicadores["anio"] == ultimo_anio].set_index("centro")["porcentaje_renovable"]
pivot_puntuacion = df_indicadores.pivot_table(index="anio", columns="centro", values="puntuacion_global", aggfunc="mean")

print("\n=== Indicadores de Sostenibilidad ===")
print(df_indicadores[["huella_carbono", "porcentaje_renovable", "indice_social", "puntuacion_global"]].describe())
print("\nHuella de carbono media por año:\n", huella_anual)
print(f"\n% Renovable por centro ({ultimo_anio}):\n", renovable_ultimo)
print("\nPuntuación global (pivot):\n", pivot_puntuacion)

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Sostenibilidad", fontsize=15, fontweight="bold", y=1.02)
fig.patch.set_facecolor(mpl.rcParams["figure.facecolor"])

axes[0].plot(huella_anual.index, huella_anual.values, marker="o",
             color=PALETA_VERDE[0], linewidth=2, markersize=6,
             markerfacecolor=PALETA_VERDE[1], markeredgecolor="#0e1117")
axes[0].fill_between(huella_anual.index, huella_anual.values, alpha=0.15, color=PALETA_VERDE[0])
axes[0].set_title("Huella de carbono media (kg CO2)")
axes[0].set_xlabel("Año")
axes[0].set_ylabel("kg CO2")
axes[0].yaxis.set_major_formatter(formatter)
axes[0].yaxis.grid(True)
axes[0].set_axisbelow(True)

renovable_ultimo.plot(kind="bar", ax=axes[1], color=PALETA_VERDE[1], edgecolor="#0e1117", linewidth=0.5)
axes[1].set_title(f"% Energía renovable ({ultimo_anio})")
axes[1].set_ylabel("%")
axes[1].tick_params(axis="x", rotation=45)
axes[1].yaxis.grid(True)
axes[1].set_axisbelow(True)

colores_linea = ["#4fc3f7", "#a5d6a7", "#ef9a9a", "#ffd54f", "#ce93d8"]
for i, centro in enumerate(pivot_puntuacion.columns):
    axes[2].plot(pivot_puntuacion.index, pivot_puntuacion[centro],
                 marker="o", label=centro,
                 color=colores_linea[i % len(colores_linea)],
                 linewidth=2, markersize=5)
axes[2].set_title("Puntuación global por centro")
axes[2].set_xlabel("Año")
axes[2].set_ylabel("Puntuación")
axes[2].legend(fontsize=7)
axes[2].yaxis.grid(True)
axes[2].set_axisbelow(True)

plt.tight_layout()
guardar("sostenibilidad")
plt.show()