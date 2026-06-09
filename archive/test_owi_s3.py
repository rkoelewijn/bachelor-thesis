import duckdb

def test_s3_documents():
    print("📡 INITIALIZING OWI S3 DOCUMENTS CONNECTION...")
    con = duckdb.connect()

    try:
        # 1. Setup
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute("SET allow_asterisks_in_http_paths = true;")
        con.execute("SET parquet_metadata_cache = true;")

        print("🔑 Registering CSC Allas S3 Bucket...")
        con.execute("""
        CREATE PERSISTENT SECRET IF NOT EXISTS ows_remote_index (
            TYPE s3,
            ENDPOINT 'a3s.fi',
            URL_STYLE 'path',
            SCOPE 's3://2006391-owi-remote-index'
        );
        """)

        # This is the path to the DOCUMENTS table for the exact same day/shard we just tested
        documents_path = "s3://2006391-owi-remote-index/year=2025/month=12/day=25/collection=26eb6c02-e237-11f0-b4b1-8ebf6bb2cab9/documents/*/*.parquet"

        # --- TEST 1: WHAT IS IN THIS FILE? ---
        print("\n🔍 TEST 1: Inspecting the Document Schema...")
        schema = con.execute(f"DESCRIBE SELECT * FROM '{documents_path}'").fetchall()
        for col in schema:
            print(f"  - Column: {col[0]} (Type: {col[1]})")

        # --- TEST 2: IS DOORNROOSJE HERE? ---
        print("\n⏳ TEST 2: Searching for Doornroosje.nl URLs in this shard...")
        sql_query = f"""
        SELECT docid, url 
        FROM '{documents_path}'
        WHERE url LIKE '%doornroosje.nl%'
        LIMIT 5;
        """
        
        results = con.execute(sql_query).fetchall()
        
        if results:
            print("\n✅ SUCCESS! Found Doornroosje pages!")
            for row in results:
                print(f"  - DocID: {row[0]} | URL: {row[1]}")
        else:
            print("\n⚠️ No Doornroosje URLs found in this specific daily shard.")
            print("   (This is normal; they might not crawl the venue every single day).")

    except Exception as e:
        print(f"\n🚨 UNEXPECTED ERROR: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    test_s3_documents()