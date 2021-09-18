import os
import json
from prometheus_client import Gauge,start_http_server
import time



# please change registry_path
registry_path = ""


def walk_through_repo(path):

    image_with_size_list = []
    project_with_size_dict = {}

    repositories_path = path + "/repositories/"
    for (dirpath, dirnames, filenames) in os.walk(repositories_path):
        for dirname in dirnames:
            if "current" in dirname:
                
                image_with_tag = dirpath.replace(repositories_path,"").replace('/_manifests/tags/',":")

                image_manifest_file = dirpath + "/" + dirname + "/link"
                with open(image_manifest_file,"r") as f:
                   manifest_hash = f.readline().split(":")[1]

                manifest_json_path = path + "/blobs/sha256/" + manifest_hash[0:2] + "/" + manifest_hash + "/data"
                
                image_size_byte = 0
                try:
                    with open(manifest_json_path,"r") as f:
                        manifest_json = json.load(f)
                    try:
                        for layer in manifest_json['layers']:
                            image_size_byte += int(layer['size']) 
                    except:
                        pass
                except:
                    pass

                each_image_with_size = {}
                each_image_with_size['image_with_tag'] = image_with_tag
                each_image_with_size['image_size_byte'] = image_size_byte

                image_with_size_list.append(each_image_with_size)

                project_name = image_with_tag.split('/',1)[0]
                if project_name in project_with_size_dict:
                    project_with_size_dict[project_name] += image_size_byte
                else:
                    project_with_size_dict[project_name] = image_size_byte
                

    return project_with_size_dict


if __name__ == '__main__':
    start_http_server(8000)
    g = Gauge("registry_watch", 'registry size',["registry_name"])
    while True:
        project_with_size_dict = walk_through_repo(registry_path)
        for project_name,size in project_with_size_dict.items():
            g.labels(project_name).set(size)          
        time.sleep(29)
