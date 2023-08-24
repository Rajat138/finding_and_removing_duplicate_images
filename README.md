---
title: Image Duplicate Handle
emoji: 🏃
colorFrom: pink
colorTo: green
sdk: gradio
sdk_version: 3.36.1
app_file: app.py
pinned: false
license: mit
---

# handling_image_duplication
handling image duplication

## Expected Input format:
1. Pass the drive link of the folder within which you need to find duplicate images
2. Make sure the drive link is publically accessed with editor rights
3. Any two images within that folder must not have same name otherwise one of them will be ignored
4. Images should be of .jpeg extension

## Setup:
#Clone repository  
git clone github....  
cd handling_image_duplication  

#create environment  
virtualenv  
source bin/activate  
pip install -r requirements.txt  


## Command line usage
```
python duplicateimages.py --link "drive-link" --remove False/True
```

## Huggingface demo
visit https://tttarun-jarvis-image-duplicate-handle.hf.space/ for interactive demo
