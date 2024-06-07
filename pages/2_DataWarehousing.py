import os
import streamlit as st
import pandas as pd
st.set_page_config(page_title = "Youtube Data on Streamlit")
st.header("DataWarehousing", divider='rainbow')
import data_IO 
fileConfig = data_IO.config()
import googleapiclient.discovery
import re
import mysql.connector 
# Python MySQL connection
db = mysql.connector.connect(
    host =fileConfig["key1"],
    user = fileConfig["key2"],
    passwd = fileConfig["key3"],
    database = fileConfig["key4"]
)

#creating cursor object
mycursor = db.cursor()

api_service_name = "youtube"
api_version = "v3"

apiKey =fileConfig["key5"]
youtube = googleapiclient.discovery.build(api_service_name, 
                                          api_version,
                                          developerKey=apiKey)


def channelData(channel_id):
 # This  Function takes the Channel Id and Return the Channel Name,type,ViewCount ,Descripion and status of the channel    
    request = youtube.channels().list(
                                    part="snippet,contentDetails,statistics,status,topicDetails",
                                    id = channel_id)
    response = request.execute()
    data = { "channel_id": channel_id,"channel_name": response['items'][0]['snippet']['title'],"channel_type":response['items'][0]['topicDetails']['topicCategories'],"channel_viewCnt": response['items'][0]['statistics']['viewCount'],
        "channesl_dec": str(response['items'][0]['snippet']['description']),"channel_status": str(response['items'][0]['status']) }
    return data


def playlistIdDetails(channel_id):
    #This  Function takes the Channel Id and Return the Channel id, Playlist_id and playList names of the channel as a dictionary   with the keys of channel_id , playList_id , playList_Name
    pl_request = youtube.playlists().list(
                                        part="contentDetails,snippet",
                                        channelId=channel_id,
                                        maxResults=50)
    pl_response = pl_request.execute()
    plLstId = []
    plstName = []
    x=0
    for plItem in pl_response['items']:
        plLstId.append(str(plItem['id']))
        plstName.append(str(pl_response['items'][x]['snippet']['title'])) 
        x=x+1
    data = {"channel_id": channel_id,"playList_id":plLstId ,"playList_Name":plstName ,"playListCount" :len(plLstId)}
    return data

def videoIdGen(playLsId):
    # video_details fetching by playlist as input
    vid_request = youtube.playlistItems().list(
                                            part="contentDetails",
                                            playlistId = playLsId , 
                                            maxResults=50)
    vid_response = vid_request.execute()
    VID_data = vid_response
    vid_Lst = []
    vid_count = int(len(VID_data['items']))
    for i in range(0 , vid_count ) :
        vid = VID_data['items'][i]['contentDetails']['videoId']
        if len(vid_Lst) == 0:
                vid_Lst.append(vid)
        else:
            if vid in vid_Lst:
                continue 
            else:   
                vid_Lst.append(vid)
    vidId_CSV = ",".join(vid_Lst)
    data = {"videoID":vidId_CSV , "videoCountThisPL" :vid_count ,"playListID" :playLsId }
    return data

def videoInfo(vid):
    # with video_id as input we can get video details
    vdo_request = youtube.videos().list(
                                        part="contentDetails,snippet,statistics",
                                        id = vid,
                                        maxResults=50)
    vdo_response = vdo_request.execute()
    return vdo_response

def commentDataScrape(vid_ID):
    # This Function takes video id and returns all the comment Data
    com_request = youtube.commentThreads().list( 
                                                part = "snippet", 
                                                videoId = vid_ID ,
                                                maxResults=100)
    com_response = com_request.execute()
    commentIDLst =[] 
    commentTXTLst =[] 
    commentAuthorLst =[]
    commentPublishLst = []
    for item in com_response['items']:
        commentID = item['snippet']['topLevelComment']['etag']
        commentIDLst.append(commentID)
        commentTXT = item['snippet']['topLevelComment']['snippet']['textDisplay']
        commentTXTLst.append(commentTXT)
        commentAuthor = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
        commentAuthorLst.append(commentAuthor)
        commentPublish = item['snippet']['topLevelComment']['snippet']['publishedAt']
        commentPublishLst.append(commentPublish)
    commentData ={"videoID":vid_ID ,"commentID":commentIDLst,"comment_Text":commentTXTLst ,"comment_Author":commentAuthorLst ,"comment_PublishDate":commentPublishLst }
    return commentData

