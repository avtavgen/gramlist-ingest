import os
import re

from datetime import datetime
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator


class GramlistProcessor(object):
    def __init__(self, entity, log):
        self.info = []
        self.log = log
        self.entity = entity

    def _get_users(self):
        for file in self._get_file_names():
            raw_text = self._get_file_text(file)
            pattern = "\d+\. @([^\s]+)\n(.+?)\n30-DAY ENGAGEMENT RATE:(.+?)\n"
            main_data = re.compile(pattern, re.S)
            creators = main_data.findall(raw_text)
            for creator in creators:
                self.info.append(self._get_user_info(creator))
            self.entity.save(users=self.info)

    def _get_user_info(self, creator):
        categories = ["lifestyle", "travel", "beauty", "fashion"]
        user_data = dict()
        engagement_rate = creator[2].strip()
        if engagement_rate.endswith("%"):
            engagement_rate = engagement_rate.replace("%", "")
        user_data["uri"] = "gramlist␟user␟{}".format(creator[0])
        user_data["ingested"] = False
        user_data["date"] = datetime.now().strftime("%Y-%m-%d")
        user_data["screen_name"] = creator[0]
        user_data["engagement_rate"] = engagement_rate
        user_data["categories"] = categories
        user_data["profile"] = self.get_description(creator[1])
        user_data["followers"] = self.get_followers(creator[1])
        user_data["location"] = self.get_location(creator[1])
        user_data["wow_growth"] = self.get_growth(creator[1])
        user_data["posting_average"] = self.get_posting_av(creator[1])
        user_data["likes_to_comments"] = self.get_likes(creator[1])
        return user_data

    def _get_file_names(self):
        files = []
        for _, _, f in os.walk("data/"):
            for file in f:
                files.append(file)
        return files

    def _get_file_text(self, filename):
        password = ""
        extracted_text = ""

        fp = open('data/' + filename, "rb")
        parser = PDFParser(fp)

        document = PDFDocument(parser, password)

        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()

        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    extracted_text += lt_obj.get_text()

        fp.close()

        extracted_text = extracted_text.replace("CONTACT\n", "")
        return extracted_text

    def get_description(self, info):
        desc_pattern = "(.+?)\nFOLLOWERS:.+?"
        description_p = re.compile(desc_pattern, re.S)
        description = description_p.search(info)
        return description.group(1).replace("\n", "")

    def get_followers(self, info):
        fl_pattern = "FOLLOWERS:\s*([^\s]+)"
        followers = re.search(fl_pattern, info)
        followers = followers.group(1).replace(",", "")
        if followers.endswith("K"):
            if "." in followers:
                followers = followers.replace(".", "").replace("K", "00")
            else:
                followers = followers.replace("K", "000")
        return int(followers)

    def get_location(self, info):
        l_pattern = "LOCATION:\s*(.+?)\n"
        location = re.search(l_pattern, info)
        return location.group(1)

    def get_growth(self, info):
        g_pattern = "W/O/W \s*GROWTH:\s*(-*\d*\.*\d+)"
        growth = re.search(g_pattern, info)
        growth = growth.group(1)
        if growth.endswith("%"):
            growth = growth.replace("%", "")
        return growth

    def get_posting_av(self, info):
        g_pattern = "DAILY POSTING AVERAGE:\s*(\d*\.*\d+)"
        p_average = re.search(g_pattern, info)
        return p_average.group(1)

    def get_likes(self, info):
        g_pattern = "AVERAGE \s*LIKES \s*& \s*COMMENTS:\s*(\d+K*,*\.*\d* \s*/\s* \d*K*,*\.*\d*)*"
        l_average = re.search(g_pattern, info)
        return l_average.group(1)

    def fetch(self):
        self.log.info('Making Gramlist monthly creators export')
        self._get_users()
        return self
