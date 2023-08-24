import gradio as gr

import gdown
import glob
import os
import zipfile
import subprocess
from tqdm import tqdm
import pandas as pd
import warnings
import shutil
import json
warnings.filterwarnings('ignore')
from collections import deque
from huggingface_hub import hf_hub_download, login
login(token='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')

def addEdge(v, w):
    global visited, adj
    adj[v].append(w)
    adj[w].append(v)

def BFS(componentNum, src):
    global visited, adj
    queue = deque()
    queue.append(src)
    visited[src] = 1
    reachableNodes = []

    while (len(queue) > 0):
        u = queue.popleft()
        reachableNodes.append(u)
        for itr in adj[u]:
            if (visited[itr] == 0):
                visited[itr] = 1
                queue.append(itr)

    return reachableNodes

def findReachableNodes(arr, n):
    global V, adj, visited
    a = []
    componentNum = 0
    for i in range(n):
        u = arr[i]
        if (visited[u] == 0):
            componentNum += 1
            a1 = BFS(componentNum, u)
        return(a1)
    
def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

def unzipiing(folder):
    lst = glob.glob(folder+'/*') 
    index = 0
    while index < len(lst):
        i = lst[index]
        if(i[-4:]=='.zip'):
            os.chmod(i, 0o644)
            print(f"Flolder: {folder.split('/')[-1]}  and Zip file: {i.split('/')[-1]}")
            zip_file_path = i
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(zip_file_path))
            os.remove(i)
            new_list = glob.glob(folder+'/*')
            lst.extend((i for i in new_list if i not in lst))

        if(len(glob.glob(i+'/*'))!=0):
            print(f"processing subflolder: {i.split('/')[-1]}")
            unzipiing(i)
        else:
            pass
        index+=1
    return('Processed folder')


def process_folders(x):
    global V, adj, visited

    drive_link = x
    
    if not os.path.exists(os.getcwd() + '/1'):
        os.mkdir(os.getcwd() + '/1')

    # Download drive folder
    l = gdown.download_folder(drive_link)

    # Get the folder name
    folder_path = os.getcwd() + '/' + l[0].replace(os.getcwd()+'/','').split('/')[0]
    folder_name = l[0].replace(os.getcwd()+'/','').split('/')[0]

    # Prcoess the folder
    unzipiing(folder_path)

    shutil.move(os.getcwd() + '/' + l[0].replace(os.getcwd()+'/','').split('/')[0],os.getcwd() + '/1/' + l[0].replace(os.getcwd()+'/','').split('/')[0])

    # Retrieve all images in that folder
    # image_paths = glob.glob(f'{folder_path}/**/*.jpeg', recursive=True)

    # Create a temporary directory to work on folder
    # if not os.path.exists(os.getcwd()+f'/1/{folder_name}'):
        # os.makedirs(os.getcwd()+f'/1/{folder_name}')

    # Move all images to the new folder
    # for i in image_paths:
        # if os.path.exists(os.getcwd()+f'/1/{folder_name}/'+i.split('/')[-1]):
            # continue
        # shutil.move(i, os.getcwd()+f'/1/{folder_name}/')

    # Process images
    l_final = []
    for folder in tqdm(glob.glob(os.getcwd() + '/1/*')):
        folder_path = str(folder) + '/'
        result = subprocess.run(['find-dups', '--max-distance', '0', folder_path], capture_output=True, text=True)
        output_lines = result.stdout.strip().split('\n')
        
        # Create an empty list to store matched image paths
        matched_paths1 = []
        matched_paths2 = []

        # Iterate over output lines and extract matched paths
        for line in output_lines:
            if line.startswith('/home/'):
                matched_paths1.append(line.split(' /home')[0].strip())
                matched_paths2.append('/home'+line.split(' /home')[1].strip())
            
        # Post processing on data
        df = pd.DataFrame()
        df['1'] = list(map(lambda x:x.replace(str(folder_path),'').replace('.jpeg',''), matched_paths1))
        df['2'] = list(map(lambda x:x.replace(str(folder_path),'').replace('.jpeg',''), matched_paths2))
        
        df.columns = ['match1', 'match2']
        
        df1 = pd.DataFrame()
        df1['1'] = list(set(df['match1'].unique().tolist()+ df['match2'].unique().tolist()))
        V = len(df1)
        df1['1'] = df1['1'].apply(lambda x:x.strip())
            
        new_dict = dict([(value, key) for key, value in df1.to_dict()['1'].items()])
        new_dict1 = dict([(value, key) for key, value in new_dict.items()])
        
        df['match1_code'] = df['match1'].apply(lambda x:new_dict[x.strip()])
        df['match2_code'] = df['match2'].apply(lambda x:new_dict[x.strip()])
        
        df = df[['match1_code', 'match2_code']].drop_duplicates().reset_index(drop=True)

        adj = [[] for i in range(V + 1)]
        for i in range(len(df)):
            addEdge(int(df['match1_code'][i]), int(df['match2_code'][i]))
                
        final_l = []
        check_list = list(range(V))
            
        for i in range(V):
            flt_lst = [mm for mm_sub in final_l for mm in mm_sub]
            if(i in flt_lst):
                continue
            visited = [0 for i in range(V + 1)]
            arr = [i]
            aa = findReachableNodes(arr, 1)
            final_l.append(sorted(aa))

            
        df__ = pd.DataFrame()
        df__['groups'] = final_l
        df__ = df__.drop_duplicates().reset_index(drop=True)
            
        l_ff = []
        for i in df__['groups']:
            if(len(i)==1):
                continue
            lll = []
            for j in i:
                lll.append(new_dict1[j])
            l_ff.append(lll)
            
        df_final_grouped = pd.DataFrame()
        df_final_grouped['groups'] = l_ff
        df_final_grouped['state'] = str(folder).split('/')[-1]
        
        # df_final_grouped.to_excel(os.getcwd()+'/' +str(folder).split('/')[-1].replace(' ','_')+'.xlsx', index=False)
        
        l_final.append(df_final_grouped)

    df = pd.concat(l_final, ignore_index=True)

    df.to_excel("matched_images.xlsx", index=False)

    shutil.rmtree(os.getcwd() + '/1/')

    return("matched_images.xlsx")


