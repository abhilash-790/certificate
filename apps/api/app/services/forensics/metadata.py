from typing import Dict, Any


class MetadataAnalyzer:
    """
    Analyzes document metadata for editing software footprints (Photoshop, Canva, GIMP)
    and creation/modification date discrepancies.
    """

    SUSPICIOUS_PRODUCERS = [
        "photoshop", "canva", "gimp", "adobe illustrator", "inkscape",
        "pdf2image", "sejda", "smallpdf"
    ]

    @classmethod
    def analyze_metadata(cls, meta_dict: Dict[str, Any]) -> dict:
        producer = str(meta_dict.get("producer", "")).lower()
        creator = str(meta_dict.get("creator", "")).lower()
        software = f"{producer} {creator}"

        flagged_tools = [tool for tool in cls.SUSPICIOUS_PRODUCERS if tool in software]

        if flagged_tools:
            return {
                "result": "WARN",
                "score": 65.0,
                "reason": f"Editing software footprint detected in metadata: {', '.join(flagged_tools)}.",
                "flagged_software": flagged_tools
            }

        return {
            "result": "PASS",
            "score": 0.0,
            "reason": "Standard producer metadata.",
            "flagged_software": []
        }
