import duckdb
import json
import time
import textwrap
import os

def check_newsletter_coverage(json_file_path):
    print(f"📂 Loading newsletter: {json_file_path}")
    
    # 1. Load the Newsletter Data
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"🚨 JSON ERROR: Could not read file. {e}")
        return

    # 2. Initialize DuckDB
    con = duckdb.connect()
    print("📡 Initializing OWI Connection (Optimized for VPN)...")
    try:
        # Network & Stability Settings
        con.execute("INSTALL httpfs; LOAD httpfs; SET allow_asterisks_in_http_paths = true;")
        con.execute("SET http_timeout = 300000; SET enable_server_cert_verification = false;")
        con.execute("SET http_retries = 5;")
        
        # Connect to Finnish S3 Bucket
        con.execute("""
            CREATE PERSISTENT SECRET IF NOT EXISTS ows_remote_index (
                TYPE s3, ENDPOINT 'a3s.fi', URL_STYLE 'path', SCOPE 's3://2006391-owi-remote-index'
            );
        """)
        
        # Path for 2026 Dutch documents
        base_path = "s3://2006391-owi-remote-index/year=2026/month=*/day=*/collection=*/documents/language=nld/*.parquet"

        results_summary = []
        total_start = time.perf_counter()

        # Count actual artists (ignoring the TEMPLATE)
        target_count = len(data) - 1 if "TEMPLATE" in data else len(data)
        print(f"\n🔎 Scanning OWI for {target_count} artists. This will take a few minutes...\n")

        for key, item in data.items():
            # Skip your JSON template block
            if key == "TEMPLATE":
                continue

            artist = ""
            
            # Extract the artist name based on your JSON structure
            if isinstance(item, dict):
                # Prioritize 'act', fallback to 'artist' or 'name'
                artist = item.get('act') or item.get('artist') or item.get('name')
                
            # Skip if we somehow couldn't find a valid name
            if not artist or len(artist) < 2: 
                continue
            
            # Create a URL-friendly slug 
            # e.g., "Frank Boeijen" -> "frank-boeijen", "Wyatt E." -> "wyatt-e"
            artist_slug = artist.lower().replace(" ", "-").replace(".", "").replace("+", "").strip()
            
            # Print on the same line so it doesn't spam the terminal
            print(f"⏳ Checking: {artist[:30]:<30}...", end="\r")
            
            # The URL Search Query
            sql = textwrap.dedent(f"""
                SELECT DISTINCT url FROM read_parquet('{base_path}')
                WHERE url LIKE '%doornroosje.nl%' AND url LIKE '%{artist_slug}%'
                LIMIT 1;
            """).strip()
            
            start_q = time.perf_counter()
            match = con.execute(sql).fetchone()
            end_q = time.perf_counter()
            
            status = "✅ FOUND" if match else "❌ MISSING"
            url = match[0] if match else "N/A"
            
            results_summary.append({
                "artist": artist[:30], # Truncate long names for clean printing
                "status": status,
                "url": url,
                "time": end_q - start_q
            })

        # 3. Print Final Report
        print(" " * 50, end="\r") # Clear the loading line
        print("📊 --- COVERAGE REPORT ---")
        
        found_count = 0
        for res in results_summary:
            print(f"{res['status']} | {res['artist']:<25} | {res['url']}")
            if res['status'] == "✅ FOUND": 
                found_count += 1
            
        print("\n--- STATS ---")
        if len(results_summary) > 0:
            coverage_pct = (found_count / len(results_summary)) * 100
            print(f"📈 Coverage: {found_count}/{len(results_summary)} ({coverage_pct:.1f}%)")
        print(f"⏱️ Total Execution Time: {time.perf_counter() - total_start:.2f} seconds")

    except Exception as e:
        print(f"\n🚨 PIPELINE ERROR: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    json_path = "newsletters.json" 
    
    print(f"📂 Checking local folder for: {json_path}")
    
    if os.path.exists(json_path):
        check_newsletter_coverage(json_path)
    else:
        print(f"🚨 Error: Could not find '{json_path}' in the current directory.")
        print(f"📍 You are currently here: {os.getcwd()}")