import streamlit as st

def main() -> None:
    home_page = st.Page(
        'pages/home.py',
        title='Accueil',
        icon=':material/image_search:',
        default=True)
    
    about_page = st.Page(
        'pages/changelog.py',
        title='Nouveautés',
        icon=':material/diamond_shine:')
    
    pg = st.navigation([home_page, about_page])
    st.set_page_config(page_title="Recherche inversée sur des images d'archive", page_icon=":material/image_search:")
    pg.run()

if __name__ == '__main__':
    main()