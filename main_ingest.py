import boto3
import yaml
import os
from dotenv import load_dotenv

# Memuat variabel dari .env
load_dotenv()

# Memuat konfigurasi dari sources.yaml
with open("sources.yaml", "r") as f:
    config = yaml.safe_load(f)

def run_ingestion():
    # Inisialisasi client S3
    s3 = boto3.client(
        's3',
        endpoint_url=f"http://{os.getenv('MINIO_ENDPOINT')}",
        aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('MINIO_SECRET_KEY'),
        region_name='us-east-1'
    )

    # Loop melalui setiap dataset di sources.yaml
    for dataset in config['datasets']:
        bucket_name = dataset['target_bucket']
        
        # Cek dan buat bucket jika belum ada
        try:
            s3.head_bucket(Bucket=bucket_name)
        except:
            s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' berhasil dibuat.")

        # Eksekusi upload
        print(f"Sedang mengunggah {dataset['name']} ({dataset['source_path']})...")
        try:
            s3.upload_file(
                dataset['source_path'], 
                bucket_name, 
                dataset['target_object_name']
            )
            print(f"✅ Berhasil mengunggah {dataset['target_object_name']} ke bucket {bucket_name}")
        except Exception as e:
            print(f"❌ Gagal mengunggah {dataset['name']}: {e}")

if __name__ == "__main__":
    run_ingestion()