import sys
import subprocess
from pathlib import Path

# --- PATH CONFIGURATION ---
CURRENT_DIR = Path(__file__).resolve().parent
MAIN_DIR = CURRENT_DIR / "main"

SCRIPTS = {
    "1": {
        "name": "Build Evaluation Corpus (Web Scraper)",
        "file": MAIN_DIR / "build_corpus.py",
        "description": "Scrapes Doornroosje and builds the full_evaluation_corpus.json"
    },
    "2": {
        "name": "Run Baseline Pipeline (NLI Only)",
        "file": MAIN_DIR / "baseline_evaluator.py",
        "description": "Evaluates intrinsic hallucinations using XLM-RoBERTa"
    },
    "3": {
        "name": "Run Hybrid Pipeline (NLI + MusicBrainz)",
        "file": MAIN_DIR / "hybrid_evaluator.py",
        "description": "Evaluates both intrinsic and extrinsic hallucinations"
    }
}

def print_menu():
    print("\n" + "="*60)
    print(" 🎛️  CLOUDSPEAKERS THESIS PIPELINE - MASTER CONTROL")
    print("="*60)
    
    for key, info in SCRIPTS.items():
        print(f"  [{key}] {info['name']}")
        print(f"      ↳ {info['description']}")
    
    print("-" * 60)
    print("  [4] Run Full Pipeline Sequentially (1 ➔ 2 ➔ 3)")
    print("  [q] Quit")
    print("="*60)

def execute_script(script_path):
    """Runs the selected python file in an isolated subprocess."""
    if not script_path.exists():
        print(f"\n🚨 Error: Could not find the file at {script_path}")
        print("   Please check your file names and paths.")
        # Return False so the "Run All" loop knows to abort if a file is missing
        return False

    print(f"\n🚀 Launching {script_path.name}...\n")
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ The script {script_path.name} crashed or was interrupted.")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Pipeline execution manually aborted.")
        return False

def main():
    while True:
        print_menu()
        choice = input("\nSelect a pipeline to run (1/2/3/4) or 'q' to quit: ").strip().lower()

        if choice == 'q':
            print("Exiting Cloudspeakers CLI. Goodbye! 👋\n")
            break
            
        elif choice == '4':
            print("\n" + "🔥 "*15)
            print(" INITIATING FULL END-TO-END PIPELINE")
            print("🔥 "*15)
            
            # Loop through keys 1, 2, and 3 in order
            for step in ["1", "2", "3"]:
                print(f"\n--- Starting Step {step}: {SCRIPTS[step]['name']} ---")
                success = execute_script(SCRIPTS[step]["file"])
                
                # If a script crashes, abort the rest of the chain so we don't process bad data
                if not success:
                    print(f"\n🚨 Chain aborted at Step {step} due to an error.")
                    break
            else:
                # This 'else' belongs to the 'for' loop. It triggers only if the loop finishes without breaking.
                print("\n" + "✅ "*15)
                print(" ALL PIPELINES COMPLETED SUCCESSFULLY")
                print("✅ "*15)

        elif choice in SCRIPTS:
            execute_script(SCRIPTS[choice]["file"])
            
        else:
            print("⚠️ Invalid selection. Please choose 1, 2, 3, 4, or q.")

if __name__ == "__main__":
    main()