def channelDataBase(channel_id):
    # This Function takes output of channelData() function and process the data which is suitable to store in SQL table "Channel" 
    ch_data = (channelData(channel_id))
    chId = str(ch_data['channel_id'])
    chNam =str(ch_data['channel_name'])
    chTyp = " , ".join(ch_data['channel_type'][0:255])
    chVc = int(ch_data['channel_viewCnt'])
    chDes = str(ch_data['channesl_dec'][0:255])
    chSta = str(ch_data['channel_status'])
    mycursor.execute("CREATE TABLE IF NOT EXISTS Channel (channel_id VARCHAR(255), channel_name VARCHAR(255) ,channel_type VARCHAR(255) ,channel_views INT UNSIGNED,channel_description LONGTEXT ,channel_status VARCHAR(255), PRIMARY KEY(channel_id) )")
    sql = "INSERT INTO Channel (channel_id, channel_name , channel_type, channel_views ,channel_description , channel_status) VALUES (%s, %s ,%s ,%s, %s ,%s)"
    val = (chId , chNam ,chTyp , chVc, chDes,chSta )
    mycursor.execute(sql, val)
    
def duration2Seconds(inputTime):
    # This Function converts the video duration from hours:minutes:seconds format to totally seconds format
    inputTimeString = str(inputTime)
    hours_pattern = re.compile(r'(\d+)H')
    minutes_pattern  = re.compile(r'(\d+)M')
    seconds_pattern  = re.compile(r'(\d+)S')
    hours = hours_pattern.search(inputTimeString)
    minutes = minutes_pattern.search(inputTimeString)
    seconds = seconds_pattern.search(inputTimeString)
    hours = hours.group(1) if hours else 0
    minutes = minutes.group(1) if minutes else 0
    seconds = seconds.group(1) if seconds else 0
    hourTotal = int(hours)*3600
    minuteTotal = int(minutes)*60
    totalSeconds = hourTotal +minuteTotal + int(seconds)
    return totalSeconds

def dateTimeFormat(inputString):
    #This function changes " 2022-01-01T00:02:00Z " time date format to " 2022-01-01 00:02:00 " which is SQL compatible format 
    t1 = inputString [0:10]
    t2 = inputString [12:19]
    t3 =t1+" "+t2
    return t3

def videoDatabase(channel_id):
    #This function takes the channel id as input and takes all the multiple playlist id s  later multiple  video id s at once later multiple coments data utilizing minimum API responses and process them to thiet corossponing SQL Tables
    vidList=[]
    mycursor.execute("CREATE TABLE IF NOT EXISTS Playlist (playList_id VARCHAR(255),Channel_id VARCHAR(255), playList_name VARCHAR(255), PRIMARY KEY(playList_id) )")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Video (video_id VARCHAR(255),playList_id VARCHAR(255), video_name VARCHAR(255),video_channelID VARCHAR(255),video_description TEXT ,published_date DATETIME ,view_count INT ,like_count INT,dislike_count INT ,favourite_count INT,comment_count INT,duration INT,thumb_nail VARCHAR(255),caption_status VARCHAR(255),PRIMARY KEY(video_id) )")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Comment (comment_id VARCHAR(255) , video_id VARCHAR(255) , comment_text TEXT ,comment_autor VARCHAR(255), comment_publish_date DATETIME , PRIMARY KEY(comment_id) )")
    plaList = playlistIdDetails(channel_id)
    for i in range(0,plaList['playListCount']):
        chanId =str(channel_id) 
        playLisId =str(plaList['playList_id'][i])
        playLisName =str(plaList['playList_Name'][i])
        Plsql = "INSERT INTO Playlist (playList_id, Channel_id , playList_name ) VALUES (%s, %s ,%s )"
        Plval = (playLisId , chanId ,playLisName )
        mycursor.execute(Plsql, Plval)
        #vidIds = videoIdGen(playLisId)['videoID']
        vidData = videoInfo(videoIdGen(playLisId)['videoID'])
        vidIdsCoun = len(vidData['items'])
        for i in range (0 , vidIdsCoun):
            vidId = vidData['items'][i]['id']
            if len(vidList) == 0:
                vidList.append(vidId)
            else:
                if vidId in vidList:
                    continue 
                else:   
                    vidList.append(vidId)          
                    vidTitle = vidData['items'][i]['snippet']['title']
                    vidChanId = vidData['items'][i]['snippet']['channelId']
                    vidDesc = vidData['items'][i]['snippet']['description']
                    vidPub = dateTimeFormat(vidData['items'][i]['snippet']['publishedAt'])
                    vidvieCnt =vidData['items'][i]['statistics']['viewCount']
                    vidLike = vidData['items'][i]['statistics']['likeCount']
                    vidDislike = int(0)# this Feature is discarded from youtube since 2021
                    vidFav = vidData['items'][i]['statistics']['favoriteCount']
                    vidCmnt = vidData['items'][i]['statistics']['commentCount']
                    vidDur = duration2Seconds(vidData['items'][i]['contentDetails']['duration'])
                    vidThum = vidData['items'][i]['snippet']['thumbnails']['default']['url']
                    vidCap = vidData['items'][i]['contentDetails']['caption']
                    #print( vidId , vidTitle , vidDesc , vidPub , vidvieCnt , vidLike  , vidDislike , vidFav , vidCmnt , vidDur , vidThum , vidCap, playLisId )
                    Vidsql = "INSERT INTO Video (video_id ,playList_id , video_name ,video_channelID,video_description  ,published_date ,view_count ,like_count ,dislike_count ,favourite_count ,comment_count ,duration ,thumb_nail ,caption_status) VALUES (%s, %s ,%s,%s, %s ,%s,%s, %s ,%s,%s, %s ,%s,%s,%s )"
                    Vidval = (vidId , playLisId ,vidTitle,vidChanId ,vidDesc ,vidPub ,vidvieCnt ,vidLike ,vidDislike ,vidFav , vidCmnt, vidDur, vidThum , vidCap )
                    mycursor.execute(Vidsql, Vidval)
                    
                    cmment=commentDataScrape(vidId)
                    for i in range(0 , int(len(cmment['commentID']))):
                        videId = str(cmment['videoID'] )
                        commentId = str(cmment['commentID'][i])
                        commentTxt = str(cmment['comment_Text'][i])
                        commentAuthor = str(cmment['comment_Author'][i])
                        commentPublishDate = dateTimeFormat(cmment['comment_PublishDate'][i])
                        #print( videoId ,commentId , commentTxt , commentAuthor , commentPublishDate)   
                        cmntsql = "INSERT INTO Comment (comment_id  , video_id , comment_text ,comment_autor , comment_publish_date ) VALUES (%s, %s ,%s,%s ,%s)"
                        cmntval = (commentId , videId ,commentTxt,commentAuthor ,commentPublishDate )
                        mycursor.execute(cmntsql, cmntval)
    vidList.clear()
    status=1
    return status
    

