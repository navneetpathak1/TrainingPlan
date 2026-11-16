
import sys
from pathlib import Path

PII_MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "cbx-indic-pii-extractor-17M"
)

sys.path.insert(0, str(PII_MODEL_PATH))

from pii import PIIExtractor
pii = PIIExtractor()
 

def extract_pii(text: str):
    return pii.extract(text)


def redact_pii(text: str):
    return pii.redact(text)
