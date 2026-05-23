# Analisis Prediktif Turnover Karyawan

### Proyek Akhir — Big Data dan Analitik (CSD60707)

**Universitas Brawijaya · Program Studi Sistem Informasi · 2026**

## 

## Arsitektur Sistem

Proyek menggunakan pola **Medallion Architecture** — data mengalir melalui tiga lapisan dengan tingkat kematangan yang berbeda, semuanya disimpan di **MinIO Object Storage**.

```
┌────────────────────────────────────────────────────────────────────┐
│                        MEDALLION ARCHITECTURE                      │
│                                                                    │
│  CSV (Lokal)                                                       │
│      │                                                             │
│      ▼  main\_ingest.py + sources.yaml                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  MinIO Object Storage                        │  │
│  │                                                              │  │
│  │  BRONZE ──────► SILVER ──────────────────► GOLD              │  │
│  │  (Raw CSV)      (Cleaned, Parquet)         (ML-Ready,        │  │
│  │                                             Parquet)         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          │  S3A Connector                          │
│                          ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          Apache Spark Cluster (Docker)                       │  │
│  │                                                              │  │
│  │  silver\_layer.py ──► gold\_layer.py ──► ml\_training.py        │  │
│  │  (EDA + Cleaning)    (Feature Eng.)    (RF + Evaluasi)       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          │                                         │
│                          ▼                                         │
│               JupyterLab (Notebook \& Visualisasi)                  │
│                          │                                         │
│                          ▼                                         │
│                    HCM Manager (Insight)                           │
└────────────────────────────────────────────────────────────────────┘
```

**Penjelasan tiap layer:**

|Layer|Path di MinIO|Format|Isi|
|-|-|-|-|
|**Bronze**|`datalake/bronze/`|CSV|Data mentah dari Kaggle, tidak dimodifikasi. Menjadi *single source of truth*.|
|**Silver**|`datalake/silver/`|Parquet|Data setelah cleaning — tidak ada nilai kosong, duplikat dihapus, whitespace dibersihkan.|
|**Gold**|`datalake/gold/`|Parquet|Data siap untuk machine learning — sudah di-encode dan dirakit menjadi feature vector 55 dimensi.|

\---

## Stack Teknologi

|Komponen|Teknologi|Fungsi|
|-|-|-|
|**Ingestion**|Python, boto3|Membaca CSV lokal dan mengunggah ke MinIO|
|**Storage**|MinIO (S3-compatible)|Data lake terdistribusi per layer|
|**Processing**|Apache Spark, PySpark|ETL, EDA, dan feature engineering|
|**ML Engine**|Spark MLlib|Training Random Forest, hyperparameter tuning, evaluasi|
|**Orchestration**|Docker Compose|Menjalankan seluruh komponen dalam satu jaringan terisolasi|
|**Interface**|JupyterLab|Eksplorasi data dan visualisasi interaktif|
|**Konfigurasi**|`sources.yaml`, `.env`|Mapping dataset dan kredensial sensitif|

\---

## Struktur Proyek

```
PROJECT\_BDA/

├── config/                      # Direktori konfigurasi ekosistem

│   └── sources.yaml             # Parameter koneksi sumber data \& endpoint MinIO

├── notebooks/                   # JupyterLab Notebooks untuk analisis \& eksperimen

│   ├── 01\_data\_preprocessing.ipynb   # Tahap EDA, cleaning, dan preprocessing (Silver)

│   ├── 02-AUC-ROC.ipynb              # Implementasi model Random Forest \& tuning (Gold)

│   ├── correlation\_matrix.png        # Hasil visualisasi korelasi fitur

│  

├── report/                      # Aset gambar untuk dokumentasi dan laporan

│   └── images/

│       ├── correlation\_matrix.png

│       ├── eda\_categorical.png

│       └── TOP 10 Feature Importance.jpeg

├── test.csv                     # Dataset pengujian mentah (lokal)

├── train.csv                    # Dataset pelatihan mentah (lokal)

├── main\_ingest.py               # Skrip otomatis Ingestion Python (Lokal -> MinIO Bronze)

├── docker-compose.yml           # Orkestrasi container Docker (Spark, MinIO, JupyterLab)

├── .env                         # Konfigurasi variabel lingkungan (Kredensial MinIO)

└── requirements.txt             # Dependensi pustaka Python yang dibutuhkan

```

\---

## Prasyarat

Pastikan semua perangkat lunak berikut sudah terpasang di mesin kamu sebelum memulai:

* **Docker Desktop** (Windows/macOS) atau Docker Engine + Compose (Linux)

  * Docker daemon harus dalam keadaan berjalan
