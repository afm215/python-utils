
import os
from PIL import Image
import numpy as np 
from tqdm import tqdm 
import pickle
import io

def convert_img_to_bin(img: Image.Image, encoding_format:str=None):
    if encoding_format is None:
        encoding_format = img.format
    img = Image.fromarray(np.asarray(img))
    img_b = io.BytesIO()
    img.save(img_b, format=encoding_format)
    img_b =  img_b.getvalue()
    return img_b


def extract_imgs_from_bin(bin_content: str):
    import pickle
    import struct
    from PIL import Image
    import cv2
    import numpy as np
    returned_data = []
    # with open(bin_file, "rb") as file:
    _index = 0
    data_length_b = bin_content[_index:_index + 4]
    key = None
    i = 0
    while data_length_b:
        print("index ", _index)
        _index += 4
        data_length = struct.unpack('I', data_length_b)[0]
        print(data_length)
        try:
            key =bin_content[_index: _index + data_length].decode("utf-8")
        except Exception as e:
            if key is None:
                key = "img_" + str(i)
           
            img_b = bin_content[_index: _index + data_length]
            img_b = pickle.loads(img_b, encoding='bytes')
            img_b = np.frombuffer(img_b, dtype='uint8')
            img = cv2.imdecode(img_b, 1)
            print(img.shape)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            PIL_img = Image.fromarray(img.astype(np.uint8))
            i+=1
            returned_data.append([key, PIL_img])
            print(f"{i} images extracted", flush=True, end="\n")
            key = None
                
                
        _index += data_length
        data_length_b = bin_content[_index:_index + 4]
        
    return returned_data

def extract_and_save_img_from_bin(bin_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    extracted_imgs = extract_imgs_from_bin(bin_file)
    print(flush=True)
    nb_imgs = len(extracted_imgs)
    print("will extract ", nb_imgs, " images", flush=True)
    for  extracted_img in tqdm(extracted_imgs):
        key, img = extracted_img
        img.save(os.path.join(output_folder, key+".png"))
    print(flush=True)
    print("done", flush=True)


def save_imgs_in_bin(imgs_list, output_file, img_names= None, encoding_format="PNG"):
    import struct
    import io
    with open(output_file, "wb") as fo:
        if img_names is None:
            img_names = [f"img_{i}" for i in range(len(imgs_list))]
        for i in tqdm(range(len(imgs_list)// 10)):
            img_name:str  = img_names[i]
            img = Image.fromarray(np.asarray(imgs_list[i]))
            img_b = convert_img_to_bin(img, encoding_format)
            img_b =  pickle.dumps(img_b, -1)
            img_name_b = img_name.encode()
            print(len(img_name_b))
            print(struct.pack('I', len(img_name_b)))
            fo.write(struct.pack('I', len(img_name_b)))
            print(img_name_b)
            fo.write(img_name_b)
            fo.write(struct.pack('I', len(img_b)))
            fo.write(img_b)
        fo.flush()




    









        


            




