
from bs4 import BeautifulSoup as bs

from physorg_utils import extractPhysOrgParas, processPhysOrgPara, extractPhysOrgCategories


ALLOWABLE_ARTICLE_ATTRS = ['url', 'title', 'content', 'phrases']
ALLOWABLE_PARA_ATTRS = ['content', 'phrases']

    
    
class articleObject(object):
    """Base Article Class for handling articles from the web

    """
    
    para_extract_method = None
    
    def __init__(self, content_dict):
        self.url = content_dict['url']
        self.soup = bs(content_dict['html'], 'html.parser')
        
        
    def processArticle(self, ):
        """Extract content and any relevant addl info
        """
        self.initMeta()
        self.initParas()
        self.processParas()
        self.mergeParas()
        
        
    def initMeta(self,):
        self.meta = {'title' : self.getTitle(),
                     'url' : self.url}


    def getTitle(self,):
        try:
            self.title = self.soup.title.text
        except AttributeError:
            self.title = ''

    
    def initParas(self, method=None, para_class=None):
        self.paras = method(self.soup,
                            para_class=para_class)
        
        
    def processParas(self,):
        for p in self.paras:
            p.process()
           
        
    def mergeParas(self,):
        phrases = set()
        contents = []
        for p in self.paras:
            if p.content:
                contents.append(p.content)
                phrases.update(p.phrases)
        self.contents = ' '.join(contents)
        self.phrases = phrases
            
            
            
class articleObjectPhysOrg(articleObject):
    """PhysOrg specific version of 'articleObject'

    """
    
    def initMeta(self,):
        self.meta = {'source' : 'PhysOrg',
                     'title' : self.getTitle(),
                     'url' : self.url,
                     'categories' : extractPhysOrgCategories(self.soup)}
    
    def initParas(self, method=extractPhysOrgParas):
        articleObject.initParas(self,
                                method=method,
                                para_class=paragraphObjectPhysOrg)
    

class paragraphObject(object):
    """Base Paragraph Class for handling article sub-sections

    """
    
    
    def __init__(self, soup):
        self.soup = soup

    def __str__(self):
        return(self.content)

    def process(self, method=None):
        if not method:
            out = {'content' : self.soup.text}
        else:
            out = method(self.soup)
        self.assign_attributes(out)
        
    def assign_attributes(self, attrs_dict):
        for k,v in attrs_dict.items():
            if k in ALLOWABLE_PARA_ATTRS:
                self.__setattr__(k, v)
            
            
class paragraphObjectPhysOrg(paragraphObject):
    """PhysOrg specific version of 'paragraphObject'

    """
    
    def process(self):
        paragraphObject.process(self, method=processPhysOrgPara)       
