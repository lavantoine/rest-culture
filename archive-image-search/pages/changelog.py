from pathlib import Path
import streamlit as st


CHANGELOG_LINES_TO_SKIP = 6  # header lines
DISPLAY_LATEST = 1  # number or latest versions to display

def show_changelog():
    md_path = Path(__file__).parent.parent / "md" / "changelog.md"
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[CHANGELOG_LINES_TO_SKIP:]

    # lines which contain version numbers only
    version_numbers = [line for line in lines if line.startswith('## [')]
    
    # number of line, which separates displayed entries from hidden ones
    version_idx = lines.index(version_numbers[DISPLAY_LATEST])
    
    # display entries
    st.header('Notes de version')
    st.markdown(''.join(lines[:version_idx]))
    
    # hide others with expander
    with st.expander('Versions précédentes'):
        st.markdown(''.join(lines[version_idx:]))

show_changelog()