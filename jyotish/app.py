import pathlib
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout='wide', page_title='Jyotish.ai')

hide_style = '''<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .block-container {padding: 0rem;}</style>'''
st.markdown(hide_style, unsafe_allow_html=True)

current_dir = pathlib.Path(__file__).parent
html_path = current_dir / 'ui' / 'index.html'

if not html_path.exists():
    html_path = current_dir.parent / 'ui' / 'index.html'

if html_path.exists():
    with open(html_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=950, scrolling=True)
else:
    st.error('index.html not found')
