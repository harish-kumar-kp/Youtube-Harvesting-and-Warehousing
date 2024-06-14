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
    nextPageToken = None
    totPlLstId = []
    totPlstName = []
    while True:   
        pl_request = youtube.playlists().list(
                                            part="contentDetails,snippet",
                                            channelId=channel_id,
                                            maxResults=50,pageToken=nextPageToken)

        pl_response = pl_request.execute()
        plLstId = []
        plstName = []
        for plItem in pl_response['items']:
            plLstId.append(str(plItem['id']))
            plstName.append(str(pl_response['items'][pl_response['items'].index(plItem)]['snippet']['title'])) 
        totPlLstId.extend(plLstId)
        totPlstName.extend(plstName)     
        nextPageToken = pl_response.get('nextPageToken')
        if not nextPageToken:
            break
    data = {"channel_id": channel_id,"playList_id":totPlLstId ,"playList_Name":totPlstName ,"playListCount" :len(totPlLstId)}
    return data

def videoIdGen(playLsId):
    # video_details fetching by playlist as input
    nextPageToken = None
    x=0
    totData = []
    while True:    
        vid_request = youtube.playlistItems().list(
                                                part="contentDetails",
                                                maxResults=50,
                                                playlistId = playLsId , pageToken = nextPageToken)                           
        vid_response = vid_request.execute()
        vid_Lst = []
        for VidPlItem in vid_response['items'] :
            vid = vid_response['items'][vid_response['items'].index(VidPlItem)]['contentDetails']['videoId']
            vid_Lst.append(vid)
            vidId_CSV = ",".join(vid_Lst)
        x+=1
        #print(x)
        data = {"videoID":vidId_CSV ,"playListID" :playLsId , "vid_IDsCount":len(vid_response['items']),"pageIndex":x }
        totData.append(data)
        nextPageToken = vid_response.get('nextPageToken')
        if not nextPageToken:
            break
    return totData

def videoInfo(vid):
    # with video_id as input we can get video details
    vdo_request = youtube.videos().list(
                                        part="contentDetails,snippet,statistics",
                                        id = vid,
                                        maxResults=50)
    vdo_response = vdo_request.execute()
    return vdo_response

def commentDataScrape(video_id):
    # This Function takes video id and returns all the comment Data    
    com_response=youtube.commentThreads().list(
    part='snippet',
    videoId=video_id
    ).execute()
    commentIDLst =[] 
    commentTXTLst =[] 
    commentAuthorLst =[]
    commentPublishLst = []
    # iterate video response
    while com_response:
        # extracting required info
        # from each result object 
        for item in com_response['items']:
            commentID = item['id']
            commentIDLst.append(commentID)
            commentTXT = item['snippet']['topLevelComment']['snippet']['textDisplay']
            commentTXTLst.append(commentTXT)
            commentAuthor = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            commentAuthorLst.append(commentAuthor)
            commentPublish = item['snippet']['topLevelComment']['snippet']['publishedAt']
            commentPublishLst.append(commentPublish)
        commentData ={"videoID":video_id ,"commentID":commentIDLst,"comment_Text":commentTXTLst ,"comment_Author":commentAuthorLst ,"comment_PublishDate":commentPublishLst }
        # Again repeat
        if 'nextPageToken' in com_response:
            com_response = youtube.commentThreads().list(
                    part = 'snippet',
                    videoId = video_id,
                      pageToken = com_response['nextPageToken']
                ).execute()
        else:
            break
    return commentData

