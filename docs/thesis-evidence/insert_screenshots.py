import os
import docx
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

draft_path = r'c:\Users\n tech\OneDrive\Desktop\mindshield\docs\MindShield_FYP1_Thesis_Draft.docx'
screenshot_dir = r'c:\Users\n tech\OneDrive\Desktop\mindshield\docs\thesis-evidence\screenshots'

doc = docx.Document(draft_path)

# Helper to find paragraph by text
def find_p_by_text(text_query):
    for p in doc.paragraphs:
        if text_query in p.text:
            return p
    return None

# Helper to insert paragraph after a target paragraph
def insert_paragraph_after(paragraph, text, style=None):
    new_p = paragraph._parent.add_paragraph(text, style)
    paragraph._p.addnext(new_p._p)
    return new_p

# Helper to insert picture after a target paragraph
def insert_picture_after(paragraph, img_path, caption_text):
    # Insert caption paragraph (which goes below the image)
    p_cap = insert_paragraph_after(paragraph, caption_text, style='Figure Caption')
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Insert image paragraph (which goes on top of the caption)
    p_img = insert_paragraph_after(paragraph, "", style='Normal')
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_img.add_run()
    run.add_picture(img_path, width=Inches(2.5)) # Portrait aspect ratio, 2.5 inches width is optimal
    
    return p_img, p_cap

target_query = "UI screenshots are represented in Figures 3-8 through 3-16 [FIGURE 3-X — ACTUAL UI SCREENSHOT REQUIRED]."
p_target = find_p_by_text(target_query)

if not p_target:
    # Check if we already updated it
    target_query = "UI screenshots are represented in Figures 3-8 through 3-16:"
    p_target = find_p_by_text(target_query)

if p_target:
    p_target.text = "UI screenshots are represented in Figures 3-8 through 3-16:"
    
    figures = [
        ("Figure_3-8_Permissions_Dialog.png", "Figure 3-8 Native Permissions Request Dialog on Android"),
        ("Figure_3-9_Inbox_Dashboard.png", "Figure 3-9 Thread-Based SMS Inbox Dashboard Interface"),
        ("Figure_3-10_Message_Stream.png", "Figure 3-10 Detailed Message Stream View"),
        ("Figure_3-11_Ham_Message_Indicator.png", "Figure 3-11 Normal (HAM) Transaction Message Notification"),
        ("Figure_3-12_English_Phishing_Warning.png", "Figure 3-12 Suspicious English Phishing Warning (distilbert-pakscam-v1)"),
        ("Figure_3-13_Roman_Urdu_Phishing_Warning.png", "Figure 3-13 Localized Roman Urdu Phishing Warning (distilbert-pakscam-v3)"),
        ("Figure_3-14_Heuristic_Threat_Indicators.png", "Figure 3-14 Heuristic Threat Indicators and Highlighted Keywords"),
        ("Figure_3-15_Model_Server_Configuration.png", "Figure 3-15 Model Server Configuration Settings Panel"),
        ("Figure_3-16_API_Offline_Fallback.png", "Figure 3-16 API Offline/No Connection Fallback Screen")
    ]
    
    # We insert them sequentially after p_target. To maintain sequential ordering,
    # we insert them in reverse order, or keep updating the insert pointer.
    # If we insert them in reverse order, they will appear in normal order!
    # For example, if we insert Figure 3-16 first after p_target, then Figure 3-15 after p_target,
    # then Figure 3-15 will be between p_target and Figure 3-16!
    # This is exactly correct!
    
    inserted_count = 0
    for filename, caption in figures[::-1]:
        img_path = os.path.join(screenshot_dir, filename)
        if os.path.exists(img_path):
            insert_picture_after(p_target, img_path, caption)
            print(f"Integrated screenshot: {filename}")
            inserted_count += 1
            
    if inserted_count > 0:
        doc.save(draft_path)
        print(f"\nSUCCESS: Successfully integrated {inserted_count} screenshots into the master DOCX.")
    else:
        print("\nNo screenshots were found in the screenshots directory yet. Run the capture utility first.")
else:
    print("ERROR: Target UI screenshot paragraph placeholder not found in document.")
