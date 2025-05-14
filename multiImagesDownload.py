import io
import zipfile
import streamlit as st
import json
import requests

def multiImagesDownload(resultList,n):
    if n==1:
        with st.spinner("Rendering your image.."):
            image_url = json.loads(resultList.model_dump_json())['data'][0]['url']
            st.image(image_url,use_container_width=True)
        with st.spinner("Loading.."):
            response = requests.get(image_url)
        st.sidebar.download_button("Download Image",
        data      = response.content,
        file_name = "generated_image.png",
        mime      = "image/png")
    else:    
        image_urls = []
        responses  = []
        dataList   = []
        cols = st.columns(2)
        for result in resultList:
            image_urls.append(json.loads(result.model_dump_json())['data'][0]['url'])

        for url in image_urls:
           # st.image(url,caption=st.session_state.prompt1)
            responses.append(requests.get(url))
        for i, url in enumerate(image_urls):
            if i > 1:
                i = i-2
            with cols[i]:
                    with st.spinner("Rendering your image.."):
                        st.image(url, use_container_width=True)
        for response in responses:                       
            dataList.append(response.content)


        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for idx, data in enumerate(dataList):
                filename = f"generated_image_{idx + 1}.png"
                zip_file.writestr(filename, data)
        zip_buffer.seek(0)

        st.sidebar.download_button("Download ZIP of images",
            file_name = "generated_images.zip",
            data = zip_buffer,
            mime = "application/zip")
