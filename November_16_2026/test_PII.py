from main import extract_pii, redact_pii

text = """
नमस्ते, मेरा नाम अनीता कुलकर्णी है।
मेरा मोबाइल नंबर 98004 51763 है।
मेरा ईमेल anita.k@example.in है।
"""

print("Original Text:")
print(text)

print("\nExtracted PII:")
print(extract_pii(text))

print("\nRedacted Text:")
print(redact_pii(text))

""" Original Text:

        नमस्ते, मेरा नाम अनीता कुलकर्णी है।
        मेरा मोबाइल नंबर 98004 51763 है।
        मेरा ईमेल anita.k@example.in है।


Extracted PII:

        [{'label': 'PERSON', 'text': 'अनीता कुलकर्णी', 'start': 18, 'end': 32}, 
        {'label': 'PHONE', 'text': '98004 51763', 'start': 54, 'end': 65}, 
        {'label': 'EMAIL' ', 'text': 'anita.k@example.in', 'start': 80, 'end': 98}]

Redacted Text:

        नमस्ते, मेरा नाम [PERSON] है।
        मेरा मोबाइल नंबर [PHONE] है।
        मेरा ईमेल [EMAIL] है।

"""