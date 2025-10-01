import streamlit as st
import pandas as pd

# Mengatur layout halaman menjadi lebar dan memberikan judul pada tab browser
st.set_page_config(layout="wide", page_title="Dashboard ")

# Judul utama dashboard
st.title('📊 Dashboard Analisis Data ')
st.write('Aplikasi ini memungkinkan Anda untuk memfilter dan memvisualisasikan data  berdasarkan kecamatan, desa, dan variabel yang dipilih.')

# --- Langkah 1: Upload File ---
st.header('Langkah 1: Upload Dataset  Anda')
uploaded_file = st.file_uploader("Pilih file Excel atau CSV", type=['xlsx', 'csv'])

st.write("---") # Garis pemisah

# Proses hanya berjalan jika file sudah diupload
if uploaded_file is not None:
    try:
        # Baca file sesuai formatnya, 'low_memory=False' untuk mencegah error pada file CSV besar
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, low_memory=False)
        else:
            df = pd.read_excel(uploaded_file)

        st.success('✅ File berhasil diupload dan dibaca!')

        # --- VALIDASI & PEMBERSIHAN DATA ---

        # Periksa apakah kolom wajib ('nama_kec' dan 'nama_desa') ada
        if 'nama_kec' not in df.columns or 'nama_desa' not in df.columns:
            st.error("⚠️ **Error:** Pastikan dataset Anda memiliki kolom dengan nama persis 'nama_kec' dan 'nama_desa'.")
        else:
            # Simpan jumlah baris awal untuk laporan
            original_row_count = len(df)
            
            # Hapus baris di mana 'nama_kec' atau 'nama_desa' kosong
            df.dropna(subset=['nama_kec', 'nama_desa'], inplace=True)
            
            rows_dropped = original_row_count - len(df)
            if rows_dropped > 0:
                st.warning(f"⚠️ **Notifikasi:** {rows_dropped} baris telah dihapus karena tidak memiliki data di kolom 'nama_kec' atau 'nama_desa'.")

            # Konversi semua kolom (selain kolom inti) ke tipe numerik
            # Nilai yang tidak bisa dikonversi (teks) akan diubah menjadi kosong (NaN)
            for col in df.columns:
                if col not in ['nama_kec', 'nama_desa']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # --- Langkah 2: Opsi Filter ---
            st.header('Langkah 2: Filter Data')

            # Membuat pilihan filter dalam kolom agar lebih rapi
            col1, col2 = st.columns(2)

            with col1:
                # Dropdown untuk memilih kecamatan
                list_kecamatan = sorted(df['nama_kec'].unique().tolist())
                list_kecamatan.insert(0, "Semua Kecamatan")
                selected_kecamatan = st.selectbox('Pilih Kecamatan:', list_kecamatan)

            with col2:
                # Multiselect untuk memilih kolom/variabel
                all_columns = [col for col in df.columns if col not in ['nama_kec', 'nama_desa']]
                selected_columns = st.multiselect('Pilih kolom/variabel yang ingin ditampilkan:', all_columns)

            # --- Langkah 3: Menampilkan Hasil ---
            if selected_kecamatan and selected_columns:
                st.header('Langkah 3: Hasil Analisis')

                # Filter dataframe berdasarkan kecamatan yang dipilih
                if selected_kecamatan == "Semua Kecamatan":
                    filtered_df = df.copy()
                else:
                    filtered_df = df[df['nama_kec'] == selected_kecamatan]

                # Tampilkan Tabel Data
                st.subheader('Tabel Data Hasil Filter')
                
                # Menyiapkan kolom yang akan selalu ditampilkan
                display_columns = ['nama_kec', 'nama_desa'] + selected_columns
                
                st.write(f"Menampilkan **{len(filtered_df)} baris** data untuk Kecamatan **{selected_kecamatan}**.")
                # Menggunakan st.dataframe untuk tabel interaktif
                st.dataframe(filtered_df[display_columns])

                st.write("---") # Garis pemisah

                # Tampilkan Opsi Visualisasi
                st.subheader('Visualisasi Data')
                
                # Filter hanya kolom numerik dari yang sudah dipilih user
                numeric_cols_selected = [col for col in selected_columns if pd.api.types.is_numeric_dtype(filtered_df[col])]

                if not numeric_cols_selected:
                    st.warning("Pilih setidaknya satu kolom berisi **angka** untuk dapat membuat visualisasi.")
                else:
                    # Bagi layout menjadi dua kolom untuk pilihan
                    viz_col1, viz_col2 = st.columns(2)
                    with viz_col1:
                        # Dropdown untuk memilih tipe chart
                        chart_type = st.selectbox("Pilih Tipe Visualisasi:", ["Bar Chart", "Line Chart", "Area Chart"])
                    with viz_col2:
                        # Dropdown untuk memilih variabel yang akan divisualisasikan (sumbu Y)
                        y_axis = st.selectbox('Pilih variabel untuk divisualisasikan:', numeric_cols_selected)
                    
                    if y_axis:
                        # Mengatur 'nama_desa' sebagai index agar menjadi sumbu X pada grafik
                        chart_data = filtered_df.set_index('nama_desa')
                        
                        st.write(f"Menampilkan **{chart_type}** untuk variabel **'{y_axis}'**.")

                        # Menampilkan chart berdasarkan pilihan user
                        if chart_type == "Bar Chart":
                            st.bar_chart(chart_data, y=y_axis)
                        elif chart_type == "Line Chart":
                            st.line_chart(chart_data, y=y_axis)
                        elif chart_type == "Area Chart":
                            st.area_chart(chart_data, y=y_axis)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses file: {e}")