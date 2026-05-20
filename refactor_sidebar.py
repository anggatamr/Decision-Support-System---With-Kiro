import os
import glob

# Fix modules
module_files = glob.glob('modules/*.py')
for f in module_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace st.sidebar with st
    content = content.replace('st.sidebar.', 'st.')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print('Refactored modules.')
