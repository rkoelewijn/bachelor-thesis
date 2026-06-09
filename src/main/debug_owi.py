import duckdb

def query_owi_remote(artist, domain="doornroosje.nl"):
    print(f"\n📡 DIRECT DUCKDB QUERY for: '{artist}' on {domain}")
    
    # Initialize an in-memory DuckDB database
    con = duckdb.connect()
    
    try:
        # Load the module to read data over HTTPS
        print("📥 Installing httpfs extension...")
        con.execute("INSTALL httpfs;")
        con.execute("LOAD httpfs;")
        
        # --- THE WILDCARD FIX ---
        print("🔓 Unlocking HTTP wildcards...")
        con.execute("SET allow_asterisks_in_http_paths = true;")
        
        # --- THE SSL FIX ---
        print("🛡️ Bypassing University SSL Interception...")
        con.execute("SET enable_server_cert_verification = false;")
        
        # This is the public research shard for Open Web Search Parquet data
        s3_path = "https://data.openwebsearch.eu/owi/parquet/latest/*.parquet"

        # The SQL Query: We scan the remote files without downloading them entirely
        sql = f"""
        SELECT url, title, content
        FROM read_parquet('{s3_path}')
        WHERE url LIKE '%{domain}%'
          AND (content ILIKE '%{artist}%' OR title ILIKE '%{artist}%')
        LIMIT 1
        """

        print("⏳ Scanning European index shards... (This may take 10-30 seconds)")
        result = con.execute(sql).fetchone()

        if result:
            url, title, content = result
            print(f"✅ FOUND A MATCH!")
            print(f"🔗 URL: {url}")
            print(f"📝 TITLE: {title}")
            print(f"📄 CONTENT SNIPPET:\n   \"{content[:300]}...\"")
            return content
        else:
            print("⚠️ No matching documents found in the OWI shards.")
            return None
            
    except duckdb.HTTPException as e:
        print(f"\n🚨 HTTP ERROR: The OWI server rejected the connection.")
        print(f"Details: {e}")
        print("Note: If you get a 403 Forbidden, it means the OWI shards are currently locked behind B2ACCESS authentication or you are not on the university VPN.")
    except Exception as e:
        print(f"\n🚨 UNEXPECTED ERROR: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    query_owi_remote("Frank Boeijen", "doornroosje.nl")