class SpeechService:
    @staticmethod
    def speak(text: str):
        return {
            'status': 'ok',
            'message': 'Speech synthesis is not configured in this lightweight environment.',
            'text': text,
        }
