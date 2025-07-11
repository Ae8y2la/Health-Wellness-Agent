import streamlit as st
import speech_recognition as sr
from src.hooks import LifecycleHooks
from src.context import UserSessionContext
from typing import Optional

class VoiceInput:
    """Handles voice input using browser's Web Speech API or fallback to speech_recognition"""
    
    def __init__(self, context: UserSessionContext):
        self.context = context
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def listen_via_browser(self) -> Optional[str]:
        """Use Streamlit's experimental HTML component for Web Speech API"""
        try:
            js_code = """
            const listener = new webkitSpeechRecognition();
            listener.continuous = false;
            listener.interimResults = false;
            
            listener.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                window.parent.postMessage({type: 'speechResult', data: transcript}, '*');
            }
            
            listener.start();
            """
            
            result = st.components.v1.html(
                f"""
                <script>{js_code}</script>
                <div id="speech-result"></div>
                """,
                height=0,
                width=0,
            )
            
            if result and 'data' in result:
                return result['data']
            return None
            
        except Exception as e:
            LifecycleHooks.on_error('VoiceInput', e, self.context)
            return self.fallback_listen()
    
    def fallback_listen(self) -> Optional[str]:
        """Fallback using speech_recognition library"""
        try:
            with self.microphone as source:
                st.info("Speak now...")
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                return text
        except sr.WaitTimeoutError:
            st.warning("Listening timed out")
            return None
        except Exception as e:
            LifecycleHooks.on_error('VoiceInputFallback', e, self.context)
            return None

def voice_input_component(context: UserSessionContext) -> Optional[str]:
    """Streamlit component wrapper for voice input"""
    if st.button("🎤 Voice Input"):
        voice = VoiceInput(context)
        if st.session_state.get('use_browser_speech', True):
            text = voice.listen_via_browser()
        else:
            text = voice.fallback_listen()
        
        if text:
            st.session_state.last_voice_input = text
            return text
    return None
