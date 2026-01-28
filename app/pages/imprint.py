import streamlit as st

_, content_column, _ = st.columns([1, 3, 1])
with content_column:
    st.markdown(
        """
        ## Imprint

        **Operator**  
        **SWISDATA gGmbH**

        Media Quarter 3.4 / 5th Floor  
        Maria-Jacobi-Gasse 1  
        A-1030 Vienna  
        Austria

        ---

        **Contact**  
        Email: office@swisdata.eu  
        Phone: +43 680 23 29 65 9

        ---

        **Company Register**  
        Company register number: FN 518362y
        """
    )