* **Python 3.10+** — untuk menjalankan skrip ingestion secara lokal
* **Port berikut tidak boleh dipakai** proses lain di mesin kamu:

|Port|Digunakan oleh|
|-|-|
|`9000`|MinIO API|
|`9001`|MinIO Console (UI)|
|`7077`|Spark Master|
|`8080`|Spark Master UI|
|`8888`|JupyterLab|

\---

## Instalasi \& Setup

### 1\. Clone Repository

```bash
git clone https://github.com/papercoldmint/PROJECT\_BDA.git
cd PROJECT\_BDA
```

### 2\. Siapkan File Konfigurasi

Salin template konfigurasi dan isi sesuai kebutuhan:

```bash
# Linux / macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Isi file `.env` dengan nilai berikut (sesuaikan jika perlu):

```env
MINIO\_ENDPOINT=localhost:9000
MINIO\_ACCESS\_KEY=admin
MINIO\_SECRET\_KEY=password123
MINIO\_SECURE=False
```

### 3\. Siapkan Dataset

Download dataset dari Kaggle dan letakkan di folder `data/`:

```
data/
├── train.csv
└── test.csv
```

Sumber dataset: [Employee Attrition Dataset — stealthtechnologies/employee-attrition-dataset](https://www.kaggle.com/datasets/stealthtechnologies/employee-attrition-dataset)

### 4\. Jalankan Seluruh Stack (Docker)

Perintah berikut akan menghidupkan **semua container sekaligus** — MinIO, Spark Master, Spark Worker, dan JupyterLab:

```bash
docker-compose up -d
```

Cek status container — pastikan semua berstatus `running`:

```bash
docker-compose ps
```

Kamu akan melihat 4–5 container aktif, seperti:

```
NAME                STATUS
bda-minio           running
bda-spark-master    running
bda-spark-worker    running
bda-jupyter         running
```

### 5\. Pasang Dependensi Python (untuk ingestion lokal)

```bash
# Buat virtual environment (disarankan)
python -m venv .venv

# Aktifkan — Linux/macOS
source .venv/bin/activate

# Aktifkan — Windows (PowerShell)
.\\.venv\\Scripts\\Activate.ps1

# Install dependensi
pip install -r requirements.txt
```

\---

## Alur Eksekusi

Jalankan pipeline secara **berurutan** sesuai tahapan di bawah ini.

\---

### Tahap 1 — Data Ingestion

**File:** `src/main\_ingest.py`  
**Tujuan:** Membaca file CSV dari folder lokal `data/` dan mengunggahnya ke **Bronze Layer** di MinIO.

```bash
python src/main\_ingest.py
```

**Yang terjadi saat dijalankan:**

1. Skrip membaca konfigurasi mapping dataset dari `sources.yaml`.
2. Memvalidasi keberadaan file `train.csv` dan `test.csv` di folder `data/`.
3. Membuka koneksi ke MinIO menggunakan kredensial dari `.env`.
4. Mengunggah setiap file ke path yang sudah dikonfigurasi di MinIO.
5. Menyimpan file log metadata (JSON) untuk keperluan audit.

**Output yang diharapkan:**

```
Mengunggah Training Data...
✅ Selesai: Data \& Metadata untuk employee\_train berhasil diingest.
Mengunggah Testing Data...
✅ Selesai: Data \& Metadata untuk employee\_test berhasil diingest.
```

**Hasil di MinIO:**

```
datalake/bronze/
├── train/
│   └── train.csv
├── test/
│   └── test.csv
└── \_metadata/
    ├── employee\_train\_log.json
    └── employee\_test\_log.json
```

Kamu dapat memverifikasi hasilnya di MinIO Console: [http://localhost:9001](http://localhost:9001)

\---

### Tahap 2 — EDA \& Data Cleaning

**Notebook:** `notebooks/02\_data\_preprocessing-Copy1.ipynb`  
**Tujuan:** Membaca data dari Bronze Layer, melakukan eksplorasi, membersihkan data, dan menyimpan hasilnya ke **Silver Layer**.

Buka JupyterLab di browser: [http://localhost:8888](http://localhost:8888), kemudian buka dan jalankan notebook `silver\_layer.ipynb` sel per sel.

**Proses yang dijalankan:**

**a. Membaca data dari Bronze Layer**

```python
df\_train = spark.read.csv("s3a://datalake/bronze/train/train.csv",
                          header=True, inferSchema=True)
