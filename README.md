## YouTube Data Harvesting and Warehousing using YouTube Data API v3

**Introduction**

YouTube Data Harvesting and Warehousing  project is all about developing a user-friendly web application using Streamlit a Python-based library .that utilises the complete potential of Google API to extract valuable information from YouTube channels. The extracted data is then stored to a SQL data warehouse, and made in Streamlit app in a presentable tabular or graphical form .

<br />

**Table of Contents**

1. Tools , Technologies and Skills
2. Installation
3. Utilisation
4. Features
5. Contributing
6. License
7. Contact

<br />

**Key Technologies and Skills**
- Python v3.12
- MySQL 8.0 
- Application Programming Interface (API) of Google 
- Streamlit
- Pandas
- Numpy

<br />

**Installation**

To run this project, you need to install the following packages:
```python
pip installmysql-connector-python
pip install google-api-python-client
pip install pandas
pip install regex
pip install streamlit
```

<br />

**Utilisation**

To use this project, follow these steps:

1. Clone the repository: ```git clone https://github.com/harish-kumar-kp/Youtube-Harvesting-and-Warehousing```
2. Install the required packages and libraries : ```pip install -r requirements.txt```
3. Launch the landingPage with Streamlit and Entering the Youtube channel id on concluding pages: ```streamlit run Home.py```
4. Access the app in your browser at ```http://localhost:8501```

<br />

**Operating Procedure**

 **How to Get API Key:** [https://www.youtube.com/watch?v=brCkpzAD0gc](https://www.youtube.com/watch?v=brCkpzAD0gc)

**Data Harvesting:** With Google API retrieving comprehensive data from YouTube channels by channel id as input. Where the data includes information on channels, playlists, videos, and comments. By interacting with the Google API, we collect the data in Python as a Dictionary .

**Python Dicionary to SQL:** The application allows users to migrate data from Python to a SQL data warehouse. Users can choose which channel's data to migrate. To ensure compatibility with a structured format, the data is cleansed using the powerful pandas library. Following data cleaning, the information is segregated into separate tables, including channels, playlists, videos, and comments, utilizing SQL queries.

**Data Analysis and Visualization:** The project provides comprehensive data analysis capabilities with Streamlit with predfined Queries. With Streamlit the users can create interactively create charts and graphs  from the collected data.

- **Channel Analysis:** Channel analytics on playlists, videos, subscribers, views, likes, comments, and durations , For Better understanding of the channel's performance and audience engagement through detailed visualizations and summaries.

- **Video Analysis:** Video analytics on views, likes, comments, and durations, enabling both an overall channel and specific channel perspectives. Leverage visual representations and metrics to extract valuable insights from individual videos.


🎬 𝗣𝗿𝗼𝗷𝗲𝗰𝘁 𝗗𝗲𝗺𝗼 𝗩𝗶𝗱𝗲𝗼: [https://www.youtube.com/watch?v=HVDnJR51FCM](https://www.youtube.com/watch?v=HVDnJR51FCM)

<br />

**Contributing**

Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please feel free to submit a pull request.

<br />

**License**

This project is licensed under the MIT License. Please review the LICENSE file for more details.

<br />

**Contact**

📧 Email: harishk_kotte@rediffmail.com

🌐 LinkedIn: [https://www.linkedin.com/in/harish-kumar-k-p-67587a262/](https://www.linkedin.com/in/harish-kumar-k-p-67587a262/)

For any further questions or inquiries, feel free to reach out. We are happy to assist you with any queries.

