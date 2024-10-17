# KI-Nutzungshinweis: dieser Codes wurde mithilfe von GPT-basierten KI-Tools generiert (GPT-4o).
# KI-basierte Anpassungen und Überarbeitungen wurden nachträglich durchgeführt.

import json
import os


class ProgressManager:
    def __init__(self, tested_file, processed_file):
        self.tested_file = tested_file
        self.processed_file = processed_file
        self.tested_combinations = self.load_tested_combinations()
        self.processed_combinations = self.load_processed_combinations()

    def load_tested_combinations(self):
        """Lade die getesteten Kombinationen aus der JSON-Datei."""
        try:
            with open(self.tested_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der getesteten Kombinationen: {e}")
            return []

    def load_processed_combinations(self):
        """Lade die bereits ausgewerteten Kombinationen aus der JSON-Datei."""
        if os.path.exists(self.processed_file):
            try:
                with open(self.processed_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der verarbeiteten Kombinationen: {e}")
                return []
        return []

    def save_processed_combinations(self):
        """Speichere die verarbeiteten Kombinationen."""
        try:
            with open(self.processed_file, 'w') as f:
                json.dump(self.processed_combinations, f)
            print("Verarbeitete Kombinationen erfolgreich gespeichert.")
        except Exception as e:
            print(f"Fehler beim Speichern der verarbeiteten Kombinationen: {e}")

    def get_unprocessed_combinations(self, batch_size=100):
        """Erhalte eine Liste von ungetesteten Kombinationen in Batches."""
        unprocessed_combinations = [
            comb for comb in self.tested_combinations if comb not in self.processed_combinations
        ]
        return unprocessed_combinations[:batch_size]

    def mark_as_processed(self, batch):
        """Markiere eine Liste von Kombinationen als verarbeitet."""
        self.processed_combinations.extend(batch)
        self.save_processed_combinations()