```

**b. Exploratory Data Analysis (EDA)**

* Statistik deskriptif tiap fitur (mean, std, min, max)
* Distribusi label `Attrition` — ditemukan: 47,55% *left*, 52,45% *stayed* (seimbang)
* Boxplot fitur numerik vs. status attrition
* Bar chart fitur kategorikal vs. status attrition
* Deteksi outlier menggunakan metode **IQR** (Interquartile Range)
* Heatmap **correlation matrix** antar fitur numerik

**c. Data Cleaning**

|Langkah|Temuan|Tindakan|
|-|-|-|
|Cek missing values|Tidak ditemukan|Tidak perlu imputasi|
|Cek duplikat|0 duplikat dari 59.598 baris|Tidak ada yang dihapus|
|Trim whitespace|16 kolom string|Dibersihkan dengan `trim()`|
|Drop kolom tidak relevan|`Employee ID`|Dihapus (bukan prediktor)|

**d. Simpan ke Silver Layer**

```python
df\_clean.write.mode("overwrite").parquet("s3a://datalake/silver/employee-attrition/")
```

**Output:** DataFrame bersih berukuran **59.598 baris × 23 kolom**, tersimpan di Silver Layer dalam format Parquet.

\---

### Tahap 3 — Feature Engineering

**Notebook:** `notebooks/02\_data\_preprocessing-Copy1.ipynb`  
**Tujuan:** Mengubah fitur kategorikal menjadi representasi numerik dan merakitnya menjadi satu feature vector, lalu menyimpan hasilnya ke **Gold Layer**.

Buka dan jalankan `gold\_layer.ipynb` di JupyterLab.

**Pipeline transformasi:**

```
Fitur Kategorikal (15 kolom)
        │
        ▼  StringIndexer
        │  (string → indeks integer, berdasarkan frekuensi)
        │  Contoh: Gender {Female, Male} → {0, 1}
        │
        ▼  OneHotEncoder (dropLast=True)
        │  (indeks → vektor biner, hindari dummy variable trap)
        │  Contoh: Male(1) → \[0, 1]
        │
        ▼
 Fitur Numerik (7 kolom) ──┐
 \[Langsung digunakan]       │
                            ▼
                    VectorAssembler
                    (gabungkan semua → 1 kolom "features")
                            │
                            ▼
              DenseVector 55 dimensi  +  kolom "label" (0/1)
```

**Hasil split data:**

```
Total dataset:  59.598 baris
Train set (80%): 47.826 baris  →  24.809 stayed, 23.017 left
Test set  (20%): 11.772 baris  →   6.159 stayed,  5.613 left
```

Pembagian dilakukan secara **stratified** (proporsi kelas terjaga) dengan `seed=42` agar hasilnya dapat direproduksi.

**Simpan ke Gold Layer:**

```python
df\_encoded.write.mode("overwrite").parquet("s3a://datalake/gold/employee-attrition/")
```

\---

### Tahap 4 — Model Training \& Evaluasi

**Notebook:** `notebooks/03-AUC-ROC.ipynb`  
**Tujuan:** Melatih model **Random Forest**, melakukan hyperparameter tuning, mengevaluasi performa, dan mengekstrak *feature importance*.

Buka dan jalankan `03-AUC-ROC.ipynb` di JupyterLab.

**a. Melatih Model Baseline**

```python
rf\_baseline = RandomForestClassifier(
    labelCol="label",
    featuresCol="features",
    numTrees=100,
    maxDepth=10
)
baseline\_model = rf\_baseline.fit(train\_split)
```

**b. Hyperparameter Tuning via GridSearch**

```python
paramGrid = (ParamGridBuilder()
    .addGrid(rf\_tuned.numTrees, \[20, 50, 100])
    .addGrid(rf\_tuned.maxDepth, \[5, 8, 12])
    .build())

cv = CrossValidator(
    estimator=rf\_tuned,
    estimatorParamMaps=paramGrid,
    evaluator=roc\_evaluator,   # AUC-ROC sebagai metrik utama
    numFolds=3
)
cv\_model    = cv.fit(train\_split)
best\_model  = cv\_model.bestModel
```

Total kombinasi yang diuji: **9 model** (3 nilai `numTrees` × 3 nilai `maxDepth`), masing-masing dievaluasi dengan **3-fold cross-validation**.

**c. Evaluasi Model**

```python
best\_preds = best\_model.transform(test\_split)

