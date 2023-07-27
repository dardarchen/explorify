import numpy as np
from PIL import Image, ImageDraw
from io import BytesIO
import requests
import streamlit as st
import pandas as pd

class DisplayAPI(object):
    
    def center_crop(self, img):
        width = img.shape[1]
        height = img.shape[0]
        if width > height:
            new_width = height
            left = int(np.ceil((width - new_width) / 2))
            right = width - int(np.floor((width - new_width) / 2))
            center_cropped_img = img[:, left:right, ...]
        else:
            new_height = width
            top = int(np.ceil((height - new_height) / 2))
            bottom = height - int(np.floor((height - new_height) / 2))
            center_cropped_img = img[top:bottom, :, ...]
        return center_cropped_img
    
    def circle_crop_image(self, image_url):
        r = requests.get(image_url)
        img = Image.open(BytesIO(r.content))
        img_arr = self.center_crop(np.array(img))
        dim = img_arr.shape[0]
        lum_img = Image.new('L', [dim,dim] , 0)
        draw = ImageDraw.Draw(lum_img)
        draw.pieslice([(0,0), (dim,dim)], 0, 360, 
                    fill = 255, outline = "white")
        lum_img_arr =np.array(lum_img)
        final_img_arr = np.dstack((img_arr,lum_img_arr))
        return final_img_arr

    def display_auth_url(self, url):
        for _ in range(5):
            st.write(" ")
        st.write(f'''<h1 style="font-size:80px;">
                Explorify  <a style="text-decoration: none;" target="_blank"
                href="{url}"><img src="https://cdn3.emoji.gg/emojis/SpotifyLogo.png" width="65px" height="65px" alt="SpotifyLogo"></a></h1>''',
                    unsafe_allow_html=True)
        st.write("Click the icon to sign in. Happy exploring!")
        st.write('''<p style="font-size:12px; color:#716586">Built by Darren Chen</p>''', unsafe_allow_html=True)
        
    def display_username(self, username):
        for _ in range(2):
            st.write(" ")
        st.header(f"Hi {username}! Here's a summary of your favorite music.")
    
    def display_profile_image(self, profile_image):
        st.write(" ")
        columns = st.columns((3, 1, 3))
        columns[1].image(self.circle_crop_image(profile_image))
        st.write(" ")

    def display_artists(self, data):
        chunks = []
        curr = []
        for i in range(len(data)):
            curr.append(data[i])
            if (i + 1) % 5 == 0:
                chunks.append(curr)
                curr = []
        if curr:
            chunks.append(curr)
        for chunk in chunks:
            columns = st.columns((2, 1, 2, 1, 2, 1, 2, 1, 2))
            for i in range(0, 9, 2):
                col, entry = columns[i], chunk[i // 2]
                name, url, popularity, image, _ = entry
                col.image(self.circle_crop_image(image))
                col.write(f'''<center><h5>
                <a style="color: #ffffff; text-decoration: none;" target="_self"
                href="{url}">{name}</a></h5></center>''',
                    unsafe_allow_html=True)
    
    def display_top_songs(self, data):
        df = pd.DataFrame(columns=["Title", "Artist", "Preview", "Popularity", " ", "Id"], data=data)
        cleaned_df = df[[" ", "Title", "Artist", "Popularity"]]
        cleaned_df.index = [x + 1 for x in cleaned_df.index]
        st.data_editor(
            cleaned_df,
            column_config = {
                " ": st.column_config.ImageColumn(),
            },
            use_container_width=True
        )
    
    def display_recommended_songs(self, data):
        st.write(" ")
        for song in data:
            title, artist, url, popularity, image, _ = song
            columns = st.columns((2, 4, 1, 8, 1, 10, 2))
            imageCol, textCol, audioCol = 1, 3, 5
            columns[imageCol].image(image)

            columns[textCol].write(" ")
            columns[textCol].write(" ")
            columns[textCol].subheader(title)
            columns[textCol].write(artist)

            columns[audioCol].write(" ")
            columns[audioCol].write(" ")
            columns[audioCol].write(" ")
            columns[audioCol].audio(url)



