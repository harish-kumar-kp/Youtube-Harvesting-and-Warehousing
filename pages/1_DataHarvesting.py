import streamlit as st
st.set_page_config(page_title = "Youtube Data on Streamlit")
st.header("Data Harvesting", divider='rainbow')
import os
import googleapiclient.discovery
import re
import data_IO 
fileConfig = data_IO.config()

api_service_name = "youtube"
api_version = "v3"
apiKey = fileConfig["key5"] #can be changed with own your Values as well
youtube = googleapiclient.discovery.build(api_service_name, 
                                          api_version,
                                          developerKey=apiKey)
def channeDetails(channel_id):
 # This  Function takes the Channel Id and Return the Channel Name,type,ViewCount ,Descripion and status of the channel    
    request = youtube.channels().list(
                                    part="snippet,contentDetails,statistics,status,topicDetails",
                                    id = channel_id)
    response = request.execute()
    chammelTypeLst = []
    for items in (response['items'][0]['topicDetails']['topicCategories']):
        chammelTypeLst.append(items)
        chammelTypeCSV = " , ".join(chammelTypeLst)    
    #"channel_type":response['items'][0]['topicDetails']['topicCategories']
    data = { "channel_id":channel_id,"channel_name": response['items'][0]['snippet']['title'],"channel_type":chammelTypeCSV,"channel_logo":response['items'][0]['snippet']['thumbnails']['medium'] ,
            "channel_viewCnt": response['items'][0]['statistics']['viewCount'],"channesl_dec": str(response['items'][0]['snippet']['description']),"channel_status": str(response['items'][0]['status']['privacyStatus']) }
    return data

intext = str(st.text_input("Please Enter Youtube Channel ID",))
submit = st.button("Check Channel Details")
if submit:    
    if intext=="":
        st.write(":red[*Channel ID Entry is Mandatory*]")
    else:
        intext=intext.strip()
        chDet = channeDetails(intext)
        ChanneName = chDet["channel_name"]
        channel_ID = intext
        ChanneStatus = chDet["channel_status"]
        ChanneViewCount = chDet["channel_viewCnt"]
        st.write(f":orange[*Channel ID* :]  :green[{channel_ID}]")
        st.write(f":orange[*Channel Name* :]  :green[{ChanneName}]")
        
        st.write(f":orange[*Channel Thumbnail* :point_down:] ")
        image_url = chDet['channel_logo']['url']
        st.image(image_url)
        
        st.write(":orange[*Channel Type:*] "+str(chDet['channel_type']))
        
        st.write(f":orange[*Channel ViewCount:*]:green[{ChanneViewCount}]")
        
        st.write(":orange[*About Channel:* ]"+str(chDet["channesl_dec"]) )
        
        st.write(f":orange[*Channel Status:*]   :green[{ChanneStatus}]") 

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

    
    
