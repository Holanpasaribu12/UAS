"""A simple interactive ACO experiment using real Bandung tourist locations."""

import statistics

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

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

st.subheader("Peta rute dan pilihan tujuan pertama")
hasil_eksperimen = st.session_state.get("hasil_eksperimen")
tujuan_pertama = st.selectbox(
    "Pilih tempat yang ingin dikunjungi pertama setelah Gedung Sate",
    [nama for nama in TEMPAT if nama != TITIK_AWAL],
)
rute_pilihan, jarak_pilihan, _ = jalankan_aco_tsp(
    TEMPAT,
    JARAK,
    TITIK_AWAL,
    tujuan_pertama=tujuan_pertama,
    jumlah_semut=30,
    jumlah_iterasi=JUMLAH_ITERASI,
    alpha=ALPHA,
    beta=BETA,
    evaporasi=EVAPORASI,
    seed=SEED_AWAL,
)
rute_optimal_pilihan, jarak_optimal_pilihan = cari_rute_optimal(
    TEMPAT,
    JARAK,
    TITIK_AWAL,
    tujuan_pertama=tujuan_pertama,
)

mode_peta = st.radio(
    "Pilih rute yang ingin dibandingkan",
    [
        "Tujuan pertama pilihan",
        "Hasil eksperimen ACO",
    ] if hasil_eksperimen else ["Tujuan pertama pilihan"],
    index=1 if hasil_eksperimen else 0,
    horizontal=True,
)
if mode_peta == "Hasil eksperimen ACO":
    rute_aco_peta = hasil_eksperimen["rute_aco"]
    jarak_aco_peta = hasil_eksperimen["jarak_aco"]
    rute_optimal_peta = hasil_eksperimen["rute_optimal"]
    jarak_optimal_peta = hasil_eksperimen["jarak_optimal"]
    st.caption(
        "Peta menampilkan rute terbaik dari seluruh 30 percobaan dan "
        "rute optimal pembanding. Pilihan tujuan pertama tidak membatasi "
        "hasil eksperimen ini."
    )
else:
    rute_aco_peta = rute_pilihan
    jarak_aco_peta = jarak_pilihan
    rute_optimal_peta = rute_optimal_pilihan
    jarak_optimal_peta = jarak_optimal_pilihan
    st.caption(
        f"Peta memakai 30 semut dan {JUMLAH_ITERASI} iterasi; "
        "tujuan pertama yang dipilih tetap dipertahankan oleh ACO."
    )

kolom_aco, kolom_optimal = st.columns(2)
kolom_aco.metric("Rute terbaik ACO", f"{jarak_aco_peta:.2f} km")
kolom_optimal.metric(
    "Rute optimal pembanding",
    f"{jarak_optimal_peta:.2f} km",
)

pusat_peta = (
    sum(koordinat[0] for koordinat in TEMPAT_WISATA.values()) / len(TEMPAT_WISATA),
    sum(koordinat[1] for koordinat in TEMPAT_WISATA.values()) / len(TEMPAT_WISATA),
)
peta = folium.Map(
    location=pusat_peta,
    zoom_start=12,
    control_scale=True,
    height=480,
)
layer_optimal = folium.FeatureGroup(name="Rute optimal (biru)")
folium.PolyLine(
    [TEMPAT_WISATA[nama] for nama in rute_optimal_peta],
    color="#2563eb",
    weight=6,
    opacity=0.85,
    tooltip="Rute optimal",
).add_to(layer_optimal)
layer_optimal.add_to(peta)
layer_aco = folium.FeatureGroup(name="Rute terbaik ACO (jingga)")
folium.PolyLine(
    [TEMPAT_WISATA[nama] for nama in rute_aco_peta],
    color="#ea580c",
    weight=4,
    opacity=1,
    dash_array="10, 8",
    tooltip="Rute terbaik ACO",
).add_to(layer_aco)
layer_aco.add_to(peta)
for nama, koordinat in TEMPAT_WISATA.items():
    folium.CircleMarker(
        location=koordinat,
        radius=7,
        color="#1f2937",
        weight=2,
        fill=True,
        fill_color="#ffffff",
        fill_opacity=1,
        tooltip=nama,
        popup=nama,
    ).add_to(peta)
folium.LayerControl(collapsed=False).add_to(peta)
st_folium(peta, height=500, use_container_width=True, returned_objects=[])
st.markdown("**🔵 Rute optimal:** " + " → ".join(rute_optimal_peta))
st.markdown("**🟠 Rute terbaik ACO:** " + " → ".join(rute_aco_peta))
if rute_aco_peta == rute_optimal_peta:
    st.info(
        "Pada hasil ini, ACO menemukan urutan yang sama dengan rute optimal. "
        "Garis biru dan jingga bertumpuk; garis ACO dibuat putus-putus agar "
        "keduanya tetap dapat dibedakan."
    )
st.caption(
    "Garis pada peta menghubungkan koordinat secara lurus sesuai perhitungan "
    "Haversine; ini bukan rute jalan. Peta dasar memerlukan koneksi internet."
)
with st.expander("Jarak rute optimal untuk tujuan pertama yang dipilih"):
    st.markdown("**Rute optimal:** " + " → ".join(rute_optimal_pilihan))
    st.write(f"Total jarak optimal: {jarak_optimal_pilihan:.3f} km.")

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
                rute_terbaik = rute.copy()
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
    st.rerun()

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
