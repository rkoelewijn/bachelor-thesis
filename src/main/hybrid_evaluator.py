    import time
    import json
    import string
    import numpy as np
    from pathlib import Path
    from sklearn.metrics import f1_score, confusion_matrix, precision_score, recall_score, accuracy_score

    # Setup paths relative to the script location
    CURRENT_DIR = Path(__file__).resolve().parent
    ROOT_DIR = CURRENT_DIR.parent.parent 

    # NEW: We load the raw baseline results instead of parsing the raw corpus again
    RAW_BASE_PATH = ROOT_DIR / "data" / "results" / "raw_validation_results.json"
    EXPORT_PATH = ROOT_DIR / "data" / "results" / "validation_results_hybrid.json"
    HYBRID_METRICS_EXPORT_PATH = ROOT_DIR / "data" / "results" / "hybrid_metrics.json"
    GROUND_TRUTH_PATH = ROOT_DIR / "data" / "eval" / "hybrid_ground_truth_labels.json"

    # Internal modules (Notice we removed data_loader, dutch_parser, and decomposer!)
    import validator 

    # --- NUMPY TO JSON ENCODER ---
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)

    def print_header():
        print("="*60)
        print("CLOUDSPEAKERS HYBRID EVALUATOR")
        print("="*60)

    def normalize_string(s):
        """Removes punctuation, extra whitespaces, and forces lowercase for robust matching."""
        s = s.lower().strip()
        s = s.translate(str.maketrans('', '', string.punctuation))
        return " ".join(s.split())

    def load_ground_truths(filepath):
        """Loads and flattens the ground truth JSON into a normalized claim -> label dictionary."""
        if not filepath.exists():
            print(f"WARNING: Ground truth file missing at {filepath}")
            return {}
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        flat_gt = {}
        if isinstance(data, list):
            for item in data:
                claim = item.get('claim')
                ground_truth = item.get('ground_truth')
                if claim and ground_truth:
                    flat_gt[normalize_string(claim)] = ground_truth
                    
        return flat_gt

    def get_locked_threshold():
        """Loads the optimal threshold (T) calculated during the baseline evaluation."""
        return 70.0

    def synthesize_mb_facts(mb_facts, artist):
        """Converts structured MusicBrainz JSON into a list of factual English sentences."""
        sentences = [] 

        if not mb_facts or mb_facts.get("status") == "Not Found":
            return sentences
        
        if "area" in mb_facts and mb_facts.get("area") != "Unknown":
                sentences.append(f"{artist} originates from {mb_facts['area']}.")
        
        if "country" in mb_facts and mb_facts.get("country") != "Unknown" and mb_facts.get("country") != mb_facts.get("area"):
                sentences.append(f"{artist} originates from {mb_facts['country']}.")

        if "genre" in mb_facts and mb_facts.get("genre") != "Unknown":
                sentences.append(f"{artist} plays {mb_facts['genre']} music.")

        return sentences
        
    def check_extrinsic_database(claim, mb_facts, artist, locked_threshold):
        """
        Checks an unsupported claim against the MusicBrainz database.
        Returns 'INTRINSIC' if MB disproves it, 'SUPPORTED' if MB proves it, or None.
        """
        fact_sentences = synthesize_mb_facts(mb_facts, artist)

        if not fact_sentences:
            return None

        # Run NLI using the synthesized MusicBrainz facts as the premise
        mb_evaluations = validator.validate_claims([claim], fact_sentences)
        
        best_mb_ent = mb_evaluations[0].get('best_ent_score', 0)
        best_mb_con = mb_evaluations[0].get('best_con_score', 0)


        # Use the same exact thresholding logic as the text baseline
        if best_mb_con >= locked_threshold and best_mb_con > best_mb_ent: 
            return "INTRINSIC"
        elif best_mb_ent >= locked_threshold and best_mb_ent > best_mb_con:
            return "SUPPORTED"

        
        return None

    def main():
        """ 
        The evaluator loads the pre-scored raw validation results. 
        If a claim is unsupported/hallucinated, it queries the MusicBrainz 
        graph to catch Extrinsic Relation Errors, using the locked baseline threshold.
        """
        start_time = time.time()
        print_header()
        
        if not RAW_BASE_PATH.exists():
            print(f"Pipeline aborted: Raw base data missing at {RAW_BASE_PATH}")
            return
            
        with open(RAW_BASE_PATH, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
            
        locked_t = get_locked_threshold()
        
        print(f"Loaded locked Baseline Threshold: {locked_t:.2f}")
        print(f"Loaded {len(corpus)} pre-scored artist entries for hybrid evaluation.\n")

        final_output_data = []
        valid_evals = []
        
        # Initialize counters
        total_override_attempts = 0
        intrinsic_override_count = 0
        supported_override_count = 0

        for entry in corpus:
            artist = entry.get("artist", "Unknown")
            mb_facts = entry.get("musicbrainz_facts", {"status": "Not Found"})

            hybrid_evaluations = []

            for eval_data in entry.get("raw_validations", []):
                claim = eval_data.get('claim', 'Unknown Claim')
                ent_score = eval_data.get('best_ent_score', 0)
                con_score = eval_data.get('best_con_score', 0)
                
                gt_label = eval_data.get('ground_truth', 'UNKNOWN')

                # PHASE A: Standard Text Baseline Logic (Closed-World)
                if ent_score >= locked_t and ent_score > con_score: 
                    verdict = "SUPPORTED"
                elif con_score >= locked_t and con_score > ent_score: 
                    verdict = "INTRINSIC"
                else: 
                    verdict = "EXTRINSIC"

                # PHASE B: Hybrid Database Override (Open-World)
                mb_override = False
                mb_verdict = None 

                if verdict in ["EXTRINSIC", "INTRINSIC"]:
                    mb_verdict = check_extrinsic_database(claim, mb_facts, artist, locked_t)
                    total_override_attempts += 1 
                
                    if mb_verdict == "INTRINSIC" and verdict != "INTRINSIC":
                            verdict = "INTRINSIC"
                            mb_override = True
                            intrinsic_override_count += 1 
                    elif mb_verdict == "SUPPORTED":
                            verdict = "SUPPORTED"
                            mb_override = True
                            supported_override_count += 1
                    
                eval_data['nli_verdict'] = verdict
                eval_data['mb_override'] = mb_override
                eval_data['mb_verdict_raw'] = mb_verdict 
                hybrid_evaluations.append(eval_data)
                
                if gt_label in ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]:
                    valid_evals.append(eval_data)

            entry["validation_results"] = hybrid_evaluations
            
            # Min-Pooling Aggregation for sentence level
            sentence_claims_supported = all(e['nli_verdict'] == "SUPPORTED" for e in hybrid_evaluations)
            entry['sentence_verdict_pred'] = "CORRECT" if sentence_claims_supported else "INCORRECT"
            
            true_sentence_claims_supported = all(e['ground_truth'] == "SUPPORTED" for e in hybrid_evaluations if e['ground_truth'] in ["SUPPORTED", "INTRINSIC", "EXTRINSIC"])
            if any(e['ground_truth'] in ["SUPPORTED", "INTRINSIC", "EXTRINSIC"] for e in hybrid_evaluations):
                entry['sentence_ground_truth'] = "CORRECT" if true_sentence_claims_supported else "INCORRECT"
            
            final_output_data.append(entry)

        # =====================================================================
        # CHECKPOINT: Save the raw hybrid data to disk BEFORE doing any math!
        # =====================================================================
        print("\nSaving raw hybrid results to disk...")
        EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_output_data, f, indent=4, cls=NpEncoder, ensure_ascii=False)
        print(f"Safely saved hybrid evaluation dataset to: {EXPORT_PATH}")

        # --- METRICS CALCULATION ---
        print("\nSTAGE 4: HYBRID EVALUATION METRICS & EXPORT")
        print("-" * 60)
        
        print("\n--- Knowledge Graph Intervention Summary ---")
        print(f"Total KG Queries Attempted: {total_override_attempts}")
        print(f"Successful Overrides to INTRINSIC: {intrinsic_override_count}")
        print(f"Successful Overrides to SUPPORTED: {supported_override_count}\n")
        
        y_true_claims = [e['ground_truth'] for e in valid_evals]
        y_pred_claims = [e['nli_verdict'] for e in valid_evals]
        
        y_true_sentences = [entry['sentence_ground_truth'] for entry in final_output_data if 'sentence_ground_truth' in entry]
        y_pred_sentences = [entry['sentence_verdict_pred'] for entry in final_output_data if 'sentence_ground_truth' in entry]

        if y_true_claims:
            labels = ["SUPPORTED", "INTRINSIC", "EXTRINSIC"]
            conf_matrix_atomic = confusion_matrix(y_true_claims, y_pred_claims, labels=labels)
            macro_prec = precision_score(y_true_claims, y_pred_claims, average='macro', zero_division=0)
            macro_rec = recall_score(y_true_claims, y_pred_claims, average='macro', zero_division=0)
            macro_f1 = f1_score(y_true_claims, y_pred_claims, average='macro', zero_division=0)

            print("--- Atomic Claim Level (Ternary) ---")
            print("Confusion Matrix:")
            print(conf_matrix_atomic)
            print(f"Precision (Macro): {macro_prec:.4f}")
            print(f"Recall (Macro):    {macro_rec:.4f}")
            print(f"F1-Score (Macro):  {macro_f1:.4f}")
        
        if y_true_sentences:
            accuracy = accuracy_score(y_true_sentences, y_pred_sentences)
            y_true_binary = [1 if v == "INCORRECT" else 0 for v in y_true_sentences]
            y_pred_binary = [1 if v == "INCORRECT" else 0 for v in y_pred_sentences]
            
            error_detection_rate = recall_score(y_true_binary, y_pred_binary, zero_division=0)
            binary_f1 = f1_score(y_true_binary, y_pred_binary, zero_division=0)

            tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary).ravel()
            false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

            print("\n--- Binary Sentence Level (Min-Pooling) ---")
            print(f"Accuracy: {accuracy:.4f}")
            print(f"Error Detection Rate (Recall on INCORRECT): {error_detection_rate:.4f}")
            print(f"False Positive Rate: {false_positive_rate:.4f}")
            print(f"F1-Score (Binary): {binary_f1:.4f}")

            # JSON Export for graphing
            metrics_export = {
                "atomic_metrics": {
                    "labels": labels,
                    "confusion_matrix": conf_matrix_atomic.tolist(),
                    "precision_macro": float(macro_prec),
                    "recall_macro": float(macro_rec),
                    "f1_macro": float(macro_f1)
                },
                "binary_metrics": {
                    "accuracy": float(accuracy),
                    "error_detection_rate": float(error_detection_rate),
                    "false_positive_rate": float(false_positive_rate),
                    "f1_binary": float(binary_f1)
                }
            }
            
            HYBRID_METRICS_EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(HYBRID_METRICS_EXPORT_PATH, 'w', encoding='utf-8') as f:
                json.dump(metrics_export, f, indent=4, cls=NpEncoder)
            print(f"\nSaved metrics summary to: {HYBRID_METRICS_EXPORT_PATH}")

        elapsed = time.time() - start_time
        print(f"Hybrid Pipeline finished in {elapsed:.2f} seconds.")

    if __name__ == "__main__":
        main()