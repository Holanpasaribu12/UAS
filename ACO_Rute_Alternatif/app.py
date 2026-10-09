
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from aco import (
    ALPHA,
    BETA,
    EVAPORASI,
    JUMLAH_ITERASI,
    JUMLAH_SEMUT,
    jalankan_aco,
)
from network import (
    SKENARIO,
    buat_graph,
)
from visualisasi import gambar_jaringan


# ==================================================
# 1. KONFIGURASI APLIKASI
# ==================================================

st.set_page_config(
    page_title="Simulasi ACO - Rute Alternatif",
    page_icon="🗺️",
    layout="wide"
)

st.title("Simulasi Ant Colony Optimization (ACO)")
st.write(
    "Analisis pengaruh penutupan jalur terhadap pencarian "
    "rute alternatif dari node A menuju node G."
)

# ==================================================
# 5. SIDEBAR DAN PARAMETER
# ==================================================

st.sidebar.header("Pengaturan Simulasi")

st.sidebar.write("Parameter ACO sesuai laporan:")

st.sidebar.metric("Jumlah semut", JUMLAH_SEMUT)
st.sidebar.metric("Jumlah iterasi", JUMLAH_ITERASI)
st.sidebar.metric("Alpha (α)", ALPHA)
st.sidebar.metric("Beta (β)", BETA)
st.sidebar.metric("Evaporasi (ρ)", EVAPORASI)

nama_skenario = st.sidebar.selectbox(
    "Pilih skenario penutupan jalur",
    list(SKENARIO.keys())
)

jalur_ditutup = SKENARIO[nama_skenario]

st.sidebar.write(
    f"Jumlah jalur ditutup: {len(jalur_ditutup)}"
)

st.sidebar.caption(
    "Titik awal: A | Titik tujuan: G"
)

# Tombol menjalankan satu skenario atau seluruh skenario.
kolom_tombol1, kolom_tombol2 = st.columns(2)

with kolom_tombol1:
    jalankan_satu = st.button(
        "Jalankan Skenario Terpilih",
        type="primary",
        use_container_width=True
    )

with kolom_tombol2:
    jalankan_semua = st.button(
        "Bandingkan Semua Skenario",
        use_container_width=True
    )


# ==================================================
# 6. MENJALANKAN SIMULASI
# ==================================================

if jalankan_satu:
    graph = buat_graph(jalur_ditutup)

    rute, jarak, waktu_ms = jalankan_aco(
        graph,
        seed=42
    )

    st.subheader(nama_skenario)

    if rute is None:
        st.error(
            "Rute dari A ke G tidak ditemukan pada jaringan ini."
        )
    else:
        kolom1, kolom2, kolom3 = st.columns(3)

        kolom1.metric("Panjang rute", f"{jarak:g} satuan")
        kolom2.metric("Waktu pencarian", f"{waktu_ms:.3f} ms")
        kolom3.metric("Jalur ditutup", len(jalur_ditutup))

        st.success("Rute terbaik ditemukan!")

        st.write("**Rute:**", " → ".join(rute))

        fig = gambar_jaringan(
            graph,
            jalur_ditutup,
            rute
        )
        st.pyplot(fig)
        plt.close(fig)

        st.write("**Jalur yang ditutup:**")
        if jalur_ditutup:
            st.write(
                ", ".join(f"{u}-{v}" for u, v in jalur_ditutup)
            )
        else:
            st.write("Tidak ada jalur yang ditutup.")


# ==================================================
# 7. PERBANDINGAN EMPAT SKENARIO
# ==================================================

if jalankan_semua:
    hasil = []

    with st.spinner("Menjalankan ACO pada empat skenario..."):
        for index, (nama, daftar_tutup) in enumerate(SKENARIO.items()):
            graph = buat_graph(daftar_tutup)

            rute, jarak, waktu_ms = jalankan_aco(
                graph,
                seed=42 + index
            )

            hasil.append({
                "Skenario": nama,
                "Jalur Ditutup": len(daftar_tutup),
                "Rute Terbaik": (
                    " → ".join(rute) if rute else "Tidak ditemukan"
                ),
                "Panjang Rute": (
                    jarak if jarak is not None else None
                ),
                "Waktu Pencarian (ms)": round(waktu_ms, 3),
                "Status": (
                    "Berhasil" if rute else "Tidak ditemukan"
                ),
            })

    df = pd.DataFrame(hasil)

    st.subheader("Hasil Perbandingan Skenario")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Grafik panjang rute.
    df_jarak = df.dropna(subset=["Panjang Rute"])

    if not df_jarak.empty:
        st.subheader("Perbandingan Panjang Rute")

        fig1, ax1 = plt.subplots(figsize=(9, 4))

        ax1.bar(
            df_jarak["Skenario"],
            df_jarak["Panjang Rute"]
        )

        ax1.set_ylabel("Panjang rute (satuan jarak)")
        ax1.set_xlabel("Skenario")
        ax1.tick_params(axis="x", rotation=15)
        fig1.tight_layout()

        st.pyplot(fig1)
        plt.close(fig1)

        st.subheader("Perbandingan Waktu Pencarian")

        fig2, ax2 = plt.subplots(figsize=(9, 4))

        ax2.bar(
            df_jarak["Skenario"],
            df_jarak["Waktu Pencarian (ms)"]
        )

        ax2.set_ylabel("Waktu pencarian (ms)")
        ax2.set_xlabel("Skenario")
        ax2.tick_params(axis="x", rotation=15)
        fig2.tight_layout()

        st.pyplot(fig2)
        plt.close(fig2)

    # Unduh hasil untuk bahan laporan.
    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Unduh Hasil Pengujian (CSV)",
        data=csv,
        file_name="hasil_pengujian_aco.csv",
        mime="text/csv"
    )


# ==================================================
# 8. INFORMASI PENELITIAN
# ==================================================

with st.expander("Tentang simulasi ini"):
    st.write(
        """
        **Judul:** Analisis Pengaruh Penutupan Jalur terhadap
        Kinerja Algoritma Ant Colony Optimization dalam
        Menentukan Rute Alternatif.

        **Peneliti:** Asiholan Pandapotan Pasaribu

        **NIM:** 20235520005

        Simulasi menggunakan graph berbobot. Node mewakili titik
        lokasi, sedangkan edge mewakili jalur dengan bobot jarak.

        Semut memilih jalur berdasarkan pheromone dan informasi
        heuristik berupa kebalikan jarak. Pheromone mengalami
        evaporasi dan penambahan berdasarkan rute yang ditemukan.

        Nilai jarak adalah bobot simulasi, bukan jarak jalan nyata.
        Waktu pencarian diukur saat algoritma ACO berjalan dan dapat
        berubah antar-eksekusi maupun perangkat.
        """
    )