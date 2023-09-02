import re
import io
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain, filterfalse
from typing import Callable, TypedDict, Union, BinaryIO, Dict
from datetime import datetime, date 


import easyocr
import streamlit as st
from PIL import Image, ImageDraw


@st.cache_resource
def load_model():
    return  easyocr.Reader(['en'])


def draw_boxes(
        image:Union[str, BinaryIO],
          bounds:list, 
          color:str='red',
            width:int=2
            ):
    """
    Draws the bounding boxes on the texts on the image

    Args:
        :param image: (str|Byte): Path to the image or image bytes
        :param bounds: (list): List of bounding boxes
        :param color: (str): Color of the bounding box
        :param width: (int): Width of the bounding box

    Returns:
        :return: (PIL.Image): Image with bounding boxes
    """
    if isinstance(image, str):
        img = Image.open(image)
    else:
        img = Image.open(io.BytesIO(image))

    draw = ImageDraw.Draw(img)
    for bound in bounds:
        p0, p1, p2, p3 = bound[0]
        draw.line([*p0, *p1, *p2, *p3, *p0], fill=color, width=width)

    return img


class OCRResult(TypedDict):
    created: date
    amount_sent: float
    amount_recieved: float
    amount_sent_fee: float


@dataclass
class OCR:
    model: Callable
    result_string: str = None


    def detect(self, image:Union[str, BinaryIO]):
        """
        Predicts the result of the OCR model
        Args:
            :param image: (str|Byte): Path to the image or image bytes
        Returns:
            :return:  (PIL.Image): Image with bounding boxes
        """
        results = None
        if isinstance(image, str):
            with open(image, 'rb') as f:
                img = f.read() 
                results = self.model.readtext(img)
        else:
            results = self.model.readtext(image, detail=0)

        if not results:
            raise ValueError('No results found')

        # texts = [result[1] for result in results]
        
        self.result_string  = ' '.join(results)

        # print(texts)

        return draw_boxes(image, self.model.readtext(image))
    

        
    def extract_info(self)->OCRResult:
        """
        Extracts information from the result of the OCR model
        
        Returns:
            :return: (dict): Extracted information
        """
        results = {}
        regex = re.compile(r'\d{1,2},\d{3}.\d{2}')
        regex_date = re.compile(r'(\d{1,2}/\d{1,2}/\d{4})')


        if self.result_string is None:
            raise ValueError('Result string is empty')
        
        date = regex_date.search(self.result_string)
        if date:
            results['created'] = datetime.strptime(date.group(), '%d/%m/%Y').date()
        
        amount_list = regex.findall(self.result_string)
        if len(amount_list) == 3:
            amount_list = [float(amount.replace(',', '')) for amount in amount_list]
            amount_sent, amount_recieved, amount_sent_fee = amount_list
            results['amount_sent'] = amount_sent
            results['amount_recieved'] = amount_recieved
            results['amount_sent_fee'] = amount_sent_fee

        
        return results
        
    
   
   
        

   