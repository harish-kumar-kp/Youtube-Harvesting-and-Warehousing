import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(page_title = "Youtube Data on Streamlit")
st.header("Query Data", divider='rainbow')
import os
import googleapiclient.discovery
import re
import data_IO 
import mysql.connector 

fileConfig = data_IO.config()
# Python MySQL connection
db = mysql.connector.connect(
    host =fileConfig["key1"],
    user = fileConfig["key2"],
    passwd = fileConfig["key3"],
    database = fileConfig["key4"]
)

mycursor = db.cursor()#cursor creation
sql=""
x=1
querySelected = st.selectbox(
   ":red[**Select your Query**] :point_down: ",
   ("1. What are the names of all the videos and their corresponding channels?", 
    "2. Which channels have the most number of videos, and how many videos do they have?", 
    "3. What are the top 10 most viewed videos and their respective channels?",
    "4. How many comments were made on each video, and what are their corresponding video names?", 
    "5. Which videos have the highest number of likes, and what are their corresponding channel names?", 
    "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
    "7. What is the total number of views for each channel, and what are their corresponding channel names?", 
    "8. What are the names of all the channels that have published videos in the year 2022?", 
    "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
    "10.Which videos have the highest number of comments, and what are their corresponding channel names?",
    "Chart for 3. What are the top 10 most viewed videos and their respective channels?",
    "Chart for 7. What is the total number of views for each channel, and what are their corresponding channel names?",
    "Chart for 9. What is the average duration of all videos in each channel, and what are their corresponding channel names?"),
   placeholder="Select Your Query Here ...",
)

mycursor.execute("Show tables;") 
myresult = mycursor.fetchall()
if len(myresult)==0:
    st.write(":red[No Deta Availabl to Display]")
else:

    if querySelected == "1. What are the names of all the videos and their corresponding channels?":
        x =1
        sql = "SELECT Video.video_name AS Video,Channel.channel_name AS Channel FROM Video INNER JOIN Channel ON Video.video_channelID = Channel.channel_id"
        
    elif querySelected == "2. Which channels have the most number of videos, and how many videos do they have?":
        x = 2
        sql = "SELECT Channel.channel_name AS Channel , COUNT(*) AS Count from Video INNER JOIN Channel ON Video.video_channelID = Channel.channel_id GROUP BY Video.video_channelID ORDER BY COUNT(*) DESC "
        
    elif querySelected == "3. What are the top 10 most viewed videos and their respective channels?":
        x =3
        sql = " SELECT Video.video_name AS Video , Channel.channel_name AS Channel , Video.view_count AS ViewCount FROM Video INNER JOIN Channel ON Video.video_channelID = Channel.channel_id ORDER BY Video.view_count DESC LIMIT 10 "
        
    elif querySelected == "4. How many comments were made on each video, and what are their corresponding video names?":
        x =4
        sql = "SELECT  COUNT(*) AS Count , Video.video_name AS Video FROM Comment INNER JOIN Video ON Comment.video_id = Video.video_id GROUP BY Comment.video_id "
        
    elif querySelected == "5. Which videos have the highest number of likes, and what are their corresponding channel names?":
        x =5
        sql = "SELECT Video.video_name AS Video , Video.like_count AS Likes , Channel.channel_name AS ChannelName FROM Video INNER JOIN Channel ON Video.video_channelID  = Channel.channel_id ORDER BY Video.like_count DESC"
        
    elif querySelected == "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        x =6
        sql = "SELECT Video.video_name AS Video , Video.like_count AS Likes ,Video.dislike_count AS DisLikes_NA_Since2021  FROM Video"
        
    elif querySelected == "7. What is the total number of views for each channel, and what are their corresponding channel names?":
        x =7
        sql = "SELECT Channel.channel_views AS TotalViews , Channel.channel_name AS Channel  FROM Channel"
        
    elif querySelected == "8. What are the names of all the channels that have published videos in the year 2022?":
        x =8
        sql = "SELECT Video.video_name AS Video , Channel.channel_name AS ChannelName FROM Video INNER JOIN Channel ON Video.video_channelID  = Channel.channel_id WHERE year(Video.published_date) = 2022"
        
    elif querySelected == "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        x =9
        sql = "SELECT ROUND(AVG(TIME_TO_SEC(Video.duration))) AS Duration , Channel.channel_name AS ChannelName FROM Video INNER JOIN Channel ON Video.video_channelID  = Channel.channel_id GROUP BY Video.video_channelID"

    elif querySelected == "10.Which videos have the highest number of comments, and what are their corresponding channel names?":
        x=10
        sql = "SELECT   Video.video_name AS Video, COUNT(*) AS CommentCount , Channel.channel_name AS Channel FROM Comment INNER JOIN Video ON Comment.video_id = Video.video_id INNER JOIN Channel ON Video.video_channelID = Channel.channel_id GROUP BY Comment.video_id ORDER BY COUNT(*) DESC"

    elif querySelected =="Chart for 3. What are the top 10 most viewed videos and their respective channels?":
        x=11
        sql = " SELECT Video.video_name AS Video , Channel.channel_name AS Channel , Video.view_count AS ViewCount FROM Video INNER JOIN Channel ON Video.video_channelID = Channel.channel_id ORDER BY Video.view_count DESC LIMIT 10 "

    elif querySelected =="Chart for 7. What is the total number of views for each channel, and what are their corresponding channel names?":
        x=12
        sql = "SELECT Channel.channel_views AS TotalViews , Channel.channel_name AS Channel  FROM Channel"

    elif querySelected =="Chart for 9. What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        x=13
        sql = "SELECT ROUND(AVG(TIME_TO_SEC(Video.duration))) AS Duration , Channel.channel_name AS ChannelName FROM Video INNER JOIN Channel ON Video.video_channelID  = Channel.channel_id GROUP BY Video.video_channelID"


    
mycursor.execute(sql)
myresult = mycursor.fetchall()

if x <11 : 
    df = pd.DataFrame(myresult ,columns = mycursor.column_names )
    st.dataframe(df)
else:
    df = pd.DataFrame(myresult ,columns = mycursor.column_names )
    st.bar_chart(df)

#st.write(x)
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





