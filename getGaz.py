# -*- coding: utf-8 -*-
import re
import urllib
import time
import sys
import urllib2
import os
import pprint

VERSION = '0.9.6'
NAME = u'Контекст PaperDonkey'

class GetGaz (object):
    """Base class for downloading gazet articles
       Provides cleaning methods, writing and other usefull stuff
       New gazet classes can be inherited from this class
       __init__ method must be overrided with gazet specific patterns and constants
       some paper specific tweeking is needed.
       """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize GetGaz object with basic patterns and other stuff
        """

        #patterns
        self.pattern_match_title = re.compile (r'',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'',re.DOTALL) # Автор
        self.pattern_match_news_author = re.compile (r'',re.DOTALL)      # Автор новостей
        self.pattern_match_content = re.compile (r'',re.DOTALL) # Текст статьи
        self.pattern_match_date = re.compile (r'',re.DOTALL) # Date
        self.pattern_match_number = re.compile(r'',re.DOTALL) # Номер Газеты
        self.pattern_match_table = re.compile(r'<table.+?</table>',re.DOTALL)
        #patterns

        self.pattern_match_data_url = re.compile(r'',re.DOTALL)
        self.pattern_match_data_url_URL = re.compile(r'',re.DOTALL)
        self.pattern_match_date_url_news = re.compile(r'',re.DOTALL)

        self.main_URL = r'http://www.blah-blah-blah.com'
        self.work_URL = self.main_URL
        self.divider = '\n\n@\n\n' # Divider betwean articles
        self.small_div = '\n\n'    # Divider near title and author
        self.PATH = r'D:\\'        # Default save to path
        self.filename = 'cp_gazname_' # Name prefix
        self.urls = []# parsed urls ready fo getPaper
        self.data = '' # currently processed data
        self.gazeta = [] # list of processed articles
        self.number = 0 # Gazet number
        self.fullFileName = '' # filename to save gazet
        self.ext = '.txt'
        if not DATE:                        # Date in special format
            self.Date = self.localDate()
        else:
            self.Date = DATE
        self.usrDate = DATE
        self.TestRun = False
        self.PROXIE = PROXIE # Proxie
        self.current_url = ''
        self.markTables = False

        #substitution lists:

        self.title_substitution_pairs = [
            (r'&quot;|&ldquo;|&rdquo;|&raquo;|&laquo;', r'"'),
            (r'<.+?>|&nbsp;', r''),
            (r'&rsquo;|&#39;', r"'"),
            (r'&amp;', r'&'),
            (r' *\r+| *\n+', r' '),
            (r' +', r' '),
            ]
        self.author_substitution_pairs = [
            (r'&quot;', r'"'),
            (r'<.+?>|&nbsp;| *\r+| *\n+', r''),
            (r' +', r' '),
            ]
        self.content_substitution_pairs = [
            (r'\s</p>','\n'),
            (r' +',' '),
            (r'&#12288;', ''),
            (r'<br><br>','\n'),
            (r'</p>','\n'),
            (r'&amp;','&'),
            (r'&rsquo;|&#39;',"'"),
            (r'&quot;|&ldquo;|&rdquo;|&raquo;|&laquo;','"'),
            (r'&mdash;|&ndash;|&middot;','-'),
            (r'&hellip;','...'),
            (r'<.+?>|&nbsp;|&diams;|&shy;',''),
            (r'\t',''),
            (r'\r','\n'),
            (r'\n+','\n'),
            ]

        #ERROR MeSSAGES#
        self.error_messages_dict= {'articles_not_found':u'ОШИБКА: !!! No articles found look into Help for known problems !!! (Статьи не найдены)',
                                   'articles_not_downloaded':u'ОШИБКА: !!! No articles found look into Help for known problems !!! (Что-то вроде найдено но не скачано)',
                                   'article_download_error':u'ОШИБКА: !!! Не удалось скачать статью переходим к следующей в списке !!!',
                                   'connection_error':u'ОШИБКА: !!! Ошибка соединения !!! (Проблема с интернет соединением)',
                                   'write_error':u'ОШИБКА: !!! Ошибка во время записи файла, возможно недостаточно прав (попробуйте сохранить на рабочий стол) !!!',
                                   'get_num_error':u'ОШИБКА: !!! Не удалось получить номер газеты'}
    def raiseError(self, error):
        """raise non critical Error"""
        assert error in self.error_messages_dict #little sanity check
        print self.error_messages_dict.get(error)

    def chgExt(self, ext):
        """ Change extention of file to write
                chgExt(extention)
                returns nothing
        """
        assert ext in ('.txt', '.doc')
        self.ext = ext

    def chgWorkURL(self, url):
        """ change working url
        example: chgWorkURL('http://www.ukurier.gov.ua')"""
        assert 'http' in url
        self.work_URL = url

    def chgOutDir(self, path):
        """ Change output directory, where completed file will be saved"""
        # should be rewritten with os.path
        #if path[-1] != '\\':
            #path += '\\'
        self.PATH = path

    def chgPROXIE(self, proxie):
        """change Proxie server address"""
        self.PROXIE = proxie

    def chgNumber(self, num):
        """Change paper number"""
        self.number = num

    def process (self):
        """
        metafunction making full paper processing
        Processes Gazet urls_list and writes to file"""
        self.getNumber ()
        self.makeName ()
        self.compileUrlsList()
        if not self.urls:
            self.raiseError('articles_not_found')
            return
        self.getPaper ()
        if self.gazeta:
            self.gazeta[-1] = self.gazeta[-1][:-5] # Getting rid of last divider
            self.toFile()
            print '%d articles processed' %len(self.gazeta)
        else:
            self.raiseError('articles_not_downloaded')

    def getPaper (self):
        """Download and process urls from urls list """
        assert self.urls # There are realy some urls to process
        for article_url in self.urls:
            self.data = self.getData (article_url)
            self.current_url = article_url
            print 'Retriving: ', article_url
            if not self.data:
                self.raiseError('article_download_error')
                continue
            self.gazeta.append (self.compileArticle (article_url))

    def getData (self, url):
        """ Download data from url returns string of rawHTML"""
        assert 'http' in url # little sanity check
        request = urllib2.Request(url)
        request.add_header('User-Agent','PaperDonkey/0.4.9')
        if self.PROXIE:
            request.set_proxy(self.PROXIE,"http")
        opener = urllib2.build_opener()
        try:
            usock = opener.open(request)
        except:
            self.raiseError('connection_error')
            return None
        data = usock.read ()
        usock.close
        return data

    def compileArticle (self,url):
        """compileArticle(url)->string

        returns string composed of title, content,
        and author with divider at ste end"""
        title = self.getTitle ()
        author = self.getAuthor ()
        content = self.getContent (url)
        article = ''
        if author:
            if content:
                if content[-len(author):] == author: #Get rid of author duplicity if exist
                    content = content[:(-len(author)-1)]
                content = content.strip()
        if title:
            article = ''.join((title.strip (), self.small_div))
        else: return ' '.join(('\n\n\nTROUBLE at',str (url),' in title +\n',self.divider))
        if content:
            article = ''.join((article, content))
        else: return ' '.join(('\n\n\nTROUBLE at',str (url),' in content +\n',self.divider))
        if author and len(author)>3 and author != '\n' and author != '':
            article = ''.join((article, self.small_div, author, self.divider))
        else: article = ''.join((article, self.divider))
        return article

    def toFile (self):
        """writes processed articles into file
           to destination specified in PATH with
           name specified in fullFileName"""
        print 'Writing to: ', os.path.join (self.PATH,self.fullFileName)
        try:
            f = open (os.path.join (self.PATH,self.fullFileName),'w')
            try:
                for article in self.gazeta:
                    f.write (article)
            finally:
                f.close ()
        except IOError:
            self.raiseError('write_error')

    def getTitle (self):
        """Parses article Title
           returns string containing article's Title or None"""
        title = self.pattern_match_title.findall (self.data)
        if title:
            title = title[0]
            title = title.strip()
            for s1, s2 in self.title_substitution_pairs:
                title = re.sub(s1, s2, title)
            title = title.strip()
            return title
        return None

    def getAuthor (self):
        """Parse Author of Article
        returns string containing author's name(in most cases :)) or None"""
        author = self.pattern_match_author.findall (self.data)
        if author:
            author = author[0]
            for s1, s2 in self.author_substitution_pairs:
                author = re.sub (s1, s2, author)
            author = author.strip('.').strip(',').strip()
            return author
        return None

    def getContent (self, url):
        """Parse article content
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        content = self.pattern_match_content.findall (self.data)
        if content:
            content = content[0]
            for s1, s2 in self.content_substitution_pairs:
                content = re.sub (s1, s2, content)
            content = content.strip()
            return content
        return None

    def checkDate (self):
        """retursn string containing date or None"""
        date = self.pattern_match_date.findall (self.data)
        if date:
            return date[0]
        return None

    def getNumber (self):
        """Gets number of this Gazet assigns it to self.number or
           assigns None"""
        d = self.getData(self.work_URL)
        if d:
            number = self.pattern_match_number.search(d)
            if number:
                self.number = number.group(1)
            else:
                self.number = None
                self.raiseError('get_num_error')

    def localDate(self):
        """Returns curent date in string format"""
        year = str (time.localtime () [0])
        month = str(time.localtime () [1])
        if len (month) < 2:
            month = '0'+month
        day = str(time.localtime () [2])
        return (year,month,day)

    def makeName (self):
        '''Makes name for file and assigns it to fullFIleName '''
        year,month,day = self.Date
        year = str(int(year) - 2000)
        if int(day) < 10:
            day = '0'+ day
        self.fullFileName = ''.join((self.filename, year, month, day, '-', str(self.number), self.ext))

## УРЯДОВЫЙ КУРЬЕР

class getUK(GetGaz):

    """Get articles from Ukurier.gov.ua"""
    def __init__ (self, DATE=None, TEST=False, PROXIE=False):
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<div class="naz_art">(.+?)</div>\s',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<div style="float:right; width:400px; text-align:right; font-style:italic;">(.*?)</div>',re.DOTALL) # Автор
        self.pattern_match_news_author = re.compile (r'<em>(.*?)</em>',re.DOTALL)      # Автор новостей
        self.pattern_match_content = re.compile (r'<div class="krat".*?>(.+?)</p></div>',re.DOTALL) # Текст статьи
        self.pattern_match_date = re.compile (r'<div style="float:left; width:50px;">(\d\d.\d\d.\d\d\d\d)</div>',re.DOTALL)
        self.pattern_match_number = re.compile(r'<div class="vipusk">№ (\d+)',re.DOTALL)
        self.pattern_match_table = re.compile(r'<table.+?</table>',re.DOTALL)
        self.pattern_match_data_url = re.compile(r'<div class="art">(.+?<div class="pereglyad".*?>.+?)</a></div>',re.DOTALL)
        self.pattern_match_data_url_URL = re.compile(r'<div class="pereglyad".*><a href=(.+?)>',re.DOTALL)
        self.pattern_match_date_url_news = re.compile(r'<div.*class="punktirightdate".*?>(\d\d.\d\d.\d\d\d\d)</div>',re.DOTALL)
        #atributes
        self.main_URL = r'http://ukurier.gov.ua/'
        self.work_URL = self.main_URL
        self.filename = 'cp_uk_'
        self.usrDate = DATE
        self.markTables = False

        #substitution pairs update:
        self.author_substitution_pairs.append((r'<.+?>|&nbsp;|\r+|\n+', ''))

    def getAuthor (self):
        """Parse Author"""
        author = self.pattern_match_author.findall (self.data)
        if not author:
            author = self.pattern_match_news_author.findall (self.data)
        if author:
            author = author[0]
            for s1, s2 in self.author_substitution_pairs:
                author = re.sub(s1, s2, author)
            author = author.strip()
            return author
        return None

    def getUrlsToLook (self):
        """compiles list of pages to look for articles UK specific returns list of urls"""
        data = re.search (r'<div  class="punktileft">(.+?)</ul></li></ul>\s',
                            self.getData(self.main_URL),re.DOTALL).group (1)
        urls = re.findall ('<a href=(.+?)>',data)
        return urls

    def parseArtUrlsFromUrl(self,url):
        """returns list of articls urls occuring in specified page"""
        # has to be rewritten someday
        arts = []
        urls = []
        data = self.getData(url)
        arts = self.pattern_match_data_url.findall(data)
        year,month,day = self.Date
        date = '.'.join((day, month, year))
        if self.usrDate:
            date =  self.usrDate
        for art in arts:
            date_match = re.search(date,art)
            if date_match:
                url = self.pattern_match_data_url_URL.findall(art)[0]
                ValidUrl = re.search('articl',url)# ankor for url validation
                if ValidUrl:
                    urls.append(self.main_URL+url)
        return urls

    def parseNewsUrls(self):
        """returns list of news urls"""
        # has to be rewritten someday
        data = self.getData(self.main_URL)
        datas = re.findall('<div class="nnews">(.+?)</p></div>\s*?</div>',data,re.DOTALL)
        year,month,day = self.Date
        date = '.'.join((day, month, year))
        if self.usrDate:
            date =  self.usrDate
        urls = []
        for dat in datas:
            date_match = re.search(date,dat)
            if date_match:
                urls.append(self.main_URL+re.findall('<a href=(.+?)>',dat)[0])
        return urls

    def compileUrlsList (self):
        """assign urls to self.urls of all found urls"""
        print u'Ищем статьи...'
        urls_to_look = self.getUrlsToLook()
        self.urls = []
        for url in urls_to_look:
            self.urls.extend(self.parseArtUrlsFromUrl(''.join((self.main_URL, url))))
        self.urls.extend(self.parseNewsUrls())

    def getContent (self,url):
        """Parse article content overloads GetGaz.getContent
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        content = self.pattern_match_content.findall (self.data)
        if content:
            content = content[0]
            match_pdf = re.search(r'a href="(.+pdf)"',content)
            if match_pdf:
                match_pdf = match_pdf.group(1)
                content = ''.join(("\n\n Full article in PDF sheet here: ", match_pdf))
                return content
            for s1, s2 in self.content_substitution_pairs:
                content = re.sub(s1, s2, content)
            content = content.strip()
            return content
        return None


