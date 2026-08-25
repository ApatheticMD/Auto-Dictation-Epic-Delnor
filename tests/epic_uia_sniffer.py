import os
import uiautomation as auto

def extract_elements(element, file_handle, depth=0):
    indent = "  " * depth
    name = element.Name
    control_type = element.ControlTypeName
    auto_id = element.AutomationId
    class_name = element.ClassName
    
    file_handle.write(f"{indent}[{control_type}] Name: '{name}' | ID: '{auto_id}' | Class: '{class_name}' | Depth: '{depth}'\n")
    
    child = element.GetFirstChildControl()
    while child:
        extract_elements(child, file_handle, depth + 1)
        child = child.GetNextSiblingControl()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "epic_elements.txt")
    
    epic_window = auto.WindowControl(searchDepth=1, SubName="Foundation Production")
    
    if not epic_window.Exists(maxSearchSeconds=5):
        print("EERROR: Could not find the Epic application window.")
        return
        
    print(f"INFO: Connected successfully to: {epic_window.Name}")
    print(f"INFO: Extracting UIA elements to: {output_path} ...")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"UIA Target Window: {epic_window.Name}\n")
        f.write("=" * 50 + "\n")
        extract_elements(epic_window, f)
        
    print("INFO: Extraction complete")

if __name__ == "__main__":
    import time
    time.sleep(2)
    main()
