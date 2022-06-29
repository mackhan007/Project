import webbrowser
import wikipedia
from googlesearch import search


class Google:
    def __init__(self) -> None:
        pass

    def search_on_wiki(self, data):
        ny = wikipedia.page(data)
        data = ny.content[:500].encode('utf-8')
        response = ''
        response += data.decode()
        return response
    
    def search_on_wiki(self, data):
        pass 
        
    def open_on_tab(self, data):
        url = "https://www.google.com.tr/search?q={}".format(data)
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            self.console(error_log="Error with the execution of skill with message {0}".format(e))
            self.response("Sorry I faced an issue with google search")

g = Google()
g.search_on_wiki("whatsapp")