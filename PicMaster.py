import os
import dotenv
from multiImagesDownload import multiImagesDownload
from openai import AzureOpenAI
import openai
import speech_recognition as SR
import streamlit as st
dotenv.load_dotenv()

api_key   = os.getenv("dalle_api_key")

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT_dalle")
api_version = os.getenv("OPENAI_API_VERSION", "2024-04-01-preview")
if "client" not in st.session_state:
    st.session_state.client=None
if st.session_state.client is None:
    try:
        st.session_state.client = AzureOpenAI(
        azure_endpoint  = endpoint,
        api_version     = "2024-12-01-preview",
        api_key         = api_key
        )
        resp = st.session_state.client.models.list()
    except openai.AuthenticationError as e:
        st.error("Error in authenticating to AI system " + str(e))
       
    except Exception as e:
        st.error("Error in connecting to AI system " + str(e))


if "text_input" not in st.session_state:
    st.session_state.text_input = ""
if "prompt1" not in st.session_state:
    st.session_state.prompt1=""
def inputFromMicrophone():
    recog = SR.Recognizer()
    try:
        with SR.Microphone() as source:
            with st.spinner("Listening..."):
                recog.adjust_for_ambient_noise(source,duration=1)
                audio = recog.listen(source,timeout = None,phrase_time_limit = 20)
  
        st.session_state.prompt1 = recog.recognize_google(audio)
    except AttributeError as e:
        st.error("Could not find PyAudio; check audio hardware installation")
    except SR.UnknownValueError as e:
        st.warning("Coud not understand audio, use textbox instead or try again!")
    except SR.RequestError as e:    
        st.error("Could not get response from Google Speech Recognistion!")
    except:
        st.error("Other errors!")
        
def clear_text():
    st.session_state.prompt1 = st.session_state.text_input
    st.session_state.text_input = ""

result = None
resultList=[]
st.header("Free Image generator!")
st.subheader("Convert your words into beautiful creation, generate images with HD quality in seconds!")
col1,col2=st.columns([5,1])
with col1:
    st.text_input("Please describe your image here:",
            key="text_input",
            placeholder="A beautiful sunset view with birds",
            on_change = clear_text)
with col2:
    st.write("")
    st.write("")
    if st.button("🎤",help = "Click here to speak your image description"): 
        inputFromMicrophone()


  

if st.session_state.prompt1:
    st.write("Your Image description : "+st.session_state.prompt1)
    with st.sidebar:
        st.header("Choose image setting:")
        n = st.number_input("How many images to generate?",min_value=1,max_value=3,)
        style = st.radio("Select the type of generated images:",
                        ["Vivid","Natural"],index=0)
        qlty = st.radio("Select the Quality of generated images:",
                        ["HD","Standard"],index=1)
        size = st.radio("Select size of the image",
                ["1024x1024", "1792x1024", "1024x1792"],
                index=0
                )
        custStyle = st.radio("Custom style of the image",
                ["Standard","Oil Painting - in the style of an oil painting",
                "Sketch - in pencil sketch style",
                "Cyberpunk - in cyberpunk futuristic style",
                "Anime - anime art style",
                "3D Render - 3D digital art style",
                "Vintage - vintage photography style"],
                index=0
                )
    style = style.lower()
    qlty  = qlty.lower()
    if st.button("Generate"):
        if custStyle != "Standard":
            finPrompt=str(st.session_state.prompt1) +" "+custStyle
        else:
            finPrompt=str(st.session_state.prompt1)

        if n == 1:
            with st.spinner("Generating your image, please wait.."):    
                try:     
                    result  = st.session_state.client.images.generate(
                    model   = "dall-e-3",
                    prompt  = finPrompt,
                    n       = n,
                    style   = style,
                    quality = qlty,
                    size    = size
                
                    )
                except openai.BadRequestError as e:
                    st.error("Error occured in generating image "+str(e))
                except openai.AuthenticationError as e:
                    st.error("Error occured in generating image "+str(e))
                except:
                    st.error("Error occured in generating image")
        else:
            with st.spinner("Generating " + str(n) +" images, this may take a while..."):
                for m in range(n):
                    try:                      
                        resultList.append(st.session_state.client.images.generate(
                        model   = "dall-e-3",
                        prompt  = finPrompt,
                        n       = 1,
                        style   = style,
                        quality = qlty,
                        size    = size  
                        ))
                    except openai.BadRequestError as e:
                        st.error("Error occured in generating image "+str(e))
                    except:
                        st.error("Error occured in generating image")
     #   st.session_state.prompt1=""
    #else:
  #      st.error("Please describe your image first!")
if result:
    n=1
    multiImagesDownload(result,n)
 
else:
    if resultList != []:
        multiImagesDownload(resultList,n)
        