import bleach #library buat mencegah XSS (Cross Site Scripting)

class Utility:
    
    @staticmethod
    def deleteDoubleSpace(string):
        if isinstance(string, str):
            return " ".join(string.split()) #ngilangin spasi double
        
    @staticmethod
    def deleteSpace(string):
        if isinstance(string, str):
            return string.strip() #ngilangin spasi

    @staticmethod
    def blockMongoInject(payload): #ngeblocking mongo query
        if isinstance(payload, dict):
            for key, value in payload.items():
                if isinstance(key, str) and key.startswith("$"): #kalo key nya ada $ lgsg error
                    raise ValueError("Illegal MongoDB operator")
                Utility.blockMongoInject(value)
        elif isinstance(payload, list):
            for item in payload:
                Utility.blockMongoInject(item)
    
    @staticmethod
    def sanitizeHTML(value):
        if isinstance(value, str):
            return bleach.clean(value, strip=True)#buat ngilangin script html di input 
        if isinstance(value, list):
            return [Utility.sanitizeHTML(item) for item in value]
        if isinstance(value, dict):
            return {key: Utility.sanitizeHTML(value) for key, value in value.items()}
        return None
    
    