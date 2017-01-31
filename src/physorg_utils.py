
import time
import re

import bs4
from bs4 import BeautifulSoup as bs



def extractPhysOrgParas(soup,
                        para_class = None,
                        wrap_content=False):
    """Extract Paragraphs from a PhysOrg Article Soup

    """
    try:
        content = soup.article
        paras = [para_class(p) \
                 for p in content.findAll('p')]
        return(paras)
    except AttributeError:
        return([])
    
    
def processPhysOrgPara(para,):
    para = para.contents
    para = [p for p in filter(None, para)]
    for p in para:
        if type(p)==bs4.element.NavigableString:
            p = p.strip()
    para = [p for p in filter(None, para)]
    
    content = ''
    phrases = []
    if len(para)==1 and type(para[0])==bs4.element.NavigableString:
        content = para[0].strip()
    elif len(para)==1:
        pass
    elif len(para)>1:
        c = []
        for i,p in enumerate(para):
            if type(p) == bs4.element.NavigableString:
                c.append(p.strip())
            elif type(p) == bs4.element.Tag:
                if p.name in ['p', 'b']:
                    break
                elif p.name=='i':
                    c.append(p.text.strip())
                    phrases.append(p.text.strip().lower())
                elif p.name == 'a':
                    try:
                        if type(para[i-1])==bs4.element.NavigableString and \
                           type(para[i+1])==bs4.element.NavigableString:
                            c.append(p.text.strip())
                            phrases.append(p.text.strip().lower())
                        else:
                            break
                    except IndexError:
                        break

        c = [l.strip() for l in c]
        c = ' '.join(filter(None, c))
        content = c
    return({'content' : content,
            'phrases' : phrases})


def extractPhysOrgLinks(soup):
    """Extract PhysOrg links from PhysOrg Article Soup

    """

    # Define 'links' dictionary
    links = {'Related' : set(),
             'Recommended' : set(),
             'Other' : set(),
            }
    
    # Get links for 'Related Stories' and 'Recommended for you'
    rrs = soup.find_all(attrs={'class':'news-col'})
    for rs in rrs:
        try:
            if re.search('related', rs.find('h2').text.lower()):
                links['Related'].update(set([cleanPhysOrgLink(a['href']) \
                                             for a in rs.find_all('a')]))
            elif re.search('recommended', rs.find('h2').text.lower()):
                links['Recommended'].update(set([cleanPhysOrgLink(a['href']) \
                                                 for a in rs.find_all('a')]))
            else:
                links['Other'].update(set([cleanPhysOrgLink(a['href']) \
                                           for a in rs.find_all('a')]))
        except AttributeError:
            pass
            
    # Get the 'news-box' links
    nb = soup.findAll('article', {'class':'news-box'})
    nb_links = [l for l in filter(physOrgNewsFilter,
                                  [cleanPhysOrgLink(n.find('a')['href']) \
                                   for n in nb])]
    links['Other'].update(set(nb_links))
    
    # Merge for easy use
    links['All'] = links['Related'].copy()
    links['All'].update(links['Recommended'])
    links['All'].update(links['Other'])
    
    return(links)


def extractPhysOrgCategories(soup):
    """
    <ul class="bread-crumbs">
        <li class="bread-crumbs-first" itemscope itemtype="http://data-vocabulary.org/Breadcrumb">
            <a href="https://phys.org/" rel="home" itemprop="url"><span itemprop="title">Home</span></a>
        </li>
        <li itemscope itemtype="http://data-vocabulary.org/Breadcrumb">
            <a href="https://phys.org/science-news/" itemprop="url">
                <span itemprop="title">Other Sciences</span>
            </a>
        </li>
        <li itemscope itemtype="http://data-vocabulary.org/Breadcrumb">
            <a href="https://phys.org/science-news/archaeology-fossils/" itemprop="url">
                <span itemprop="title">Archaeology & Fossils</span>
            </a>            
        </li>
        <li>
            <a href="https://phys.org/archive/09-11-2016/">November 9, 2016</a>
        </li>
    </ul>
    """
    bc = soup.find('ul', {'class' : "bread-crumbs"})
    lis = bc.findAll('li')[:-1]
    return(tuple([li.text.strip() for li in lis]))


def prepHTMLDoc(url, html):

    return({'url' : url,
            'html' : html,
            'Source' : 'PhysOrg',
            'LastUpdate' : time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())})



def physOrgNewsFilter(href):
    """Determine if PhysOrg article or other link instead
    
    """
    return(href.startswith('http://phys.org/news/'))


def cleanPhysOrgLink(link):
    return(re.sub(r'#nRlv$', '', link))


def getURLEnd(url):
    splits = url.split('/')
    content = splits[-1]
    content = content.split('.')[0]
    return(content)

def titleFromURL(url):
    content = getURLEnd(url)
    content = content.split('-')
    name = ' '.join([c.upper() for c in content[2:]])
    return(name)

def dateFromURL(url):
    content = getURLEnd(url)
    content = content.split('-')
    date = '-'.join([c for c in content[:2]])
    return(date)
    
