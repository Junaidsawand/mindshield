import os
import subprocess
import sys

adb_path = r"C:\Users\n tech\AppData\Local\Android\Sdk\platform-tools\adb.exe"
screenshot_dir = r"c:\Users\n tech\OneDrive\Desktop\mindshield\docs\thesis-evidence\screenshots"

os.makedirs(screenshot_dir, exist_ok=True)

figures = [
    ("Figure_3-8_Permissions_Dialog.png", "Figure 3-8: Native Permissions Request dialog"),
    ("Figure_3-9_Inbox_Dashboard.png", "Figure 3-9: Thread-Based SMS Inbox dashboard"),
    ("Figure_3-10_Message_Stream.png", "Figure 3-10: Detailed Message Stream view"),
    ("Figure_3-11_Ham_Message_Indicator.png", "Figure 3-11: Normal (HAM) Transaction Message indicator"),
    ("Figure_3-12_English_Phishing_Warning.png", "Figure 3-12: Suspicious English Phishing Warning card"),
    ("Figure_3-13_Roman_Urdu_Phishing_Warning.png", "Figure 3-13: Localized Roman Urdu Phishing warning card"),
    ("Figure_3-14_Heuristic_Threat_Indicators.png", "Figure 3-14: Heuristic Threat Indicators / Highlighted keywords UI card"),
    ("Figure_3-15_Model_Server_Configuration.png", "Figure 3-15: Model Server Configuration settings panel"),
    ("Figure_3-16_API_Offline_Fallback.png", "Figure 3-16: API Offline/No Connection fallback screen")
]

print("====================================================")
print("  MINDSHIELD INTERACTIVE SCREENSHOT CAPTURE UTILITY")
print("====================================================")
print(f"Target directory: {screenshot_dir}")
print("For each figure, prepare the screen on your device, then:")
print("  - Press ENTER to capture the screenshot.")
print("  - Type 'skip' and press ENTER to skip that figure.")
print("====================================================\n")

for filename, desc in figures:
    target_path = os.path.join(screenshot_dir, filename)
    print(f"--> Ready to capture: {desc}")
    print(f"    Saving to: {filename}")
    
    # Wait for input
    inp = input("    Press ENTER to capture or type 'skip': ").strip().lower()
    
    if inp == 'skip':
        print(f"    Skipping {filename}\n")
        continue
        
    print("    Capturing...")
    # Capture screenshot on device
    cap_cmd = [adb_path, "shell", "screencap", "-p", "/sdcard/temp_cap.png"]
    subprocess.run(cap_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Pull to host
    pull_cmd = [adb_path, "pull", "/sdcard/temp_cap.png", target_path]
    res = subprocess.run(pull_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if res.returncode == 0 and os.path.exists(target_path):
        print(f"    SUCCESS: Captured and saved to {filename}\n")
        # Clean up temp file on device
        subprocess.run([adb_path, "shell", "rm", "/sdcard/temp_cap.png"])
    else:
        print(f"    ERROR: Failed to capture/pull. Stderr: {res.stderr.decode().strip()}\n")

print("Screenshot capture utility finished.")
