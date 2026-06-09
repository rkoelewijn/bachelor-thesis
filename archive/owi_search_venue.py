import duckdb
import time
import textwrap

def find_any_doornroosje_urls():
    print("📡 OWI URL EXPLORER: Searching for 'doornroosje.nl' across 2026...")
    con = duckdb.connect()
    start_total = time.perf_counter()
    
    try:
        # 1. High-Stability Network Config
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute("SET allow_asterisks_in_http_paths = true;")
        con.execute("SET parquet_metadata_cache = true;")
        
        # Extended timeouts for the Finland S3 -> Ede/Nijmegen VPN route
        con.execute("SET http_timeout = 300000;") # 5 minutes
        con.execute("SET http_retries = 5;")
        con.execute("SET enable_server_cert_verification = false;") # Your SSL bypass
        
        con.execute("""
            CREATE PERSISTENT SECRET IF NOT EXISTS ows_remote_index (
                TYPE s3,
                ENDPOINT 'a3s.fi',
                URL_STYLE 'path',
                SCOPE 's3://2006391-owi-remote-index'
            );
        """)

        # 2. Optimized Path Logic
        # We target ONLY the documents folder. Note the glob pattern:
        # year/month/day/collection/documents/language/file.parquet
        # We start with March (3) as it's the most likely stable 2026 shard.
        base_path = "s3://2006391-owi-remote-index/year=2026/month=*/day=*/collection=*/documents/language=nld/*.parquet"

        # 3. The URL Search Query
        # We only select URL to keep data transfer tiny
        sql_query = textwrap.dedent(f"""--sql
            SELECT DISTINCT url 
            FROM read_parquet('{base_path}')
            WHERE url LIKE '%doornroosje.nl/event%'
            LIMIT 20;
        """).strip()

        print("⏳ Querying S3 Metadata (this may take 60-120 seconds)...")
        start_query = time.perf_counter()
        
        results = con.execute(sql_query).fetchall()
        
        end_query = time.perf_counter()
        print(f"⏱️ Query Execution Time: {end_query - start_query:.2f} seconds")

        if results:
            print(f"\n✅ SUCCESS! Found {len(results)} URLs from Doornroosje:")
            for i, row in enumerate(results, 1):
                print(f"  {i}. 🔗 {row[0]}")
        else:
            print("\n⚠️ No URLs found in the March 2026 shards.")
            print("💡 Trying a broader search or checking February might be next.")

    except Exception as e:
        print(f"\n🚨 ERROR: {e}")
        if "No files found" in str(e):
            print("\n🔍 Troubleshooting: The month '3' path might not be ready.")
            print("   Try changing base_path to: month=2 (February) or month=1 (January).")
            
    finally:
        end_total = time.perf_counter()
        print(f"\n🏁 Total Pipeline Time: {end_total - start_total:.2f} seconds")
        con.close()

if __name__ == "__main__":
    find_any_doornroosje_urls()