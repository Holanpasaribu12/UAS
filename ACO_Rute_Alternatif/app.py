"""A simple interactive ACO experiment using real Bandung tourist locations."""

import statistics

import pandas as pd
import streamlit as st

from aco import (
    ALPHA,
    BETA,
    EVAPORASI,
    JUMLAH_ITERASI,
    cari_rute_optimal,
    jalankan_aco_tsp,
)
from network import (
    TEMPAT_WISATA,
    TITIK_AWAL,
    buat_matriks_jarak,
    url_openstreetmap,
)


st.set_page_config(
    page_title="Rute Wisata Bandung dengan ACO",
    page_icon="🗺️",
    layout="centered",
)

TEMPAT = list(TEMPAT_WISATA)
JUMLAH_SEMUT_DIUJI = (5, 15, 30)
ULANGAN = 10
SEED_AWAL = 42
JARAK = buat_matriks_jarak(TEMPAT)


st.title("Rute Wisata Bandung dengan ACO")
st.write(
    "Temukan urutan kunjungan wisata yang pendek, mulai dan berakhir "
    "di Gedung Sate. ACO dibandingkan dengan semua kemungkinan urutan "
    "kunjungan sebagai jawaban optimal."
)

with st.expander("Cara kerja dan rancangan eksperimen", expanded=True):
    st.markdown(
        f"""
        - **Kasus:** kunjungi semua {len(TEMPAT) - 1} tempat wisata lalu kembali
          ke {TITIK_AWAL}.
        - **Data:** koordinat perkiraan lokasi wisata nyata; jarak dihitung dengan
          rumus Haversine (garis lurus), dalam kilometer.
        - **Percobaan:** ACO dijalankan 10 kali untuk setiap jumlah semut
          **5, 15, dan 30**.
        - **Parameter tetap:** {JUMLAH_ITERASI} iterasi, α={ALPHA:g},
          β={BETA:g}, evaporasi={EVAPORASI:g}; seed dicatat agar percobaan
          dapat diulang.
        - **Evaluasi:** jarak rata-rata dan waktu ACO dibandingkan dengan
          rute optimal yang ditemukan dengan memeriksa semua
          **{(len(TEMPAT) - 1)}! = 120 urutan**.
        """
    )
    st.caption(
        "Catatan: jarak garis lurus bukan jarak jalan atau rekomendasi navigasi."
    )

st.subheader("Data lokasi nyata")
baris_lokasi = [
    {
        "Tempat": nama,
        "Lintang": koordinat[0],
        "Bujur": koordinat[1],
        "Peta": url_openstreetmap(nama),
    }
    for nama, koordinat in TEMPAT_WISATA.items()
]
st.dataframe(
    pd.DataFrame(baris_lokasi),
    width="stretch",
    hide_index=True,
    column_config={
        "Lintang": st.column_config.NumberColumn(format="%.5f"),
        "Bujur": st.column_config.NumberColumn(format="%.5f"),
        "Peta": st.column_config.LinkColumn("OpenStreetMap"),
    },
)

st.info(
    "**Titik awal dan akhir:** Gedung Sate. "
    "**Tempat yang dikunjungi:** lima lokasi lainnya, masing-masing satu kali."
)

hasil_eksperimen = st.session_state.get("hasil_eksperimen")
if st.button(
    "▶ Jalankan dan evaluasi ACO",
    type="primary",
    width="stretch",
):
    rute_optimal, jarak_optimal = cari_rute_optimal(TEMPAT, JARAK, TITIK_AWAL)
    catatan = []
    rute_terbaik = None
    jarak_terbaik = float("inf")

    progress = st.progress(0, text="Menjalankan 30 percobaan ACO...")
    selesai = 0
    for jumlah_semut in JUMLAH_SEMUT_DIUJI:
        for ulangan in range(ULANGAN):
            seed = SEED_AWAL + ulangan
            rute, jarak_aco, waktu_ms = jalankan_aco_tsp(
                TEMPAT,
                JARAK,
                TITIK_AWAL,
                jumlah_semut=jumlah_semut,
                jumlah_iterasi=JUMLAH_ITERASI,
                alpha=ALPHA,
                beta=BETA,
                evaporasi=EVAPORASI,
                seed=seed,
            )
            catatan.append({
                "Jumlah semut": jumlah_semut,
                "Ulangan": ulangan + 1,
                "Seed": seed,
                "Jarak ACO (km)": jarak_aco,
                "Selisih dari optimum (%)": (
                    (jarak_aco - jarak_optimal) / jarak_optimal * 100
                ),
                "Waktu ACO (ms)": waktu_ms,
                "Urutan kunjungan": " → ".join(rute),
            })
            if jarak_aco < jarak_terbaik:
                rute_terbaik = rute
                jarak_terbaik = jarak_aco
            selesai += 1
            progress.progress(selesai / (len(JUMLAH_SEMUT_DIUJI) * ULANGAN))
    progress.empty()

    detail = pd.DataFrame(catatan)
    ringkasan = []
    for jumlah_semut in JUMLAH_SEMUT_DIUJI:
        kelompok = detail[detail["Jumlah semut"] == jumlah_semut]
        jarak_rata_rata = kelompok["Jarak ACO (km)"].mean()
        selisih_rata_rata = kelompok["Selisih dari optimum (%)"].mean()
        ringkasan.append({
            "Jumlah semut": jumlah_semut,
            "Rata-rata jarak (km)": jarak_rata_rata,
            "Simpangan baku (km)": statistics.stdev(
                kelompok["Jarak ACO (km)"]
            ),
            "Rata-rata waktu (ms)": kelompok["Waktu ACO (ms)"].mean(),
            "Selisih dari optimum (%)": selisih_rata_rata,
            "Rute optimal ditemukan": (
                f"{(kelompok['Selisih dari optimum (%)'] < 0.000001).sum()}/{ULANGAN}"
            ),
        })

    st.session_state["hasil_eksperimen"] = {
        "ringkasan": pd.DataFrame(ringkasan),
        "detail": detail,
        "rute_optimal": rute_optimal,
        "jarak_optimal": jarak_optimal,
        "rute_aco": rute_terbaik,
        "jarak_aco": jarak_terbaik,
    }
    hasil_eksperimen = st.session_state["hasil_eksperimen"]

