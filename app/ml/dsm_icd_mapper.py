from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class CodeMapping:
    dsm_code: str
    icd_code: str
    disorder_name: str
    description: str


MOOD_DISORDER_MAP: Dict[str, CodeMapping] = {
    "F32.0": CodeMapping("296.21", "F32.0", "Major Depressive Disorder, Mild", "Single episode, mild severity"),
    "F32.1": CodeMapping("296.22", "F32.1", "Major Depressive Disorder, Moderate", "Single episode, moderate severity"),
    "F32.2": CodeMapping("296.23", "F32.2", "Major Depressive Disorder, Severe", "Single episode, severe without psychotic features"),
    "F32.3": CodeMapping("296.24", "F32.3", "Major Depressive Disorder, Severe with Psychotic Features", "Single episode, severe with psychotic features"),
    "F33.0": CodeMapping("296.31", "F33.0", "Major Depressive Disorder, Recurrent, Mild", "Recurrent episodes, mild severity"),
    "F33.1": CodeMapping("296.32", "F33.1", "Major Depressive Disorder, Recurrent, Moderate", "Recurrent episodes, moderate severity"),
    "F33.2": CodeMapping("296.33", "F33.2", "Major Depressive Disorder, Recurrent, Severe", "Recurrent episodes, severe"),
    "F33.3": CodeMapping("296.34", "F33.3", "Major Depressive Disorder, Recurrent, Severe with Psychotic Features", "Recurrent episodes, severe with psychotic features"),
    "F34.1": CodeMapping("300.4", "F34.1", "Persistent Depressive Disorder (Dysthymia)", "Chronic depression lasting ≥2 years"),
    "F31.0": CodeMapping("296.40", "F31.0", "Bipolar I Disorder, Current Hypomanic", "Current episode hypomanic"),
    "F31.1": CodeMapping("296.41", "F31.1", "Bipolar I Disorder, Current Manic, Mild", "Current episode manic, mild"),
    "F31.2": CodeMapping("296.42", "F31.2", "Bipolar I Disorder, Current Manic, Moderate", "Current episode manic, moderate"),
    "F31.3": CodeMapping("296.43", "F31.3", "Bipolar I Disorder, Current Manic, Severe", "Current episode manic, severe"),
    "F31.4": CodeMapping("296.44", "F31.4", "Bipolar I Disorder, Current Manic, Severe with Psychotic Features", "Current episode manic, severe with psychotic features"),
    "F31.5": CodeMapping("296.50", "F31.5", "Bipolar I Disorder, Current Depressed, Mild", "Current episode depressed, mild"),
    "F31.6": CodeMapping("296.51", "F31.6", "Bipolar I Disorder, Current Depressed, Moderate", "Current episode depressed, moderate"),
    "F31.7": CodeMapping("296.52", "F31.7", "Bipolar I Disorder, Current Depressed, Severe", "Current episode depressed, severe"),
    "F31.8": CodeMapping("296.53", "F31.8", "Bipolar I Disorder, Current Depressed, Severe with Psychotic Features", "Current episode depressed, severe with psychotic features"),
    "F31.9": CodeMapping("296.7", "F31.9", "Bipolar I Disorder, Unspecified", "Unspecified bipolar I"),
    "F31.81": CodeMapping("296.89", "F31.81", "Bipolar II Disorder", "Hypomanic and depressive episodes"),
    "F34.0": CodeMapping("301.13", "F34.0", "Cyclothymic Disorder", "Chronic mood instability ≥2 years"),
    "F41.0": CodeMapping("300.01", "F41.0", "Panic Disorder", "Recurrent unexpected panic attacks"),
    "F41.1": CodeMapping("300.02", "F41.1", "Generalized Anxiety Disorder", "Excessive anxiety/worry ≥6 months"),
    "F40.10": CodeMapping("300.23", "F40.10", "Social Anxiety Disorder", "Marked fear of social situations"),
    "F43.10": CodeMapping("309.81", "F43.10", "Post-Traumatic Stress Disorder", "Exposure to traumatic event"),
    "F42": CodeMapping("300.3", "F42", "Obsessive-Compulsive Disorder", "Obsessions and/or compulsions"),
}


class DSMICDMapper:

    def map_dsm_to_icd(self, dsm_code: str) -> Optional[str]:
        for mapping in MOOD_DISORDER_MAP.values():
            if mapping.dsm_code == dsm_code:
                return mapping.icd_code
        return None

    def map_icd_to_dsm(self, icd_code: str) -> Optional[str]:
        for mapping in MOOD_DISORDER_MAP.values():
            if mapping.icd_code == icd_code:
                return mapping.dsm_code
        return None

    def get_mapping(self, code: str) -> Optional[CodeMapping]:
        return MOOD_DISORDER_MAP.get(code)

    def validate_code(self, code: str, taxonomy: str = "icd") -> bool:
        if taxonomy == "icd":
            return code in MOOD_DISORDER_MAP
        elif taxonomy == "dsm":
            return any(m.dsm_code == code for m in MOOD_DISORDER_MAP.values())
        return False

    def list_all(self) -> List[CodeMapping]:
        return list(MOOD_DISORDER_MAP.values())