def deleteDataBase():
    # to delete the Tables
    mycursor.execute("DROP TABLE IF EXISTS Channel")
    mycursor.execute("DROP TABLE IF EXISTS Playlist")
    mycursor.execute("DROP TABLE IF EXISTS Video")
    mycursor.execute("DROP TABLE IF EXISTS Comment")

def databaseMatch(inputText):
    #This function initilizes the tabls for Channel data , Video Data and Comment Data and prevents the Double Entry of Chnnel id at user input activity
    mycursor.execute("CREATE TABLE IF NOT EXISTS Channel (channel_id VARCHAR(255), channel_name VARCHAR(255) ,channel_type VARCHAR(255) ,channel_views INT UNSIGNED,channel_description LONGTEXT ,channel_status VARCHAR(255), PRIMARY KEY(channel_id) )")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Video (video_id VARCHAR(255),playList_id VARCHAR(255), video_name VARCHAR(255),video_channelID VARCHAR(255),video_description TEXT ,published_date DATETIME ,view_count INT ,like_count INT,dislike_count INT ,favourite_count INT,comment_count INT,duration INT,thumb_nail VARCHAR(255),caption_status VARCHAR(255),PRIMARY KEY(video_id) )")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Comment (comment_id VARCHAR(255) , video_id VARCHAR(255) , comment_text TEXT ,comment_autor VARCHAR(255), comment_publish_date DATETIME , PRIMARY KEY(comment_id) )")
    sql = "SELECT channel_id FROM Channel"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    inputText=inputText.strip()
    if len(myresult) == 0:
        retVal=1
        print("Chanel ID Successfully Stored")
    else:
        for x in myresult:
            if x[0]==inputText:
                retVal=0
                break
            else:
                retVal=1
    return retVal
errorStatement =""
try:                
    intext = str(st.text_input("Please Enter Youtube Channel ID",))
    submit = st.button("Scrape the Channel Information")
    if submit:
        if intext=="":
            st.write(":red[*Channel ID input cannot be Empty*]")
        else:  
            gate = databaseMatch(intext)
            if gate ==1:
                intext=intext.strip() 
                chStatus=videoDatabase(intext)
                db.commit()
                if chStatus==1:
                    channelDataBase(intext)
                    st.write("Channel Data Stored Succesfully")   
                    st.write("Video Data Stored Succesfully")
                    st.write("Comment Data Stored Succesfully")
                    db.commit()
                    #st.write(chStatus)
                else:
                    errorStatement="Data Integrety Error From The source , Please try this ID after some time"
                    #st.write(chStatus)
            elif gate==0:
                st.write("The Channel ID is Entered Already , Please try next ID")
except: 
        # Prevent the error from propagating into your Streamlit app.
        st.write(errorStatement)
        pass

#view = st.button("View Tables")
#if view:    
   # mycursor.execute("SELECT channel_id, channel_name , channel_views  , channel_status FROM Channel")
    #myresult = mycursor.fetchall()
    #df = pd.DataFrame(myresult ,columns=mycursor.column_names )
    #st.dataframe(df)

#delete = st.button("Deleta all tables")
#if delete:
    #deleteDataBase()

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
