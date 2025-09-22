import csv

def write_analysis_to_csv(per_utt_results, output_csv_path):
    with open(output_csv_path, "w", newline="", encoding="utf-8") as fout:
        w = csv.writer(fout)

        def write_block(header, key_exists, key_prod, key_notes, total_label):
            w.writerow(["Selected Utterances", "Cleaned Utterance"] + header)
            total = 0
            for r in per_utt_results:
                w.writerow([
                    r["utterance"],
                    r["cleaned"],
                    "yes" if r[key_exists] else "no",
                    "yes" if r[key_prod] else "no",
                    r[key_notes],
                    r[key_prod]
                ])
                total += r[key_prod]
            w.writerow(["", "", "", "", total_label, str(total)])
            w.writerow([""] * 6)
            w.writerow([""] * 6)

        # article
        write_block(
            ["Is there an article with a noun subject?",
             "is it in a productive context?",
             "How do I know? (article)",
             "Article Productivity"],
            "art_exists", "art_productive", "art_notes",
            "Total Article Productivity Score ="
        )

        # aux
        write_block(
            ["Is there an auxiliary?",
             "is it in a productive context? (aux)",
             "How do I know? (aux)",
             "Auxiliary Productivity"],
            "aux_exists", "aux_productive", "aux_notes",
            "Total Auxiliary Productivity ="
        )

        # active Progressive
        w.writerow([
            "Selected Utterances", "Cleaned Utterance",
            "is there a progressive -ing morpheme in active declarative?",
            "is it productive? (active progressive)",
            "how do I know? (active progressive)",
            "Active Progressive Productivity"
        ])
        total_ap = 0
        for r in per_utt_results:
            w.writerow([
                r["utterance"], r["cleaned"],
                "yes" if r["active_prog_exists"] else "no",
                "yes" if r["active_prog_productive"] else "no",
                r["active_prog_notes"],
                r["active_prog_productive"]
            ])
            total_ap += r["active_prog_productive"]
        w.writerow(["", "", "", "", "Total Active Progressive Productivity", str(total_ap)])
        w.writerow([""] * 6)
        w.writerow([""] * 6)

        # general Progressive
        w.writerow([
            "Selected Utterances", "Cleaned Utterance",
            "is there a progressive -ing morpheme?",
            "is it productive? (general progressive)",
            "how do I know? (general progressive)",
            "General Progressive Productivity"
        ])
        total_gp = 0
        for r in per_utt_results:
            w.writerow([
                r["utterance"], r["cleaned"],
                "yes" if r["prog_exists"] else "no",
                "yes" if r["prog_productive"] else "no",
                r["prog_notes"],
                r["prog_productive"]
            ])
            total_gp += r["prog_productive"]
        w.writerow(["", "", "", "", "Total General Progressive Productivity", str(total_gp)])