if hasil_eksperimen:
    st.subheader("Hasil eksperimen")
    st.metric(
        "Jarak rute optimal (semua 120 urutan diperiksa)",
        f"{hasil_eksperimen['jarak_optimal']:.2f} km",
    )

    ringkasan = hasil_eksperimen["ringkasan"]
    st.dataframe(
        ringkasan,
        width="stretch",
        hide_index=True,
        column_config={
            "Rata-rata jarak (km)": st.column_config.NumberColumn(format="%.3f"),
            "Simpangan baku (km)": st.column_config.NumberColumn(format="%.3f"),
            "Rata-rata waktu (ms)": st.column_config.NumberColumn(format="%.3f"),
            "Selisih dari optimum (%)": st.column_config.NumberColumn(format="%.3f%%"),
        },
    )

    grafik = ringkasan.set_index("Jumlah semut")[
        ["Rata-rata jarak (km)"]
    ].copy()
    grafik["Optimum (km)"] = hasil_eksperimen["jarak_optimal"]
    st.caption("Jarak rata-rata ACO dan jarak optimal untuk jumlah semut yang diuji.")
    st.line_chart(
        grafik,
        x_label="Jumlah semut",
        y_label="Jarak (km)",
    )

    terbaik = ringkasan.loc[ringkasan["Rata-rata jarak (km)"].idxmin()]
    selisih_terbaik = terbaik["Selisih dari optimum (%)"]
    st.success(
        f"**Kesimpulan otomatis:** jumlah semut {int(terbaik['Jumlah semut'])} "
        f"memberikan rata-rata jarak terendah, "
        f"{terbaik['Rata-rata jarak (km)']:.3f} km. "
        f"Rata-rata selisih dari jawaban optimal adalah "
        f"{selisih_terbaik:.3f}%. "
        f"ACO menemukan rute optimal dalam "
        f"{terbaik['Rute optimal ditemukan']} percobaan."
    )
    st.markdown(
        "**Rute optimal:** " + " → ".join(hasil_eksperimen["rute_optimal"])
    )
    st.markdown(
        "**Rute terbaik yang ditemukan ACO:** "
        + " → ".join(hasil_eksperimen["rute_aco"])
    )
    st.caption(
        "Kesimpulan hanya berlaku untuk enam tempat dan konfigurasi yang diuji. "
        "Peningkatan jumlah semut dapat memengaruhi hasil maupun waktu."
    )
    st.download_button(
        "⬇️ Unduh data semua percobaan (CSV)",
        hasil_eksperimen["detail"].to_csv(index=False).encode("utf-8-sig"),
        file_name="eksperimen_aco_rute_wisata_bandung.csv",
        mime="text/csv",
    )

with st.expander("Referensi data dan algoritma"):
    st.markdown(
        """
        - OpenStreetMap contributors — koordinat perkiraan tiap lokasi dapat
          diperiksa melalui tautan pada tabel. Peta © OpenStreetMap contributors.
        - Dorigo, M., Birattari, M., & Stützle, T. (2006).
          *Ant Colony Optimization*. IEEE Computational Intelligence Magazine,
          1(4), 28–39. [DOI](https://doi.org/10.1109/MCI.2006.329691)
        - Haversine digunakan untuk menghitung jarak permukaan bumi dari
          pasangan koordinat lintang-bujur.
        """
    )
