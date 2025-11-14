import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Configurazione pagina
# ----------------------------
PAGE_TITLE = "Dashboard personale - Partecipanti alla mia sessione del Festival dell'Innovazione Agroalimentare"

st.set_page_config(
    page_title=PAGE_TITLE,
    layout="wide"
)

st.title(PAGE_TITLE)
st.write(
    "Carica un file Excel con i dati dei partecipanti per visualizzare grafici e una tabella filtrabile."
)

# ----------------------------
# Impostazioni analisi
# ----------------------------

# Tutte le categorie di profiling presenti nel questionario
ALL_PROFILING_CATEGORIES = [
    "Occupazione",
    "Tipologia di organizzazione presso cui lavori",
    "Organizzazione presso cui lavori o studi",
    "Seniority",
    "Area aziendale",
    "Settore produttivo",
]

# Categorie per cui vogliamo disegnare un grafico
CATEGORIES_WITH_CHARTS = [
    c
    for c in ALL_PROFILING_CATEGORIES
    if c != "Organizzazione presso cui lavori o studi"
]

# Colonna che non vogliamo mostrare come grafico
ORGANIZATION_COLUMN = "Organizzazione presso cui lavori o studi"

# Palette colori del brand
BRAND_COLORS = ["#73b27d", "#f1ad72", "#d31048"]

# ----------------------------
# Upload file
# ----------------------------
uploaded_file = st.file_uploader(
    "Scegli un file Excel (.xlsx o .xls)",
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        df_uploaded = pd.read_excel(uploaded_file)

        st.success("File caricato correttamente!")

        # ----------------------------
        # Grafici per le categorie di profiling
        # ----------------------------
        st.subheader("Analisi grafica dei partecipanti")

        for category in CATEGORIES_WITH_CHARTS:
            if category not in df_uploaded.columns:
                st.warning(
                    f"La colonna '{category}' non è presente nel file caricato."
                )
                continue

            st.markdown(f"### {category}")

            # Conteggi e percentuali (ignoriamo i NaN)
            value_counts = df_uploaded[category].value_counts(dropna=True)
            if value_counts.empty:
                st.info(
                    f"Nessun dato disponibile per '{category}' dopo aver rimosso i valori mancanti."
                )
                continue

            total = value_counts.sum()
            percentages = (value_counts / total * 100).round(1)

            # DataFrame per facilitare la gestione
            dist_df = pd.DataFrame({
                category: value_counts.index.astype(str),
                "Numero": value_counts.values,
                "Percentuale": percentages.values,
            })

            # Grafico a barre con brand colors e percentuali in etichetta
            fig, ax = plt.subplots(figsize=(10, 6))

            colors = [
                BRAND_COLORS[i % len(BRAND_COLORS)]
                for i in range(len(dist_df))
            ]

            bars = ax.bar(dist_df[category], dist_df["Numero"], color=colors)

            ax.set_title(f"Distribuzione di {category}")
            ax.set_xlabel(category)
            ax.set_ylabel("Numero di partecipanti")
            plt.xticks(rotation=45, ha="right")

            # Etichette con la % sopra ogni barra
            for bar, pct in zip(bars, dist_df["Percentuale"]):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height,
                    f"{pct:.1f}%",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Tabellina riassuntiva per la singola categoria
            with st.expander(f"Dettaglio valori per '{category}'"):
                st.dataframe(
                    dist_df.set_index(category),
                    use_container_width=True,
                )

        # Nota sulla colonna Organizzazione
        if ORGANIZATION_COLUMN in df_uploaded.columns:
            st.info(
                "La colonna "
                f"'{ORGANIZATION_COLUMN}' "
                "non viene visualizzata come grafico perché contiene troppi valori diversi. "
                "Puoi comunque analizzarla nella tabella completa qui sotto."
            )

        # ----------------------------
        # Tabella completa con filtri
        # ----------------------------
        st.subheader("Tabella completa con filtri")

        df_filtered = df_uploaded.copy()

        with st.expander("Imposta filtri per le colonne"):
            for col in df_uploaded.columns:
                col_data = df_uploaded[col]

                # Colonne numeriche: filtro per intervallo
                if pd.api.types.is_numeric_dtype(col_data):
                    min_val = col_data.min()
                    max_val = col_data.max()
                    if pd.isna(min_val) or pd.isna(max_val):
                        continue

                    range_values = st.slider(
                        f"Intervallo per '{col}'",
                        float(min_val),
                        float(max_val),
                        (float(min_val), float(max_val)),
                    )
                    df_filtered = df_filtered[
                        df_filtered[col].between(range_values[0], range_values[1])
                    ]

                # Colonne testuali/categoriche: multiselect
                else:
                    unique_vals = sorted(
                        col_data.dropna().astype(str).unique().tolist()
                    )
                    if not unique_vals:
                        continue

                    selected_vals = st.multiselect(
                        f"Valori per '{col}'",
                        options=unique_vals,
                        default=unique_vals,
                    )
                    if selected_vals:
                        df_filtered = df_filtered[
                            df_filtered[col].astype(str).isin(selected_vals)
                        ]

        # Tabella completa (tutte le righe dopo i filtri)
        st.dataframe(
            df_filtered,
            use_container_width=True,
        )

    except Exception as e:
        st.error(
            f"Errore nella lettura del file: {e}. Assicurati che sia un file Excel valido."
        )
else:
    st.info("Carica un file Excel per procedere con l'analisi.")
