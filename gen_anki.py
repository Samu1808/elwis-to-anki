import enum
import json
from os import link
import shutil
from bs4 import BeautifulSoup
from pathlib import Path


class Image:
    def __init__(self, link, style, alt, html_path:Path) -> None:
        self.link = link
        self.style = style
        self.style_dict:dict = {}
        self.alt = alt
        self.html_path: Path = html_path
        self.name=''
        self.path:Path = Path()
        self.width = ''
        
        self._determine_path()
        self._determine_style()
    
    def _determine_style(self):
        style_dict_str = self.style.replace(';','","')
        style_dict_str = style_dict_str.replace(':','":"')
        style_dict_str = '{"' + style_dict_str[:-2] + '}'
        self.style_dict = json.loads(style_dict_str)
        self.width = self.style_dict["width"]
    
    def _determine_path(self):
        self.link = self.link.replace("%20", " ")
        link_path = Path(self.link)
        self.name = link_path.name
        if link_path.is_absolute():
            self.path = link_path
        else:
            self.path = self.html_path.parent / link_path
    
    def save_img_to(self, dest_path: Path):
        full_dest_path = dest_path / self.name
        shutil.copy(self.path, full_dest_path)
    
    def get_image_tag(self) -> str:
        return f'<img src="{self.name}" width="{self.width}">'
    
    
class QuestionCard:
    def __init__(self, question, title, q_1, q_2, q_3, q_4, images:list[Image] = [], answer="1 0 0 0", mode=2) -> None:
        self.question = question
        self.images:list[Image] = images
        self.title = title
        self.mode = mode
        self.q_1 = q_1
        self.q_2 = q_2
        self.q_3 = q_3
        self.q_4 = q_4
        self.answer = answer
    
    def _get_question_str(self) -> str:
        ret_str = self.question
        for image in self.images:
            ret_str += f'<br>{image.get_image_tag()}'
        return ret_str
    
    def get_csv_line(self, sep="|"):
        return f'{self._get_question_str()}{sep}{self.title}{sep}{self.mode}{sep}{self.q_1}{sep}{self.q_2}{sep}{self.q_3}{sep}{self.q_4}{sep}{self.answer}'


def scrape_html(html_file_path_str):
    html_file_path = Path(html_file_path_str)
    
    with open(html_file_path) as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    ols = soup.body.find_all("ol")
    
    question_ols = []
    for ol in ols:
        if "start" in ol.attrs and "type" in ol.attrs and len(ol.attrs)==3:
            question_ols.append(ol)
    question_cards: list[QuestionCard] = []
    for ol in question_ols:
        answers = ol.find_all("li")
        
        images: list[Image] = []
        if(len(answers) != 4):
            raise Exception(f"Unexpected amount of answers: {ol.text}")
        
        answer_str = []
        for answer in answers:
            answer_str.append(answer.text.replace("\n", ""))  
        
        if(ps := ol.find_all("p")):
            for p in ps:
                images.append(
                    Image(p.span.img['src'], p["style"], p.span.img['alt'], html_file_path)
                )
        temp_index = ol.li.text.find("\n")
        question = ol.li.text[0:temp_index]
        question_cards.append(QuestionCard(
            question,
            '',
            answer_str[0],
            answer_str[1],
            answer_str[2],
            answer_str[3],
            images
        ))      
                 
    return question_cards
            
def scrape_html(html_file_path_str):
    html_file_path = Path(html_file_path_str)
    
    with open(html_file_path) as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    ols = soup.body.find_all("ol")
    
    question_ols = []
    for ol in ols:
        if "start" in ol.attrs and "type" in ol.attrs and len(ol.attrs) == 3:
            question_ols.append(ol)
    
    question_cards: list[QuestionCard] = []
    for ol in question_ols:
        answers = ol.find_all("li")
        
        images: list[Image] = []
        if(len(answers) != 4):
            raise Exception(f"Unexpected amount of answers: {ol.text}")
        
        answer_str = []
        for answer in answers:
            answer_str.append(answer.text.replace("\n", "")) 
            
        # Loop backwards until we find the question <p> (no attributes)
        p = ol.find_previous_sibling("p")    
        while p:
            classes = p.get("class", [])
            if "picture" in classes: # found an image
                img_tag = p.find("img")
                if img_tag:
                    images.append(
                        Image(p.span.img["src"], p["style"], p.span.img['alt'], html_file_path)
                    )
            elif not p.attrs and p.text != '':  # found the question
                question_text = p.get_text(strip=True).replace("\n", "")
                break

            p = p.find_previous_sibling("p")
        
        question_cards.append(QuestionCard(
            question_text,
            '',
            answer_str[0],
            answer_str[1],
            answer_str[2],
            answer_str[3],
            images
        ))      
                 
    return question_cards  

