import sys
import os
import subprocess
from pathlib import Path

# --- PATH CONFIGURATION ---
CURRENT_DIR = Path(__file__).resolve().parent
MAIN_DIR = CURRENT_DIR / "main"

# --- GLOBAL STATE ---
TEST_MODE = False
TEST_LIMIT = 3

SCRIPTS = {
    "1": {
        "name": "Build Evaluation Corpus (Web Scraper)",
        "file": MAIN_DIR / "build_corpus.py",
        "description": "Scrapes Doornroosje and builds the full_evaluation_corpus.json"
    },
    "2": {
        "name": "Dry-Run Decomposer Claims",
        "file": MAIN_DIR / "profile_claims.py",
        "description": "Generates all atomic claims instantly (No NLI)"
    },
    "3": {
        "name": "Run Baseline Pipeline (NLI Only)",
        "file": MAIN_DIR / "baseline_evaluator.py",
        "description": "Evaluates intrinsic hallucinations using XLM-RoBERTa"
    },
    "4": {
        "name": "Run Hybrid Pipeline (NLI + MusicBrainz)",
        "file": MAIN_DIR / "hybrid_evaluator.py",
        "description": "Evaluates both intrinsic and extrinsic hallucinations"
    },
    "5": {
        "name": "Show Results",
        "file": MAIN_DIR / "evaluation_metrics.py",
        "description": "Shows performance scores."}
}

def print_menu():
    print("\n" + "="*60)
    print(" 🎛️  CLOUDSPEAKERS THESIS PIPELINE - MASTER CONTROL")
    print("="*60)
    
    for key, info in SCRIPTS.items():
        print(f"  [{key}] {info['name']}")
        print(f"      ↳ {info['description']}")
    
    print("-" * 60)
    print("  [6] Run Full Pipeline Sequentially (1 ➔ 3 ➔ 4 ➔ 5)")
    
    # Dynamic Test Mode Status UI
    mode_status = f"🟢 ON (Limit: {TEST_LIMIT} items)" if TEST_MODE else "🔴 OFF (Full Corpus)"
    print(f"  [t] Toggle Test Mode - Currently: {mode_status}")
    print("  [q] Quit")
    print("="*60)

def execute_script(script_path):
    """Runs the selected python file in an isolated subprocess."""
    if not script_path.exists():
        print(f"\n🚨 Error: Could not find the file at {script_path}")
        print("   Please check your file names and paths.")
        return False

    # Inject the test limit into the child process environment if Test Mode is ON
    env = os.environ.copy()
    if TEST_MODE:
        env["PIPELINE_TEST_LIMIT"] = str(TEST_LIMIT)
    else:
        env.pop("PIPELINE_TEST_LIMIT", None)

    print(f"\n🚀 Launching {script_path.name}...\n")
    try:
        # Pass the modified environment variables to the subprocess
        subprocess.run([sys.executable, str(script_path)], env=env, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ The script {script_path.name} crashed or was interrupted.")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Pipeline execution manually aborted.")
        return False

def main():
    global TEST_MODE
    
    while True:
        print_menu()
        choice = input("\nSelect a pipeline to run, or 't' to toggle testing: ").strip().lower()

        if choice == 'q':
            print("Exiting Cloudspeakers CLI. Goodbye! 👋\n")
            break
            
        elif choice == 't':
            TEST_MODE = not TEST_MODE
            print(f"\n⚙️ Test Mode is now {'ON' if TEST_MODE else 'OFF'}.")
            
        elif choice == '6':
            print("\n" + "🔥 "*15)
            print(" INITIATING FULL END-TO-END PIPELINE")
            print("🔥 "*15)
            
            for step in ["1", "2", "3"]:
                print(f"\n--- Starting Step {step}: {SCRIPTS[step]['name']} ---")
                success = execute_script(SCRIPTS[step]["file"])
                
                if not success:
                    print(f"\n🚨 Chain aborted at Step {step} due to an error.")
                    break
            else:
                print("\n" + "✅ "*15)
                print(" ALL PIPELINES COMPLETED SUCCESSFULLY")
                print("✅ "*15)

        elif choice in SCRIPTS:
            execute_script(SCRIPTS[choice]["file"])
            
        else:
            print("⚠️ Invalid selection. Please choose 1, 1.5, 2, 3, 4, t, or q.")

if __name__ == "__main__":
    main()