class getKP (GetGaz):
    """Get KPU"""
    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getKP object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_data = re.compile (r'<div class="state">(.+?)</div>\s*?<noindex>',re.DOTALL)# Полезная часть
        self.pattern_match_title = re.compile (r'<h1>(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<div class="state-autor">\s+(\S+ \S+)\s*&mdash;.+?</div>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div class="state">(.+)</div>\s*?<noindex>',re.DOTALL) # Текст статьи
        self.pattern_match_table = re.compile(r'<table.+?</table>',re.DOTALL)
        #patterns
        self.main_URL = r'http://kp.ua/'
        self.work_URL = self.main_URL
        self.filename = 'cp_kpu_'

    def getContent (self,url):
        """Parse article content, overloads GetGaz.getContent
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        content = self.pattern_match_content.findall (self.data)
        if content:
            content = content[0]
            content = re.sub ('\xc2\xa0','',content) #Get rid of come characters, don't remember what
            content = re.sub (r'<h1>.+?</h1>','',content,re.DOTALL) #Get rid of some duplicity
            mdel = re.search(r'<div class="state-autor">.+?</div>',content,re.DOTALL)#again some duplicity problems
            if mdel:
                mdel = mdel.group()
                content = content.replace(mdel,'')
            if self.markTables:
                content = re.sub(self.pattern_match_table,'\n ТАБЛИЦА \n' + self.current_url,content)
            else:
                content = re.sub(self.pattern_match_table,'',content)
            for s1, s2 in self.content_substitution_pairs:
                content = re.sub (s1, s2, content)
            content = content.strip()
            return content
        return None

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        raw_data = self.getData(self.work_URL)
        big_news_data = re.search(r'<div class="txt">(.+?)<div class="press-center">',raw_data,re.DOTALL)
        data = re.search('<h6>(.+?)<div class="blocknews">',raw_data,re.DOTALL)
        if data:
            data = data.group(1)
            if big_news_data:
                data = ' '.join((big_news_data.group(1),data))
        urls = re.findall('http://kp.ua/daily/\d+/\d+',data)
        filter_urls = []
        for url in urls:
            if url not in filter_urls:
                filter_urls.append(url)
        urls = [url+'/print/' for url in filter_urls]
        print u'Основные статьи найдены, ищем спецпроэкты:'
        data = re.search('<div class="special">(.+?)<div id="c-right">',raw_data,re.DOTALL)
        if data:
            data = data.group(1)
            spec_urls = re.findall('http://kp.ua/daily/\d+/\d+',data)
            print spec_urls
            filter_urls = []
            for url in spec_urls:
                if url not in filter_urls:
                    filter_urls.append(url)
            urls.extend([url+'/print/' for url in filter_urls])
            print u'Список статей составлен приступаем к загрузке...'
        self.urls = urls

    def getNumber (self):
        """Gets number of this Gazet"""
        return '000'


class getRG (GetGaz):
    """get gazet RABGAZ"""
    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getRG object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<a href=.+?class="anons_big"><font class="header_b">(.+?)</font></a>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'Автор: (.+?)\.',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div><p>\s*(.+)</p>',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(r'Выпуск <b>№ (\d+)',re.DOTALL) # Номер Газеты
        self.pattern_match_table = re.compile(r'<table.+?</table>',re.DOTALL)
        self.pattern_match_data_url = re.compile(r'<td class="grey_bott".+?<a href="/(.+?)">',re.DOTALL)
        #atribs
        self.main_URL = r'http://rg.kiev.ua/'
        self.work_URL = r'http://rg.kiev.ua/page1/nomer996/'
        self.filename = 'cp_rabgaz_'

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        data = self.getData(self.work_URL)
        print 'Looking for urls...'
        self.urls = []
        urls = self.pattern_match_data_url.findall(data)
        for url in urls:
            self.urls.append(self.main_URL+url)

class getDAY (GetGaz):
    """GET DAY       """
    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getDAY object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1 class="pname">(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<div class="pauthor">(.+?)</div>',re.DOTALL) # Автор
        self.pattern_match_news_author = re.compile (r'',re.DOTALL)      # Автор новостей
        self.pattern_match_content = re.compile (r'<p class.*?text-content-page1.*?>(.+?)<P.*?class.*?text-content-page2.*?>',re.DOTALL) # Текст статьи
        self.pattern_match_table = re.compile(u'<td>.+?</td>',re.DOTALL)
        self.pattern_match_urls_bloks = re.compile(r'polosa\d+.*?</a>(.+?)colspanmenubottom',re.DOTALL)
        #atribs
        self.main_URL = r'http://www.day.kiev.ua/'
        self.work_URL = r'http://www.day.kiev.ua/ua.2010.141' #self.main_URL
        self.filename = 'cp_day_'

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        data = self.getData(self.work_URL).decode('windows-1251')
        #-------------First aproximation------------------
        match = re.search(ur'<!--Блок баннеров box_1 ФИНИШ -->(.+?)<!--Блок баннеров box_2 НАЧАЛО -->',data,re.DOTALL)
        if match:
            data = match.group(0)
            print 'First aproximation done...'
        else:
            print 'Something wrong with data...'
        #-------------parse blocs------------------
        data_list = re.findall(r'<a href=(.+?)>',data,re.DOTALL)
        url_list = []
        if data_list:
            for item in data_list:
                url_list.append(re.search('\d+',item,re.DOTALL).group())
        #------------clean urls---------------------
        cleaned_url_list = []
        for item in url_list:
            if item not in cleaned_url_list:
                cleaned_url_list.append(item)
        #------------fill url lists-----------------
        for item in cleaned_url_list:
            self.urls.append(self.main_URL + '290619?idsource=' + item +'&mainlang=ukr')# const parameters fo print view from day

    def getNumber (self):
        """Gets number of this Gazet"""
        number = re.search(r'\d+\Z',self.work_URL)
        if number:
            self.number = number.group(0)
        else: self.number = None

    def getAuthor (self):
        """Parse Author"""
        author = self.pattern_match_author.findall (self.data)
        if author:
            author = author[0]
            author = re.sub (r'&quot;','"',author)
            author = re.sub (r'<.+?>|&nbsp;| *\r+| *\n+','',author)
            author = re.sub (r' +',' ',author)
            while author[0]==' ' or author[0]==',' or author[0]=='.':
                author = author[1:]
            while author[-1]==' ' or author[-1]==',' or author[-1]=='.' or author[-1]=='\n' or author[-1]=="""
            """:
                author = author[:-1]
            match = re.search(',',author)
            if match:
                author = re.search(r'\A(.+?),',author).group(1)
            match = re.search(r'\.',author)
            if match:
                author = re.search(r'\A(.+?)\.',author).group(1)
            return author
        return None

    def compileArticle (self,url):
        """compileArticle(url)->string

        returns string composed of title, content,
        and author with divider at ste end"""
        title = self.getTitle ()
        author = self.getAuthor ()
        match = re.search(ur'\AКоротко ',title.decode('windows-1251'))
        if not match:
            content = self.getContent (url)
        else:
            content = self.GetMultipleNews(url)[3:]
            return content + self.divider
        article = ''
        if author:
            if content[-len(author):] == author:
                content = content[:-len(author)]
        if title:
            article = ''.join((title.strip (), self.small_div))
        else: return ' '.join(('\n\n\nTROUBLE at',str (url),' in title +\n',self.divider))
        if content:
            content = content.strip()
            article = ''.join((article, content))
        else: return ' '.join(('\n\n\nTROUBLE at',str (url),' in content +\n',self.divider))
        if author and len(author)>3 and author != '\n' and author != '':
            article = ''.join((article, self.small_div, author, self.divider))
        else: article = ''.join((article, self.divider))
        return article

    def GetMultipleNews (self,url):
        """Parse article content in multiple news articles in DAY"""
        pat = re.compile('<p class.*?title-content-page1.*?>(.+?)<P.*?class.*?text-content-page2.*?>',re.DOTALL)
        content = pat.findall (self.data)

        if content:
            content = content[0]
            content = re.sub (r'\s</p>','\n',content)
            content = re.sub (r' +',' ',content)
            content = re.sub (r'\s</p>','\n',content)
            content = re.sub (r' </p>','\n',content)
            content = re.sub (r'</p>','\n',content)
            content = re.sub (r'&rsquo;|&#39;',"'",content)
            content = re.sub (r'&quot;|&ldquo;|&rdquo;|&raquo;|&laquo;','"',content)
            content = re.sub (r'&amp;','&',content)
            content = re.sub (r'&mdash;|&ndash;|&middot;','-',content)
            content = re.sub (r'&hellip;','...',content)
            content = re.sub (r' *\n+| *\r+','\n',content)
            content = re.sub (r' *\n+','\n',content)
            content = re.sub (r' \n| \r','\n',content)
            content = re.sub (r'\n\n|\r\r','\n',content)
            content = re.sub (r'\t','',content)
            content = re.sub (r'\n+|\r+','\n',content)
            content = re.sub (r' <b>','\n@\n\n',content)
            content = re.sub (r'<b>','\n@\n\n',content)
            content = re.sub (r' </b>','\n',content)
            content = re.sub (r'</b>','\n',content)
            content = re.sub (r'<.+?>|&nbsp;|&diams;|&shy;','',content)
            content = re.sub (r'\n\n\n','\n\n',content)
            content = re.sub (r'\n ','',content)
            content = content.strip()
            return content
        return None

class getWEND (GetGaz):
    """Weekend"""

    def __init__ (self, DATE = False,TEST = False, PROXIE = False):
        """Initialize getWEND object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1>(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile ('<a class="author".*?>(.+?)</a>') # Автор
        self.pattern_match_content = re.compile (r'<p>(.+?)</p><div id="vote">',re.DOTALL) # Текст статьи
        self.pattern_match_content2 = re.compile (r'<p>(.+?)</div><div id="vote">',re.DOTALL) # Текст статьи
        self.pattern_match_content3 = re.compile (r'<p>(.+?)</blockquote><div id="vote">',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(u'<div id="issue">.*?№(\d+)',re.DOTALL) # Номер Газеты
        self.pattern_match_table = re.compile(r'<table.+?</table>',re.DOTALL)
        #atribs
        self.main_URL = r'http://2000.net.ua/'
        self.work_URL = self.main_URL
        self.filename = 'cp_WEEKEND_'
        self.all_arts = False


    def setAllArts(self,state):
        """download all articals or only printed in paper"""
        print state
        self.all_arts = state

    def rightNumber(self):
        """Checks if the number(gazet number) of downloading article is actual"""
        match = self.pattern_match_number.search(self.data.decode('utf'))
        if match:
            number = match.group(1)
            if str(self.number) == number:
                return True
            else:
                return False

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        if self.TestRun:
            self.urls = ['http://2000.net.ua/weekend/gorod-sobytija/sos/68177',
                        'http://2000.net.ua/weekend/kievljane/68200'  ]
            print u'Ищем статьи...'
            return
        print u'Ищем статьи...'
        #in wend all articles are spread over static categories:
        look_up_list = ['http://2000.net.ua/weekend/gorod-sobytija/',
                        'http://2000.net.ua/weekend/gurman/',
                        'http://2000.net.ua/weekend/kievljane/',
                        'http://2000.net.ua/weekend/tv-ekran/',
                        'http://2000.net.ua/weekend/na-razvorote/',
                        'http://2000.net.ua/weekend/chto-gde/',
                        'http://2000.net.ua/weekend/dlja-vas/']
        self.urls = []
        raw_urls = []
        clean_urls = []
        pat = re.compile('</li></ul>(.+?)<div id="pagenav">',re.DOTALL)
        pat_url = re.compile('<a href=(.+?)>',re.DOTALL)
        for look_up_url in look_up_list:
            raw_urls = []
            clean_urls = []
            raw_data = self.getData(look_up_url)
            data = re.findall(pat,raw_data)
            if data:
                raw_data = data[0]
                raw_urls.extend(re.findall(pat_url,raw_data))
                for raw_url in raw_urls:
                    clean_url = re.sub('"','',raw_url)
                    match = re.search(r'http',clean_url)
                    if not match:
                        clean_url = 'http://2000.net.ua' + clean_url
                    if clean_url not in clean_urls:
                        clean_urls.append(clean_url)
            self.urls.extend(clean_urls)

    def getNumber (self):
        """Gets number of this Gazet"""
        return '000'

    def compileArticle (self,url):
        """compileArticle(url)->string

        returns string composed of title, content,
        and author with divider at ste end"""

        title = self.getTitle ()
        author = self.getAuthor ()
        content = self.getContent (url)
        article = ''
        if author and content:
            if content[-len(author):] == author:
                content = content[:-len(author)]
        if title:
            article = ''.join((title.strip (), self.small_div))
        else: return ' '.join(('\n\n\nTROUBLE at',str (url),' in title +\n',self.divider))
        if content:
            content = content.strip()
            article = ''.join((article, content))
        else: return ' '.join(('\n\n\nTROUBLE at',str (url),' in content +\n',self.divider))
        if author and len(author)>3 and author != '\n' and author != '':
            article = ''.join((article, self.small_div, author, self.divider))
        else: article = ''.join((article, self.divider))
        return article

    def getContent (self, url):
        """Parse article content, overloads GetGaz.getContent
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        table_in = False
        content = self.pattern_match_content.findall (self.data)
        if not content:
            content = self.pattern_match_content2.findall (self.data)
            if content:
                print u"\tТабличка или картинка в этой статье"
                table_in = True
            if not content:
                content = self.pattern_match_content3.findall (self.data)
        if content:
            content = content[0]
            content = re.sub (r'\s</p>','\n',content)
            if self.markTables:
                content = re.sub(self.pattern_match_table,u'\n TABLE \n' + self.current_url,content)
            content = re.sub (r' +',' ',content)
            content = re.sub (r'\s</p>','\n',content)
            content = re.sub (r'</p>','\n',content)
            content = re.sub (r'&rsquo;',"'",content)
            content = re.sub (r'&quot;|&ldquo;|&rdquo;|&raquo;|&laquo;','"',content)
            content = re.sub (r'&mdash;|&ndash;','-',content)
            content = re.sub (r'&hellip;','...',content)
            content = re.sub (r' *\n+| *\r+','\n',content)
            content = re.sub (r'<.+?>|&nbsp;|&diams;|&shy;','',content)
            content = re.sub (r' *\n+','\n',content)
            content = re.sub (r' \n| \r','\n',content)
            content = re.sub (r'\n\n|\r\r','\n',content)
            content = re.sub (r'\t','',content)
            content = re.sub (r'\n+|\r+','\n',content)
            content = re.sub (r'_+','',content)
            content = content.strip()
            if table_in:
                content = ''.join((content, '\n\n\n\n\n!!! TABLE OR IMAGE MAY BE HERE look at: ', url, ' !!!\n\n\n'))
            return content
        return None

    def getPaper (self):
        """Get articles and stuck them in list"""
        for article_url in self.urls:
            self.data = self.getData (article_url)
            self.current_url = article_url
            if not self.all_arts:
                if self.rightNumber():
                    print 'Retriving: ', article_url
                    self.gazeta.append (self.compileArticle (article_url))
            if self.all_arts:
                print 'Retriving: ', article_url
                self.gazeta.append (self.compileArticle (article_url))


class get2000 (getWEND):
    """GET 2000"""

    def __init__ (self, DATE = False,TEST = False, PROXIE = False):
        """Initialize getWEND object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False, TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1>(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile ('<a class="author".*?>(.+?)</a>') # Автор
        self.pattern_match_content = re.compile (r'<p>(.+?)</p><div id="vote">',re.DOTALL) # Текст статьи
        self.pattern_match_content2 = re.compile (r'<p>(.+?)</div><div id="vote">',re.DOTALL) # Текст статьи
        self.pattern_match_content3 = re.compile (r'<p>(.+?)</blockquote><div id="vote">',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(u'<div id="issue">.*?№(\d+)',re.DOTALL) # Номер Газеты
        self.pattern_match_table = re.compile(r'<table.+?</table>',re.DOTALL)
        #atribs
        self.main_URL = r'http://2000.net.ua/'
        self.work_URL = self.main_URL
        self.filename = 'cp_2000_'
        self.all_arts = False

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        look_up_list = ['http://2000.net.ua/2000/forum/',
                        'http://2000.net.ua/2000/derzhava/',
                        'http://2000.net.ua/2000/aspekty/',
                        'http://2000.net.ua/2000/svoboda-slova/']
        self.urls = []
        raw_urls = []
        clean_urls = []
        pat = re.compile('</li></ul>(.+?)<div id="pagenav">',re.DOTALL)
        pat_url = re.compile('<a href=(.+?)>',re.DOTALL)
        for look_up_url in look_up_list:
            print '\t  '+ look_up_url,
            raw_urls = []
            clean_urls = []
            raw_data = self.getData(look_up_url)
            data = re.findall(pat,raw_data)
            if data:
                raw_data = data[0]
                raw_urls.extend(re.findall(pat_url,raw_data))
                for raw_url in raw_urls:
                    clean_url = re.sub('"','',raw_url)
                    match = re.search(r'http',clean_url)
                    if not match:
                        clean_url = 'http://2000.net.ua' + clean_url
                    if clean_url not in clean_urls:
                        clean_urls.append(clean_url)
            self.urls.extend(clean_urls)
            print ''.join((' : ', str(len(clean_urls)), ' articles found'))


class getFacts (GetGaz):
    """GET Facts      """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getFacts object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1 class="article">(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<p class="author">(.*?)</p>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div id="textContent">(.+?)</div>',re.DOTALL) # Текст статьи
        self.pattern_match_content2 = re.compile (r'<h2>(.+?)</h2>',re.DOTALL) # Текст статьи
        #atribs
        self.main_URL = r'http://www.facts.kiev.ua'
        self.work_URL = r'http://www.facts.kiev.ua/archive/2010-08-18/' #self.main_URL
        self.filename = 'cp_facts_'

    def getAuthor (self):
        """Parse Author of Article
        returns string containing author's name(in most cases :)) or None"""
        author = self.pattern_match_author.findall (self.data)
        if author:
            try:
                author = author[0]
            except:
                return None
            author = re.sub (r'&quot;','"',author)
            author = re.sub (r'<.+?>|&nbsp;| *\r+| *\n+','',author)
            author = re.sub (r' +',' ',author)
            try:
                author[0]
            except:
                return None
            author = author.strip('.').strip(',').strip() #Getting rid of garbage
            match = re.search('"',author)
            if match:
                author = re.search(r'\A(.+?)"',author).group(1)
            match = re.search(r'\.',author)
            if match:
                return None
            #Get rid of some special words
            author = re.sub (ur'\xd0\x9f\xd0\xbe\xd0\xb4\xd0\xb3\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2\xd0\xb8\xd0\xbb ','',author)
            author = re.sub (ur'\xd0\x9f\xd0\xbe\xd0\xb4\xd0\xb3\xd0\xbe\xd1\x82\xd0\xbe\xd0\xb2\xd0\xb8\xd0\xbb\xd0\xb0 ','',author)
            author = re.sub (ur' \xd1\x81\xd0\xbf\xd0\xb5\xd1\x86\xd0\xb8\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd0\xbe \xd0\xb4\xd0\xbb\xd1\x8f ','',author)
            return author
        return None

    def getContent (self,url):
        """Parse article content overloads GetGaz.getContent
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        content = self.pattern_match_content.findall (self.data)
        contentSubTitle = self.pattern_match_content2.findall (self.data)
        if content:
            content = content[0]
            if contentSubTitle:
                content = contentSubTitle[0] + content
            content = re.sub (r'\s</p>','\n',content)
            if self.markTables:
                content = re.sub(self.pattern_match_table,u'\n TABLE \n' + self.current_url,content)
            content = re.sub (r' +',' ',content)
            content = re.sub (r'\s</p>','\n',content)
            content = re.sub (r'</p>','\n',content)
            content = re.sub (r'&amp;','&',content)
            content = re.sub (r'&rsquo;|&#39;',"'",content)
            content = re.sub (r'&quot;|&ldquo;|&rdquo;|&raquo;|&laquo;','"',content)
            content = re.sub (r'&mdash;|&ndash;|&middot;','-',content)
            content = re.sub (r'&hellip;','...',content)
            content = re.sub (r' *\n+| *\r+','\n',content)
            content = re.sub (r'<.+?>|&nbsp;|&diams;|&shy;','',content)
            content = re.sub (r' *\n+','\n',content)
            content = re.sub (r' \n| \r','\n',content)
            content = re.sub (r'\n\n|\r\r','\n',content)
            content = re.sub (r'\t','',content)
            content = re.sub (r'\n+|\r+','\n',content)
            content = content.strip()
            return content
        return None

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        if self.TestRun:
            self.urls = ['http://www.facts.kiev.ua/archive/2010-08-18/108743/index.html',
                         'http://www.facts.kiev.ua/archive/2010-08-18/108739/index.html',
                         'http://www.facts.kiev.ua/archive/2010-08-18/108728/index.html',]
            print u'Ищем статьи...'
            return
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
#-------------First aproximation------------------
        match = re.search(r'<div class="categoriesItem" >(.+?)<div id=.*?bottomContainer.*?>',data,re.DOTALL)
        if match:
            data = match.group(0)
            print 'First aproximation done...'
        else:
            print 'Something wrong with data...'
        url_list = re.findall(r'<a href=(.+?)>',data,re.DOTALL)
#------------clean urls---------------------
        cleaned_url_list = []
        cleaned_url_list = [self.main_URL + url for url in url_list]
        cleaned_url_list = [re.sub('"','',url) for url in cleaned_url_list]
        for url in cleaned_url_list:
            if url not in self.urls:
                self.urls.append(url)

    def getNumber (self):
        """Gets number of this Gazet"""
        self.number = '000'


class getZN (GetGaz):
    """GET ZN      """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getZN object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1>(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<div class="by">(.*?)</div>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div id="text">(.+?)<ul class="meta-actions"  id="bottomsubmenu">',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(r' \xb9 (\d+)',re.DOTALL)
        #atribs
        self.main_URL = r'http://www.zn.ua'
        self.work_URL = self.main_URL
        self.filename = 'cp_zn_'

    def getAuthor (self):
        """Parse Author of Article
        returns string containing author's name(in most cases :)) or None"""
        author = self.pattern_match_author.findall (self.data)
        if author:
            try:
                author = author[0]
            except:
                return None
            author = re.sub (r'\xc0\xe2\xf2\xee\xf0: |\xc0\xe2\xf2\xee\xf0\xfb: ','',author)
            author = re.sub (r'&quot;','"',author)
            author = re.sub (r'\(.+\)','',author)
            author = re.sub (r'<.+?>|&nbsp;| *\r+| *\n+|\t+','',author)
            author = re.sub (r' +',' ',author)
            try:
                author[0]
            except:
                return None
            if len(author) == 1:
                return None
            author = author.strip('.').strip(',').strip() #Getting rid of garbage
            return author
        return None

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        if self.TestRun:
            self.urls = ['http://www.zn.ua/1000/1550/70205/']
            print u'Ищем статьи...'
            return
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
#-------------First aproximation------------------
        match = re.search(r'<div class="wrap-categs">(.+?)<!-- END #wrap-categs -->',data,re.DOTALL)
        if match:
            data = match.group(0)
            print 'First aproximation done...'
        else:
            print 'Something wrong with data...'
        url_list = re.findall(r'<a href=(.+?)>',data,re.DOTALL)
#------------clean urls---------------------
        cleaned_url_list = []
        cleaned_url_list = [self.main_URL + url for url in url_list]
        cleaned_url_list = [re.sub('"','',url) for url in cleaned_url_list]
        cleaned_url_list = [''.join((url,'?printpreview')) for url in cleaned_url_list]
        for url in cleaned_url_list:
            if url not in self.urls:
                self.urls.append(url)

    def getNumber (self):
        """Gets number of this Gazet"""
        d = self.getData(self.work_URL)
        number = self.pattern_match_number.search(d)
        if number:
            self.number = number.group(1)
        else: self.number = None


class getKPR (GetGaz):
    """GET KPR      """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getKPR object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1>(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<div class="article_author">.*?<h4>(.+?)</h4>.*?</div>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div class="article_content">(.+?)<div class="article_author">',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(ur'\xb9 (\d+)',re.DOTALL)
        self.main_URL = r'http://www.kiev-pravda.kiev.ua'
        self.work_URL = self.main_URL
        self.filename = 'cp_kpr_'

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        if self.TestRun:
            self.urls = ['http://www.kiev-pravda.kiev.ua/index.php?article=3933&PHPSESSID=3ff637b17e1a7ee6c71479df20dc7655']
            print u'Ищем статьи...'
            return
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
#-------------First aproximation------------------
        match = re.search(r'<!--Main content-->(.+?)<!--Right content-->',data,re.DOTALL)
        if match:
            data = match.group(0)
            print 'First aproximation done...'
        else:
            print 'Something wrong with data...'
        url_list = re.findall(r'<a href=(.+?)>',data,re.DOTALL)
#------------clean urls---------------------
        cleaned_url_list = []
        cleaned_url_list = [self.main_URL + url for url in url_list]
        cleaned_url_list = [re.sub('"','',url) for url in cleaned_url_list]
        for url in cleaned_url_list:
            if url not in self.urls:
                self.urls.append(url)

    def getNumber (self):
        """Gets number of this Gazet"""
        d = self.getData(self.work_URL)
        number = self.pattern_match_number.search(d)
        if number:
            self.number = number.group(1)
        else: self.number = None


class getTov (GetGaz):
    """GET Tov      """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getTov object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1>(.+?)&nbsp;<b class="date">',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<b class=bnews>(\S+ \S+)</b>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<p align="justify">(.+)') # Текст статьи
        self.pattern_match_number = re.compile(r'\xd1\xe2\xb3\xe6\xe8\xe9 \xed\xee\xec\xe5\xf0 (\d+)',re.DOTALL)
        #atribs
        self.main_URL = r'http://www.tovarish.com.ua/fresh/'
        self.work_URL = self.main_URL
        self.filename = 'cp_tov_'

    def getNumber (self):
        """Gets number of this Gazet"""
        d = self.getData(self.work_URL)
        number = self.pattern_match_number.search(d)
        if number:
            self.number = number.group(1)
        else: self.number = None

    def getAuthor (self):
        """Parse Author of Article
        returns string containing author's name(in most cases :)) or None"""
        authors = self.pattern_match_author.findall (self.data)

        def find_author(author):
            if '<' in author:
                return False
            if 'nbsp' in author:
                return False
            if 'class' in author:
                return False
            if '\xd0\xdf\xc4\xca\xce\xcc'in author:
                return False
            if '\xd0\xc5\xc4\xc0\xca\xd6\xb2\xaf'in author:
                return False
            return True

        for author in authors:
            if find_author(author):
                return author
        return None

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        if self.TestRun:
            self.urls = ['http://www.kiev-pravda.kiev.ua/index.php?article=3933&PHPSESSID=3ff637b17e1a7ee6c71479df20dc7655']
            print u'Ищем статьи...'
            return
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
        urls_to_look = ['',]
        urls_to_look.extend(re.findall('<a href=".+/fresh(.+?)"',data))
        urls_to_look = [url for url in urls_to_look if not re.search('\.html',url)]
        urls = []
        for url_to_look in urls_to_look:
            print self.main_URL + url_to_look
            urls.extend(re.findall('<a href="(.+?\.html)"',self.getData(self.main_URL + url_to_look)))
        urls = [url for url in urls if not re.search('/',url)]
        self.urls = ['http://www.tovarish.com.ua/print/'+url for url in urls]


class getCN (GetGaz):
    """GET CN      """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getCN object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<div class=title>(.+?)</div>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<div class=author>(.*?)</div>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div class=article>(.+?)<tr><td><img src=/images/p.gif',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(r'class=number>.+?(\d+)',re.DOTALL)
        #atribs
        self.main_URL = r'http://www.cn.com.ua'
        self.work_URL = self.main_URL
        self.filename = 'cp_stnew_'

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
        urls = []
        urls.extend(re.findall('<a href=(.+?\.html) ',data))
        clean_urls = []
        for url in urls:
            if url not in clean_urls:
                clean_urls.append(url)
        self.urls = [''.join((self.main_URL, url)) for url in clean_urls]

    def getContent (self,url):
        """Parse article content
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        content = self.pattern_match_content.findall (self.data)
        if content:
            content = content[0]
            content = re.sub (r'\s</p>','\n',content)
            if self.markTables:
                content = re.sub(self.pattern_match_table,u'\n TABLE \n' + self.current_url,content)
            content = re.sub (r' +',' ',content)
            content = re.sub (r'\s</p>','\n',content)
            content = re.sub (r'<br><br>','\n',content)
            content = re.sub (r'</p>','\n',content)
            content = re.sub (r'&amp;','&',content)
            content = re.sub (r'&rsquo;|&#39;',"'",content)
            content = re.sub (r'&#160;',' ',content)
            content = re.sub (r'\x97','-',content)
            content = re.sub (r'&quot;|&ldquo;|&rdquo;|&raquo;|&laquo;','"',content)
            content = re.sub (r'&mdash;|&ndash;|&middot;','-',content)
            content = re.sub (r'&hellip;','...',content)
            content = re.sub (r' *\n+| *\r+','\n',content)
            content = re.sub (r'<.+?>|&nbsp;|&diams;|&shy;','',content)
            content = re.sub (r' *\n+','\n',content)
            content = re.sub (r' \n| \r','\n',content)
            content = re.sub (r'\n\n|\r\r','\n',content)
            content = re.sub (r'\t','',content)
            content = re.sub (r'\n+|\r+','\n',content)
            content = content.strip()
            return content
        return None


class getUMOL (GetGaz):
    """GET UMOL      """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getUMOL object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<span class=zag>(.+?)</span>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<span class=a>(.*?)</span>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<SPAN lang=[U|R][K|U]>(.+?)</SPAN>',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(r'class="date">.+?(\d+)',re.DOTALL)
        self.pattern_match_content2 = re.compile (r'<span class="zag">(.+?)</span>',re.DOTALL) # Подзаголовок статьи
        #atribs
        self.main_URL = r'http://www.umoloda.kiev.ua'
        self.work_URL = self.main_URL
        self.filename = 'cp_umol_'

        self.content_substitution_pairs.append((r'i','\xb3'))
        self.content_substitution_pairs.append((r'&#12288;|&#8239',''))

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
        #first aproximation:
        data = re.findall('class=plashr_a>(.+?)</tr>\s+?</table>',data, re.DOTALL)[0]
        urls_to_look = [''.join((self.main_URL, url)) for url in re.findall('<A href=(.+?) class=menu>',data)]
        urls = []
        for url_to_look in urls_to_look:
            data = self.getData(url_to_look)
            data = re.findall('<!-- Begin Center Part -->(.+?)<script language=javascript>', data, re.DOTALL)[0]
            urls.extend(re.findall('<a href=(.+?) class=zag>', data))
        clean_urls = []
        for url in urls:
            if url not in clean_urls:
                clean_urls.append(url)
        self.urls = [''.join((self.main_URL, url)) for url in clean_urls]

    def getContent (self,url):
        """Parse article content
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        small_content = self.pattern_match_content2.findall(self.data)
        content = self.pattern_match_content.findall (self.data)
        if content:
            content = '\n'.join(content)
            if small_content:
                content = '\n'.join((small_content[0], content))
            for s1, s2 in self.content_substitution_pairs:
                content = re.sub(s1, s2, content)
            content = content.strip()
            return content
        return None

class getCV (GetGaz):
    """get gazet CILCKI BICTI"""
    def __init__ (self, DATE = False,TEST = False, PROXIE = False):
        """Initialize getCV object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<p class=ZAGOL30>(.+?)</p>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<p class=AVPOSADA>(.+?)</p>',re.DOTALL) # Автор
        self.pattern_match_news_author = re.compile (r'',re.DOTALL)      # Автор новостей
        self.pattern_match_content = re.compile  (r'<p class=VRIZ>(.+?)</p></td>',re.DOTALL) # Текст статьи
        self.pattern_match_content2 = re.compile (r'<p class=TEXT>(.+?)</p> </td>',re.DOTALL) # Текст статьи2
        self.pattern_match_content3 = re.compile (r'<p class=VRIZ>(.+?)</b></p></td>',re.DOTALL)
        self.pattern_match_date = re.compile (r'',re.DOTALL) # Date
        self.pattern_match_number = re.compile(r'<span style="font-size:14pt;">.+?(\d+)',re.DOTALL) # Номер Газеты
        self.pattern_match_table = re.compile(r'<table.+?</table>',re.DOTALL)
        self.pattern_match_data_url = re.compile(r'',re.DOTALL)
        #atribs
        self.main_URL = r'http://www.silskivisti.kiev.ua/'
        self.work_URL = self.main_URL
        self.filename = 'cp_cv_'

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
        #first aproximation:
        data = re.findall(u'\u041a\u043e\u043b\u043e\u043d\u043a\u0430 2(.+?)\u043e\u043b\u043e\u043d\u043a\u0430 3',data, re.DOTALL)[0]
        urls = [re.sub('index','print',url) for url in re.findall('<a href="(.+?)"',data)]
        clean_urls = []
        for url in urls:
            if url not in clean_urls:
                clean_urls.append(url)
        self.urls = [''.join((self.work_URL, url)) for url in clean_urls]

    def getContent (self,url):
        """Parse article content, overloads GetGaz.getContent
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        content = self.pattern_match_content.findall (self.data)
        if not content:
            content = self.pattern_match_content2.findall (self.data)
        if not content:
            content = self.pattern_match_content3.findall (self.data)
        if content:
            content = content[0]
            for s1, s2 in self.content_substitution_pairs:
                content = re.sub (s1, s2 ,content)
            content = content.strip()
            return content
        return None

    def getData (self, url):
        """ Download data from url returns string of rawHTML"""
        assert 'http' in url # little sanity check
        request = urllib2.Request(url)
        request.add_header('User-Agent','PaperDonkey/0.4.9')
        if self.PROXIE:
            request.set_proxy(self.PROXIE,"http")
        opener = urllib2.build_opener()
        try:
            usock = opener.open(request)
        except:
            self.raiseError('connection_error')
            return None
        data = usock.read ()
        usock.close
        data =  data.decode('koi8_u')
        data = re.sub(u'\u255a','"',data)
        data = re.sub(u'\u2569','"',data)
        data = re.sub(u'\u2593',"'",data)
        data = re.sub(u'\u2248',"-",data)
        data = re.sub(u'\u221a',"-",data)
        data = re.sub(u'\u2550'," ",data)
        data = re.sub(u'\u2518',"...",data)
        data = re.sub(u'\u2567',u"№",data)
        data = re.sub(u'\r\n'," ",data)
        return data

    def toFile (self):
        """writes processed articles into file
           to destination specified in PATH with
           name specified in fullFileName"""
           #Need to be rewriten with os.path
        print 'Writing to: ', os.path.join (self.PATH,self.fullFileName)
        try:
            f = open (os.path.join (self.PATH,self.fullFileName),'w')
            try:
                for article in self.gazeta:
                    f.write (article.encode('utf-8'))
            finally:
                f.close ()
        except IOError:
            self.raiseError('write_error')

    def getZarubezh(self):
        #first approximation
        print u'Retriving: ЗАРУБЕЖ'
        data = self.getData(self.work_URL)
        data = re.findall(u'\u043e\u043b\u043e\u043d\u043a\u0430 1(.+?)\u043e\u043b\u043e\u043d\u043a\u0430 2',data, re.DOTALL)[0]
        small_arts_list = re.findall(r'<a href=.+?</p></span>',data,re.DOTALL)
        small_arts_list = [re.sub('</h6>', 'SMALL_DIVIDER', art) for art in small_arts_list]
        small_arts_list = [re.sub(u'\u0414\u043e\u043a\u043b\u0430\u0434\u043d\u0456\u0448\u0435...', '', art) for art in small_arts_list]
        clean_arts_list = []
        for art in small_arts_list:
            content = art
            content = re.sub (r'\n+|\r+','',content)
            content = re.sub (r'\s</p>','\n',content)
            content = re.sub (r'</p>','\n',content)
            content = re.sub (r'&quot;','"',content)
            content = re.sub (r' *\n+| *\r+','\n',content)
            content = re.sub (r'<.+?>|&nbsp;','',content)
            content = re.sub (r' *\n+','\n',content)
            content = re.sub (r' +',' ',content)
            content = re.sub (r' \n| \r','\n',content)
            content = re.sub (r'\n\n|\r\r','\n',content)
            content = re.sub (r'SMALL_DIVIDER', self.small_div, content)
            content = content.strip()
            content = ''.join((content, self.divider))
            clean_arts_list.append(content)
        self.gazeta.extend(clean_arts_list)
        pass

    def getInformags(self):
        #first approximation
        print u'Retriving: ИНФОРМАГЕНСТВА'
        data = self.getData(self.work_URL)
        data = re.findall(u'\u043e\u043b\u043e\u043d\u043a\u0430 3(.+?)<hr width=80% noshade />',data, re.DOTALL)[0]
        small_arts_list = re.findall(r'<a href=.+?</p></span>',data,re.DOTALL)
        small_arts_list = [re.sub('</h6> ', 'SMALL_DIVIDER', art) for art in small_arts_list]
        small_arts_list = [re.sub(u'\u0427\u0438\u0442\u0430\u0442\u0438', '', art) for art in small_arts_list]
        clean_arts_list = []
        for art in small_arts_list:
            content = art
            content = re.sub (r'\n+|\r+','',content)
            content = re.sub (r'\s</p>','\n',content)
            content = re.sub (r'</p>','\n',content)
            content = re.sub (r'&quot;','"',content)
            content = re.sub (r' *\n+| *\r+','\n',content)
            content = re.sub (r'<.+?>|&nbsp;','',content)
            content = re.sub (r' *\n+','\n',content)
            content = re.sub (r' +',' ',content)
            content = re.sub (r' \n| \r','\n',content)
            content = re.sub (r'\n\n|\r\r','\n',content)
            content = re.sub (r'SMALL_DIVIDER', self.small_div, content)
            content = content.strip()
            content = ''.join((content, self.divider))
            clean_arts_list.append(content)
        self.gazeta.extend(clean_arts_list)

    def process (self):
        """
        metafunction making full paper processing
        Processes Gazet urls_list and writes to file"""
        self.getNumber ()
        self.makeName ()
        self.compileUrlsList()
        if not self.urls:
            self.raiseError('articles_not_found')
            return
        self.getPaper ()
        self.getZarubezh()
        self.getInformags()
        if self.gazeta:
            self.gazeta[-1] = self.gazeta[-1][:-5] # Getting rid of last divider
            self.toFile()
            print '%d articles processed' %len(self.gazeta)
        else:
            self.raiseError('articles_not_downloaded')


class getGOLOS (GetGaz):
    """GET GOLOS      """
    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getgOLOS object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<span.+?class="ArticleTitleOnMainPage".+?>(.+?)</span>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<span id="FormView2_AutorLabel".+?>(.*?)</span>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<td class="ArticleTextOnMainPage".+?>(.+?)</td>',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(r'<span id="ctl00_FormView1_CurrentNumLabel">(\d+)',re.DOTALL)
        #atribs
        self.main_URL = r'http://www.golos.com.ua'
        self.work_URL = self.main_URL
        self.filename = 'cp_golukr_'
        self.cookie = 'ASP.NET_SessionId=hchvof55gwsia5neohth00jw; b=b; golosua=A8D1AF73F8E29B35E799539940F6CC17B12BAAB17B1D9FD76F6B2AB1306529EFEA31D54F18262A6604FA60028EB8F723C0BFAF0F8CBF622499E637E8A1D561A827ADA554DBC47B3B1E6756A3944AE7D2'
        #ASP.NET_SessionId=hchvof55gwsia5neohth00jw; b=b; golosua=A8D1AF73F8E29B35E799539940F6CC17B12BAAB17B1D9FD76F6B2AB1306529EFEA31D54F18262A6604FA60028EB8F723C0BFAF0F8CBF622499E637E8A1D561A827ADA554DBC47B3B1E6756A3944AE7D2

    def chgCookie(self, cookie):
        self.cookie = cookie

    def getData(self, url):
        """ Download data from url returns string of rawHTML"""
        assert 'http' in url # little sanity check
        cookie = self.cookie
        debug_list = []
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.1.9) Gecko/20100315 Firefox/3.5.9 WebMoney Advisor',
                   'Host' : 'golos.com.ua',
                   'Referer' : 'http://www.golos.com.ua',
                   'Connection' : 'close',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache',
                   'Cookie':cookie}
        request = urllib2.Request(url, None,  headers = headers)
        if self.PROXIE:
            request.set_proxy(self.PROXIE,"http")
        try:
            conn = urllib2.urlopen(request)
        except:
            self.raiseError('connection_error')
            return None
        data = conn.read()
        return data

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
        #first aproximation:
        data = re.findall('<span id="ctl00_Label3">(.+?)<span id="ctl00_Label22" style="color:Silver;font-size:8pt;">',data, re.DOTALL)[0]
        #urls = [re.sub('index','print',url) for url in re.findall('<a href="(.+?)"',data)]
        urls = re.findall('href="(.+?)"',data)
        urls_to_look = [re.sub('amp;', '', '/'.join((self.main_URL,url))) for url in urls if 'Rubrics.aspx' in url and 'javascript' not in url]
        clean_urls_to_look = []
        print '1st stage done'

        for url in urls_to_look:
            if url not in clean_urls_to_look:
                clean_urls_to_look.append(url)
        clean_urls = [url for url in urls if 'Article.aspx' in url and 'javascript' not in url]
        print 'main articles mathed'
        for url in clean_urls_to_look:
            apr1 = re.findall('class="ArticleRubric"(.+?)<span id="ctl00_FormView1_CurrentNumLabel">',self.getData(url), re.DOTALL)[0]
            sub_urls = re.findall('href="(.+?)"',apr1)
            clean_urls.extend(sub_urls)
            print url, ' : ', len(sub_urls)
            del sub_urls
        urls = clean_urls[:]
        clean_urls = []
        for url in urls:
            if url not in clean_urls:
                clean_urls.append(url)
        self.urls = ['/'.join((self.work_URL, re.sub('Article','Print',url))) for url in clean_urls]
        print 'all preps done'


class getKOM (GetGaz):
    """GET KOM      """

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getCN object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h1>(.+?)</h1>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<div class="dateauthor">.+?<br>(.*?)<br>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div class="patext">(.+?)</P></div>',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(r'<div class="pmnumber">.+?(\d+)',re.DOTALL)
        #atribs
        self.main_URL = r'http://comments.com.ua'
        self.work_URL = self.main_URL
        self.filename = 'cp_kom_'

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
        urls = re.findall(r'href=".+?art=(.+?)"',data)
        cl_urls = []
        for url in urls:
            if url not in cl_urls:
                cl_urls.append(url)
        self.urls = [''.join((self.main_URL, '/?art=', url)) for url in cl_urls]

class getKyivPost(GetGaz):

    def __init__ (self,DATE = False,TEST = False, PROXIE = False):
        """Initialize getCN object with basic patterns and other stuff
            DATE may be specified in ('yyyy','mm','dd')format"""
        GetGaz.__init__(self, DATE = False,TEST = False, PROXIE = False)
        #patterns
        self.pattern_match_title = re.compile (r'<h4>(.+?)</h4>',re.DOTALL)# Заголовок
        self.pattern_match_author = re.compile (r'<span class="gray" style="width: 300px;">.+?\|(.+?)</span>',re.DOTALL) # Автор
        self.pattern_match_content = re.compile (r'<div class="zag-story2">.+?</span>(.+?)<div class="copyrights gray"',re.DOTALL) # Текст статьи
        self.pattern_match_number = re.compile(r'Issue #(\d+)',re.DOTALL)
        #atribs
        self.main_URL = r'http://www.kyivpost.com'
        self.work_URL = self.main_URL + '/newspaper/'
        self.filename = 'cp_kyivpost_'

    def compileUrlsList (self):
        """finds and assigns urls to self.urls """
        print u'Ищем статьи...'
        data = self.getData(self.work_URL)
        urls = re.findall(r'href="(.+?/\d+/)"',data)
        cl_urls = []
        for url in urls:
            if url not in cl_urls:
                cl_urls.append(url)
        self.urls = [''.join((self.main_URL, url, 'print/')) for url in cl_urls]

    def getContent (self, url):
        """Parse article content
           returns string containing article content stripped of garbage(at least trys)
           or None"""
        content = self.pattern_match_content.findall (self.data)
        if content:
            content = content[0]
            content = re.sub(r'<blockquote> <strong>.+?</strong><br />', '', content)
            for s1, s2 in self.content_substitution_pairs:
                content = re.sub (s1, s2, content)
            content = content.strip()
            return content
        return None

class getVD(GetGaz):
    pass

#TEST

def test():
    import pprint
    a = getCV()
    a.data = a.getData('http://www.silskivisti.kiev.ua/18587/print.php?n=7654')
    return a
a = test()