def scrape_html_2(html_file_path_str):
    html_file_path = Path(html_file_path_str)
    
    with open(html_file_path) as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    ols = soup.body.find_all("ol")
    
    question_ols = []
    for ol in ols:
        if "start" in ol.attrs and "type" in ol.attrs and len(ol.attrs)==3:
            question_ols.append(ol)
    
    ps = soup.body.find(id="content").find_all("p")
    questions = []
    
    images = []
    image_index = 0
    
    for p in ps:
        try:
            if p.text[0].isdigit():
                images.append([])
                temp_index = p.text.find(".")
                questions.append(p.text[temp_index+2:].replace("\n", ""))
                
                p_tag = p
                while((p_img_tag := p_tag.find_next_sibling()).name == "p"):
                    images[image_index].append(
                        Image(p_img_tag.span.img['src'], p_img_tag["style"], p_img_tag.span.img['alt'], html_file_path)
                    )
                    p_tag=p_img_tag
                image_index += 1
                
        except IndexError:
            pass
        except AttributeError:
            pass
        
    print(len(questions))
    
    question_cards: list[QuestionCard] = []
    for i, ol in enumerate(question_ols):
        answers = ol.find_all("li")
        
        if(len(answers) != 4):
            raise Exception(f"Unexpected amount of answers: {ol.text}")
        
        answer_str = []
        for answer in answers:
            answer_str.append(answer.text.replace("\n", ""))  
        
        
        question_cards.append(QuestionCard(
            questions[i],
            '',
            answer_str[0],
            answer_str[1],
            answer_str[2],
            answer_str[3],
            images[i]
        ))      
                 
    return question_cards           


def scrape_html_3(html_file_path_str):
    html_file_path = Path(html_file_path_str)
    
    with open(html_file_path) as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    question_cards = []
    
    ps = soup.body.find(id="content").find_all("p")
    question_tags = []
    
    for p in ps:
        try:
            if p.text[0].isdigit():
                question_tags.append(p)
        except IndexError:
            pass
        except AttributeError:
            pass
    
    
    
    for p in question_tags:
        images = []
        temp_index = p.text.find(".")
        question = p.text[temp_index+2:].replace("\n", "")
        
        last_tag = p
        while True:
            tag = last_tag.find_next_sibling()
            if not (tag.name == "p" and "class" in tag.attrs and "picture" in tag["class"]):
                if(tag.name=="p"):
                    tag = tag.find_next_sibling()
                break
            images.append(
                Image(tag.span.img['src'], tag["style"], tag.span.img['alt'], html_file_path)
            )
            last_tag = tag
            
        
        if(tag.name != "ol"):
            raise ValueError(f"Unexpected {tag}")
        
        answers = tag.find_all("li")
        
        if(len(answers) != 4):
            raise Exception(f"Unexpected amount of answers: {tag.text}")
        
        answer_str = []
        for answer in answers:
            answer_str.append(answer.text.replace("\n", ""))  
        
        
        question_cards.append(QuestionCard(
            question,
            '',
            answer_str[0],
            answer_str[1],
            answer_str[2],
            answer_str[3],
            images
        ))
        
    
    return question_cards           
            
if __name__ == "__main__":
    output_folder = "./out'"
    output_file = "Segeln.csv"
    html_file = "./html_docs/ELWIS - Spezifische Fragen Segeln.html"

    output_folder = Path(output_folder)
    image_folder = output_folder / "images"
    if output_folder.exists() is False:
        output_folder.mkdir()
        image_folder.mkdir()
    with open(output_folder / output_file, 'w') as f:

        cards = scrape_html(html_file)
        print(f"{len(cards)}")
        for card in cards:
            for img in card.images:    
                img.save_img_to(image_folder)
            f.write(card.get_csv_line()+'\n')