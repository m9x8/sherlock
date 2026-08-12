import Levenshtein
from typing import List

class Permutator:
    def __init__(self):
        self.leetspeak_map = {
            'a': ['4', '@'],
            'e': ['3'],
            'i': ['1', '!'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7']
        }
        self.delimiters = ['.', '_', '-']

    def generate_variants(self, base_string: str) -> List[str]:
        """
        Generates common variants of a username or base string,
        including leetspeak and delimiter insertions.
        """
        variants = {base_string}

        # Leetspeak simple replacements (first pass)
        for char, replacements in self.leetspeak_map.items():
            if char in base_string:
                for rep in replacements:
                    variants.add(base_string.replace(char, rep))

        # Delimiter insertions
        if len(base_string) > 2:
            midpoint = len(base_string) // 2
            for delim in self.delimiters:
                variants.add(base_string[:midpoint] + delim + base_string[midpoint:])

        # Common suffixes
        suffixes = ['123', 'official', 'real', 'x']
        for suffix in suffixes:
            variants.add(f"{base_string}{suffix}")
            variants.add(f"{base_string}_{suffix}")

        return list(variants)

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculates a similarity score between two strings based on Levenshtein distance.
        Returns a float between 0.0 (completely different) and 1.0 (identical).
        """
        distance = Levenshtein.distance(str1, str2)
        max_len = max(len(str1), len(str2))

        if max_len == 0:
            return 1.0

        return 1.0 - (distance / max_len)
