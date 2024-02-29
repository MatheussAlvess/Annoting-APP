import os
import streamlit as st
from PIL import Image

from streamlit_tags import st_tags_sidebar
from streamlit_image_annotation import detection


if 'counter' not in st.session_state: 
    st.session_state.counter = 0

if 'image_labels' not in st.session_state:
    st.session_state.image_labels = []

def save_to_yolo_format(data, image, output_file):
    def convert_bbox_to_yolo(bbox, image_width, image_height):
        x, y, w, h = bbox
        x_center = (x + w / 2) / image_width
        y_center = (y + h / 2) / image_height
        width = w / image_width
        height = h / image_height
        return x_center, y_center, width, height
    
    image_width, image_height = image.size
    
    with open(output_file, 'w') as f:
        for bbox, label in zip(data['bboxes'], data['labels']):
            x_center, y_center, width, height = convert_bbox_to_yolo(bbox, image_width, image_height)
            line = f"{label} {x_center} {y_center} {width} {height}\n"
            f.write(line)

def saving_increment(name,img):
    ## Incrementa o contador para obter a próxima foto
    img = Image.open(img)
    if img.size[1] < 500:
        img = img.resize((500,500)) 
    img_aux = img.copy()
    img = img.save(f'images_annoted/{name}')

    save_to_yolo_format(st.session_state['result_dict'][name],
                        img_aux, f"labels_annoted/{name.split('.')[0]}.txt")
    

    st.session_state.counter += 1


def decrement():
    ## Incrementa o contador para obter a próxima foto
    st.session_state.counter -= 1

def main():
    st.set_page_config(initial_sidebar_state="expanded")
    st.title("Image to be annotated")
    st.sidebar.title('Image Uploader')

    uploaded_files = st.sidebar.file_uploader("Choose images", accept_multiple_files=True)
    labels = st_tags_sidebar(
        label='# Enter the labels :',
        text='Press enter to add more')

    if not uploaded_files or not labels:
        st.warning("Please upload images and enter labels.")
        return
    
    images = []
    progress_text = "Annoting progress."
    if uploaded_files and labels:

        # Dividir as etiquetas
        labels = [label.strip() for label in labels]
        
        for path in [labels[i] for i in range(len(labels))]:
            try:
                os.mkdir(f'images_annoted/')
            except:
                pass
            try:
                os.mkdir(f'labels_annoted/')
            except:
                pass

        for uploaded_file in uploaded_files:
            images.append(uploaded_file)
   
        label_list = [label.strip() for label in labels]
       
        if 'result_dict' not in st.session_state:
            result_dict = {}
            for img in images:
                result_dict[img.name] = {'bboxes': [],'labels':[]}
            st.session_state['result_dict'] = result_dict.copy()

        try:
            target_image_path = images[st.session_state.counter]
            new_labels = detection(image_path=target_image_path, 
                                bboxes=st.session_state['result_dict'][target_image_path.name]['bboxes'], 
                                labels=st.session_state['result_dict'][target_image_path.name]['labels'], 
                                label_list=label_list, key=target_image_path.name)
            if new_labels is not None:
                st.session_state['result_dict'][target_image_path.name]['bboxes'] = [v['bbox'] for v in new_labels]
                st.session_state['result_dict'][target_image_path.name]['labels'] = [v['label_id'] for v in new_labels]
            
            # st.json(st.session_state['result_dict'])
            
            col1, col2 = st.columns([1,1])

            with col1:
                st.button(f"Previous image",on_click=decrement)
            with col2:
                st.button(f"Next image",on_click=saving_increment,args=[images[st.session_state.counter].name,images[st.session_state.counter]])

            st.progress((st.session_state.counter/len(images)), text=progress_text)
           
        except:
            st.success("All images has been labeled successfully!")
            st.balloons()


if __name__=='__main__':
    main()