metrics = {
    "Accuracy" : mc\_evaluator.evaluate(best\_preds, {mc\_evaluator.metricName: "accuracy"}),
    "F1 Score" : mc\_evaluator.evaluate(best\_preds, {mc\_evaluator.metricName: "f1"}),
    "Precision": mc\_evaluator.evaluate(best\_preds, {mc\_evaluator.metricName: "weightedPrecision"}),
    "Recall"   : mc\_evaluator.evaluate(best\_preds, {mc\_evaluator.metricName: "weightedRecall"}),
    "AUC-ROC"  : roc\_evaluator.evaluate(best\_preds)
}
```

**d. Ekstraksi Feature Importance**

```python
feature\_importances = best\_model.featureImportances
# Visualisasikan top-10 fitur berpengaruh
```

\---

## Struktur Output MinIO

Setelah seluruh pipeline selesai dijalankan, struktur bucket `datalake` di MinIO akan terlihat seperti ini:

```
datalake/
│
├── bronze/                          ← Tahap 1 (Ingestion)
│   ├── train/
│   │   └── train.csv                  (59.598 baris, 24 kolom)
│   ├── test/
│   │   └── test.csv
│   └── \_metadata/
│       ├── employee\_train\_log.json    (timestamp, ukuran file, status)
│       └── employee\_test\_log.json
│
├── silver/                          ← Tahap 2 (EDA \& Cleaning)
│   └── employee-attrition/
│       └── part-\*.parquet             (59.598 baris × 23 kolom, Parquet)
│
└── gold/                            ← Tahap 3 \& 4 (Feature Eng. + ML)
    └── employee-attrition/
        └── part-\*.parquet             (59.598 baris × 55 kolom, Parquet)
                                       — kolom "features" (DenseVector 55-dim)
                                       — kolom "label" (0 / 1)
```

\---

## Hasil \& Performa Model

### Perbandingan Baseline vs. Best Model

|Metrik|Baseline (`maxDepth=10`)|Best Model (`maxDepth=12`)|Peningkatan|
|-|:-:|:-:|:-:|
|**Accuracy**|74,32%|**74,71%**|+0,39%|
|**Precision**|74,31%|**74,71%**|+0,40%|
|**Recall**|74,32%|**74,71%**|+0,39%|
|**F1-Score**|74,31%|**74,71%**|+0,40%|
|**AUC-ROC**|82,87%|**83,19%**|+0,32%|

> AUC-ROC \*\*83,19%\*\* masuk kategori \*\*Good\*\* (rentang 0,8–0,9), artinya model mampu membedakan karyawan yang akan keluar dari yang akan bertahan dengan tingkat keandalan yang baik.

### Confusion Matrix (Test Set: 11.762 data)

```
                    Prediksi Bertahan   Prediksi Keluar
Aktual Bertahan        4.743 (TN)         1.492 (FP)
Aktual Keluar          1.483 (FN)         4.044 (TP)
```

* **False Positive (1.492):** Diprediksi keluar, ternyata bertahan — potensi biaya intervensi yang sia-sia.
* **False Negative (1.483):** Diprediksi bertahan, ternyata keluar — karyawan berisiko yang terlewat.
* Kedua jenis kesalahan hampir seimbang → model tidak bias ke satu kelas.

### Top 10 Faktor Penyebab Turnover

|Peringkat|Fitur|Importance|
|:-:|-|:-:|
|1|Job Level|**22,88%**|
|2|Marital Status|**18,35%**|
|3|Remote Work|**11,53%**|
|4|Work-Life Balance|7,93%|
|5|Distance from Home|3,99%|
|6|Years at Company|3,25%|
|7|Number of Promotions|3,21%|
|8|Company Reputation|3,00%|
|9|Education Level|2,99%|
|10|Age|2,91%|

\---

## Akses Layanan

Setelah `docker-compose up -d`, layanan berikut dapat diakses lewat browser:

|Layanan|Alamat|Keterangan|
|-|-|-|
|**MinIO Console**|[http://localhost:9001](http://localhost:9001)|UI untuk melihat bucket \& file|
|**MinIO API**|`http://localhost:9000`|Endpoint S3-compatible|
|**Spark Master UI**|[http://localhost:8080](http://localhost:8080)|Monitor Spark jobs \& workers|
|**JupyterLab**|[http://localhost:8888](http://localhost:8888)|Notebook interaktif|

Kredensial default MinIO Console (sesuai `.env`):

* Username: `admin`
* Password: `password123`

\---

## Anggota Tim

|Nama|NIM|Peran|
|-|-|-|
|Gangsar Wijayanto|245150407111022|Data Engineer|
|Natasya Alfanisa Thomas|245150407111088|Data Analyst|
|Wijdan Shafa Azhar|235150407111054|ML Engineer|
|Divana Mutiara Zaquina|245150400111053|Project Manager|

**Dosen Pengampu:** Ir. Nanang Yudi Setiawan, S.T., M.Kom.

\---



