import streamlit as st
st.set_page_config(page_title = "Youtube Data on Streamlit")
st.header("YouTube Data Harvesting and Warehousing using SQL and Streamlit", divider='rainbow')
st.subheader("With Youtube Data API v3", divider='grey')
st.markdown("This tool is created with Python functional code block, MySQL and Streamlit along with pip installation of google-api-python-client, regex, mysql.connector")
st.markdown('<img src="https://www.dropbox.com/scl/fi/q4qn1xd2be69cqgqn99px/youtubeLogo.webp?rlkey=o43qn3112vx8fq12tkvoefada&st=v7bd1f5i&dl=1"/>', unsafe_allow_html=True)
footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Capstone Project by HARISH KUMAR K P  @mail : harishk_kotte@rediffmail.com   - GUVI  Batch : MA27<a style='display: block; text-align: center;</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
