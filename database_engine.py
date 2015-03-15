import lxml.etree as ET
import uuid
import datetime
import os

from config import DB_ROOT, TAGFILE, TAGS_DIR, NODES_DIR

# Helper functions
get_tag_xml_file = lambda filename: TAGS_DIR + filename + ".xml"
get_node_xml_file = lambda filename: NODES_DIR + filename + ".xml"
remove_knodefile = lambda knode_file: os.remove(knode_file)


def create_dir_if_necessary(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def create_database_if_needed():
    create_dir_if_necessary(DB_ROOT)
    create_dir_if_necessary(TAGS_DIR)
    create_dir_if_necessary(NODES_DIR)

def remove_knode_id_from_tagfiles(knode_id, tags):
    for tag in tags:
        tag_file = get_tag_xml_file(tag)
        tag_xml = ET.parse(tag_file)
        tag_root = tag_xml.getroot()
        for tag_knode_id in tag_root.findall('knode_id'):
            if tag_knode_id.text == knode_id:
                tag_root.remove(tag_knode_id)                        
        tag_xml.write(tag_file, pretty_print=True)

def write_tag_to_tagfile(tag):
    tagfile_f = open(TAGFILE, 'a')
    tagfile_f.write(tag + '\n')
    tagfile_f.close()
    
def create_knode(title, text, tags):
    knode_xml = ET.Element('knode')

    if title:
        knode_xml.set('title', title.lstrip())

    u_id = str(uuid.uuid4())
    knode_xml.set('knode_id', u_id)
      
    time_created =  datetime.datetime.now().strftime("%b %d, %Y %H:%M:%S")
    knode_created = ET.SubElement(knode_xml, 'created')
    knode_created.text = time_created
    knode_last_updated = ET.SubElement(knode_xml, 'last_updated')
    knode_last_updated.text = time_created

    #! And other data sanitization
    knode_text = ET.SubElement(knode_xml, 'text')
    knode_text.text = text.lstrip()

    for tag_text in tags:
        tag = ET.SubElement(knode_xml, 'tag')
        tag.text = tag_text

    knode_question = ET.SubElement(knode_xml, 'question')
    knode_question.text = ""

    knode_answer = ET.SubElement(knode_xml, 'answer')
    knode_answer.text = ""
    
    knode_comments = ET.SubElement(knode_xml, 'comments')
    knode_comments.text = ""

    tree = ET.ElementTree(knode_xml)
    filename = get_node_xml_file(u_id)
    tree.write(filename, pretty_print=True)
    return u_id

def save_tags(tags, knode_id):
    for tag in tags:
        tag_text = tag
        filename = get_tag_xml_file(tag_text)

        new_tags = []
        if not os.path.isfile(filename):
            tag_xml = ET.Element('tag')
            tag_xml.set('title', tag_text)
            tag_knode_id = ET.SubElement(tag_xml, 'knode_id')
            tag_knode_id.text = knode_id
            tree = ET.ElementTree(tag_xml)    
            tree.write(filename, pretty_print=True)
            new_tags.append(tag_text)
        else:
            tag_xml = ET.parse(filename)
            root = tag_xml.getroot()
            tag_knode_id = ET.SubElement(root, 'knode_id')
            tag_knode_id.text = knode_id
            tag_xml.write(filename, pretty_print=True)

        tagfile_f = open(TAGFILE, 'a')
        for new_tag in new_tags:
            tagfile_f.write(new_tag + '\n')
        tagfile_f.close()

def get_knode(knode_id):
    knode_file = get_node_xml_file(knode_id)
    if os.path.isfile(knode_file):
        knode_xml = ET.parse(knode_file)
        knode_root = knode_xml.getroot()
        knode_title = knode_root.get('title')
        for text in knode_root.findall('text'):
            knode_text = text.text
        tags = ""
        for tag in knode_root.findall('tag'):
            tags = tags + " " + tag.text

        for question in knode_root.findall('question'):
            knode_question = question.text
            if knode_question == None:
                knode_question = ""
        for answer in knode_root.findall('answer'):
            knode_answer = answer.text
            if knode_answer == None:
                knode_answer = ""
        for comments in knode_root.findall('comments'):
            knode_comments = comments.text
            if knode_comments == None:
                knode_comments = ""
        return [knode_title, knode_text, tags.lstrip(), knode_question, knode_answer, knode_comments]
    else:
        return None

def get_all_tags():
    if os.path.isfile(TAGFILE):
        tagfile_f = open(TAGFILE, 'r')
        all_tags = tagfile_f.readlines()
        cleaned_tags = []
        for tag in all_tags:
            cleaned_tag = tag.split('\n')[0]
            cleaned_tags.append(cleaned_tag)
        return cleaned_tags
    else:
        return None

def get_knodes_for_tags(all_tags):
    if not all_tags:
        return None
    tags_with_knodes = []
    for tag in all_tags:
        filename = get_tag_xml_file(tag)
        tag_xml = ET.parse(filename)
        tag_root = tag_xml.getroot()
        knodes = []
        for knode_id in tag_root.findall('knode_id'):
            knode_file = get_node_xml_file(knode_id.text)
            knode_xml = ET.parse(knode_file)
            knode_root = knode_xml.getroot()
            knode_title = knode_root.get('title')
            for text in knode_root.findall('text'):
                knode_text = text.text
            for question in knode_root.findall('question'):
                knode_question = question.text
            for answer in knode_root.findall('answer'):
                knode_answer = answer.text
            for comments in knode_root.findall('comments'):
                knode_comments = comments.text
            knodes.append([knode_id.text, knode_title, knode_text, knode_question, knode_answer, knode_comments])
        tags_with_knodes.append([tag, knodes])
    return tags_with_knodes

def get_knode_list(all_tags):
    tags_with_knodes = get_knodes_for_tags(all_tags)
    knode_list = []
    for tag, knodes in tags_with_knodes:
        for knode in knodes:
            knode_list.append(knode)
    return knode_list

def update_knode(knode_id, new_title, new_text, new_tags, new_question, new_answer, new_comments):
    knode_file = get_node_xml_file(knode_id)
    if os.path.isfile(knode_file):
        knode_xml = ET.parse(knode_file)
        knode_root = knode_xml.getroot()

        if knode_root.get('title') != new_title:
            knode_root.set('title', new_title) 

        for knode_text in knode_root.findall('text'):
            if knode_text.text != new_text:
                knode_text.text = new_text

        old_tags = []
        for tag in knode_root.findall('tag'):
            old_tags.append(tag.text)
            #! Check if tags have been removed
            if tag.text not in new_tags:
                knode_root.remove(tag)
                remove_knode_id_from_tagfiles(knode_id, [tag.text])

        #! Check if new tags have been added
        for new_tag in new_tags:
            if new_tag not in old_tags:
                tag = ET.SubElement(knode_root, 'tag')
                tag.text = new_tag
                #! Add to tag_file as well
                tag_file = get_tag_xml_file(new_tag)
                if os.path.isfile(tag_file):
                    tag_xml = ET.parse(tag_file)
                    tag_root = tag_xml.getroot()
                    tag_knode_id = ET.SubElement(tag_root, 'knode_id')
                    tag_knode_id.text = knode_id
                    tag_xml.write(tag_file, pretty_print=True)
                else: 
                    tag_xml = ET.Element('tag')
                    tag_xml.set('title', tag.text)
                    tag_knode_id = ET.SubElement(tag_xml, 'knode_id')
                    tag_knode_id.text = knode_id
                    tree = ET.ElementTree(tag_xml)    
                    tree.write(tag_file, pretty_print=True)
                    write_tag_to_tagfile(tag.text) 

        for knode_question in knode_root.findall('question'):
            if knode_question != new_question:
                knode_question.text = new_question

        for knode_answer in knode_root.findall('answer'):
            if knode_answer != new_answer:
                knode_answer.text = new_answer

        for knode_comments in knode_root.findall('comments'):
            if knode_comments != new_comments:
                knode_comments.text = new_comments

        knode_xml.write(knode_file, pretty_print=True)

def sanitize_tags(tags):
    new_tags = []
    for tag in tags:
        if tag != "":
            new_tags.append(tag.lstrip())
    return new_tags
