import io
import numpy as np
from PIL import Image, ImageChops, ImageEnhance


class ErrorLevelAnalysis:
    """
    Error Level Analysis (ELA) for image forgery and tamper region detection.
    Re-compresses an image at a specified JPEG quality level (default 95%)
    and measures error residual magnitude. High local variance indicates resaved/edited regions.
    """

    @classmethod
    def analyze_pil_image(cls, image: Image.Image, quality: int = 95) -> dict:
        # Convert to RGB mode
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Save to buffer at target JPEG quality
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        
        recompressed = Image.open(buffer)
        
        # Compute absolute difference image
        diff = ImageChops.difference(image, recompressed)
        
        # Convert diff to numpy array
        diff_np = np.array(diff)
        mean_diff = float(np.mean(diff_np))
        max_diff = float(np.max(diff_np))
        std_diff = float(np.std(diff_np))

        # Determine anomaly score (0.0 to 100.0)
        # Standard unedited JPEGs have uniform low error variance.
        # High std_diff indicates inconsistent local compression artifacts.
        if std_diff > 15.0 or max_diff > 120:
            is_suspicious = True
            tamper_score = min(100.0, round(std_diff * 4.5, 2))
            reason = f"High JPEG compression variance detected (std: {round(std_diff, 2)}). Indicates localized image edit or paste."
        else:
            is_suspicious = False
            tamper_score = min(30.0, round(std_diff * 2.0, 2))
            reason = "Uniform compression residual level consistent with unedited document."

        return {
            "tamper_score": tamper_score,
            "is_suspicious": is_suspicious,
            "mean_diff": round(mean_diff, 2),
            "max_diff": round(max_diff, 2),
            "std_diff": round(std_diff, 2),
            "reason": reason
        }