def channelDataBase(channel_id):
    # This Function takes output of channelData() function and process the data which is suitable to store in SQL table "Channel" 
    ch_data = (channelData(channel_id))
    try:  
        chId = str(ch_data['channel_id'])
    except:
        chId = "MissingData"

    try:  
        chNam =str(ch_data['channel_name'])
    except:
        chNam = "MissingData"
    try:  
        chTyp = " , ".join(ch_data['channel_type'][0:255])
    except:
        chTyp = "MissingData"
    try:  
        chVc = int(ch_data['channel_viewCnt'])
    except:
        chVc = 0 
    try:  
        chDes = str(ch_data['channesl_dec'][0:255])    
    except:
        chDes = "MissingData"   
    try:  
        chSta = str(ch_data['channel_status'])   
    except:
        chSta = "MissingData"             
    
    
    
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
    comList=[]
    mycursor.execute("CREATE TABLE IF NOT EXISTS Playlist (playList_id VARCHAR(255),Channel_id VARCHAR(255), playList_name VARCHAR(255), PRIMARY KEY(playList_id) )")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Video (video_id VARCHAR(255),playList_id VARCHAR(255), video_name VARCHAR(255),video_channelID VARCHAR(255),video_description TEXT ,published_date DATETIME ,view_count INT ,like_count INT,dislike_count INT ,favourite_count INT,comment_count INT,duration INT,thumb_nail VARCHAR(255),caption_status VARCHAR(255),PRIMARY KEY(video_id) )")
    mycursor.execute("CREATE TABLE IF NOT EXISTS Comment (comment_id VARCHAR(255) , video_id VARCHAR(255) , comment_text TEXT ,comment_autor VARCHAR(255), comment_publish_date DATETIME , PRIMARY KEY(comment_id) )")
    playListDict = playlistIdDetails(channel_id)# multi - UC52UDT2S6tk0-4ImaeOHI1Q single - UCFpL0H8QuHOjDgA_ccObAug
    x=0
    for items in playListDict['playList_id'] :
        playlistID = playListDict['playList_id'][playListDict['playList_id'].index(items)]
        allVidIds = videoIdGen(playlistID)
        for items in allVidIds:
            videoInfoLD = videoInfo(allVidIds[allVidIds.index(items)]['videoID'])
            #vidId = videoInfoLD['items'][0]['id']
            for vidDat in videoInfoLD['items']:
                #print(x , vidDat['id'])
                vidId = vidDat['id']
                if len(vidList) == 0:
                    vidList.append("dummyVideoId")
                else:
                    if vidId in vidList:
                        continue 
                    else: 
                        vidList.append(vidId)
                        try:  
                            vidTitle = vidDat['snippet']['title']
                        except: 
                            vidTitle = "MissingData"
                        try:
                            vidChanId = vidDat['snippet']['channelId']
                        except:   
                            vidChanId = "MissingData"
                        try:
                            vidDesc = vidDat['snippet']['description']
                        except: 
                            vidDesc = "MissingData"
                        try:
                            vidPub = dateTimeFormat(vidDat['snippet']['publishedAt'])
                        except: 
                            vidPub = "MissingData"
                        try:
                            vidvieCnt = vidDat['statistics']['viewCount']
                        except: 
                            vidvieCnt = 0
                        try:
                            vidLike = vidDat['statistics']['likeCount']
                        except: 
                            vidLike = 0
                        vidDislike = int(0)# this Feature is discarded from youtube since 2021
                        try:
                            vidFav = vidDat['statistics']['favoriteCount']
                        except: 
                            vidFav = 0
                        vidCmnt = vidDat['statistics']['commentCount']
                        try:
                            vidCmnt = vidDat['statistics']['commentCount']
                        except: 
                            vidCmnt = 0
                        vidDur = duration2Seconds(vidDat['contentDetails']['duration'])
                        try:
                            vidDur = duration2Seconds(vidDat['contentDetails']['duration'])
                        except: 
                            vidDur = 0
                        try:
                            vidThum = vidDat['snippet']['thumbnails']['default']['url']
                        except: 
                            vidThum = "MissingData"
                        try:
                            vidCap = vidDat['contentDetails']['caption']
                        except: 
                            vidCap = "MissingData"
                        #print( vidId , vidTitle , vidDesc , vidPub , vidvieCnt , vidLike  , vidDislike , vidFav , vidCmnt , vidDur , vidThum , vidCap, vidChanId )
                        Vidsql = "INSERT INTO Video (video_id ,playList_id , video_name ,video_channelID,video_description  ,published_date ,view_count ,like_count ,dislike_count ,favourite_count ,comment_count ,duration ,thumb_nail ,caption_status) VALUES (%s, %s ,%s,%s, %s ,%s,%s, %s ,%s,%s, %s ,%s,%s,%s )"
                        Vidval = (vidId , playlistID ,vidTitle,vidChanId ,vidDesc ,vidPub ,vidvieCnt ,vidLike ,vidDislike ,vidFav , vidCmnt, vidDur, vidThum , vidCap )
                        mycursor.execute(Vidsql, Vidval)
                    
                        cmmentsLD=commentDataScrape(vidId)
                        x=0
                        for item in cmmentsLD['commentID']:
                            commentId = str(cmmentsLD['commentID'][x]) 
                            videId = str(vidId)
                            if len(comList) == 0:
                                comList.append("dummyCommentId")
                            else:
                                if commentId in comList:
                                    continue 
                                else:
                                    comList.append(commentId)
                                    try:
                                        commentId = str(cmmentsLD['commentID'][x]) 
                                    except:
                                        commentId = "MissingData" 
                                    try:
                                        commentTxt = str(cmmentsLD['comment_Text'][cmmentsLD['commentID'].index(item)])
                                    except:    
                                        commentTxt = "MissingData" 
                                    try:      
                                        commentAuthor = str(cmmentsLD['comment_Author'][x])
                                    except:
                                        commentAuthor = "MissingData"
                                    try: 
                                        commentPublishDate = dateTimeFormat(cmmentsLD['comment_PublishDate'][x])
                                    except:
                                        commentPublishDate = "MissingData"
                                    #print(videId, commentId , commentTxt , commentAuthor , commentPublishDate)   
                                    x=x+1
                                    cmntsql = "INSERT INTO Comment (comment_id  , video_id , comment_text ,comment_autor , comment_publish_date ) VALUES (%s, %s ,%s,%s ,%s)"
                                    cmntval = (commentId , videId ,commentTxt,commentAuthor ,commentPublishDate )
                                    mycursor.execute(cmntsql, cmntval)

    vidList.clear()
    comList.clear()
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
                    st.write(chStatus)
            elif gate==0:
                st.write("The Channel ID is Entered Already , Please try next ID")
except: 
        # Prevent the error from propagating into your Streamlit app.
        #st.write(errorStatement)
        st.write("Data Integrety Error From The source , Please try next chnnel ID ")
        Click = st.button("Continue")
        if submit:
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