def remove_duplicates(x):
    drive_link = x
    
    if not os.path.exists(os.getcwd() + '/1'):
        os.mkdir(os.getcwd() + '/1')

    # Download drive folder
    l = gdown.download_folder(drive_link)

    # Get the folder name
    folder_path = os.getcwd() + '/' + l[0].replace(os.getcwd()+'/','').split('/')[0]
    folder_name = l[0].replace(os.getcwd()+'/','').split('/')[0]

    # Prcoess the folder
    unzipiing(folder_path)

    shutil.move(os.getcwd() + '/' + l[0].replace(os.getcwd()+'/','').split('/')[0],os.getcwd() + '/1/' + l[0].replace(os.getcwd()+'/','').split('/')[0])

    # Process folder
    for i in tqdm(glob.glob(os.getcwd()+'/1/*')):
        # Find duplicate images
        folder_path = str(i) + '/'
        result = subprocess.run(['find-dups', '--max-distance', '0', folder_path, '--on-equal', 'delete-smaller'])
    
    zip_folder(os.getcwd()+'/1/', "processed_file.zip")

    shutil.rmtree(os.getcwd() + '/1/')

    return("processed_file.zip")

    
def same_auth(username, password):
    #global user
    #global pwd
    hf_hub_download(repo_id="tttarun/auth_database", repo_type = 'dataset',filename = 'credentials_image_duplication.json',local_dir = 'credentials')
    with open('credentials/credentials_image_duplication.json', 'r') as fp:
        user_dict = json.load(fp)

    user = username
    pwd = password
    
    if user in user_dict.keys():
        if user_dict[user] == pwd:
            return True
        else:
            return False
    else:
        return False

with gr.Blocks() as my_demo:
    gr.Markdown("Demo app to find the duplicate images within a folder and return a excel file containing groups of matched images")
    with gr.Tab("Process drive link"):
        with gr.Row():
            input = gr.Textbox()
            output = gr.File()
        image_button = gr.Button("Return info")
        with gr.Row():
            input1 = gr.Textbox()
            output1 = gr.File()
        image_button1 = gr.Button("Return processed folder")

    with gr.Accordion("Open for More!"):
        gr.Markdown("Look at me...")

    image_button.click(process_folders, inputs=input, outputs=output)
    image_button1.click(remove_duplicates, inputs=input1, outputs=output1)



my_demo.launch(auth=same_auth)
