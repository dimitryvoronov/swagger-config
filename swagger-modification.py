#! /bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import yaml
import re
from yaml import load, dump

def endpointsf(file):
    with open(arguments.path+file + ".yaml", 'r') as swaggerYaml:
        try:
            parsed_yaml=yaml.safe_load(swaggerYaml)
        except yaml.YAMLError as exc:
            print(exc)

    paths = (parsed_yaml['paths'])

    for path, pathValue in list(paths.items()):
        cb_match = re.match(callback_pattern,path)
        if cb_match:
            try:
                del paths[cb_match.string]
            except KeyError as ex:
                print("error is %", ex)

    # a temp file to save a whole swagger structure
    with open((file + "-" + "tmp" + ".yaml"), "w") as f:
        yaml.dump(parsed_yaml, f)

    with open(file + "-" + "tmp" + ".yaml", 'r') as swaggerYaml:
        try:
            new_parsed_yaml=yaml.safe_load(swaggerYaml)
        except yaml.YAMLError as exc:
            print(exc)

    path_new = new_parsed_yaml['paths']
    for path, pathValue in list(new_parsed_yaml['paths'].items()):
        count = 0
        for method, methodkeys in pathValue.items():
            # if count > 1:x
            #     break
            for x_async, x_async_value in methodkeys.items():
                if count > 0:
                    break
                if re.findall(async_pattern,x_async):
                    count = count + 1
                    reqcbpath = ("/reqcb" + path)
                    path_new[reqcbpath] = path_new.pop(path)
    new_parsed_yaml['info']['title'] = (parsed_yaml['info']['title']) + " " + endpoints


    if os.path.exists(swaggerFile + "-" + "tmp" + ".yaml"):
        os.remove(swaggerFile + "-" + "tmp" + ".yaml")
        #print("The file has been deleted successfully")
    else:
        print("The file does not exist!")

    # save endpoints file
    print("Saving endpoints file")
    with open((swaggerFile + "-" + endpoints + ".yaml"), "w") as f:
        yaml.dump(new_parsed_yaml,f, default_flow_style=False, sort_keys=False)


def callbacksf(file):
    with open(arguments.path+file+".yaml", 'r') as swFile:
        try:
            callback_yaml=yaml.safe_load(swFile)
        except yaml.YAMLError as exc:
            print(exc)

    for path, pathValue in list(callback_yaml['paths'].items()):
        endp_match = re.match(endpoint_pattern,path)
        if endp_match:
            try:
                #print(path)
                del callback_yaml['paths'][endp_match.string]
            except KeyError as ex:
                print("error is %", ex)

    callback_yaml['info']['title'] = (callback_yaml['info']['title']) + " " + callbacks
    # save callbacks file
    print("Saving callbacks file")
    with open((swaggerFile + "-" + callbacks + ".yaml"), "w") as f:
        yaml.dump(callback_yaml,f, default_flow_style=False, sort_keys=False)


# Execute `main()` function
if __name__ == '__main__':

    callback_pattern = f'^/callback.*'
    endpoint_pattern = f'^((?!callback).)*$'
    async_pattern = f'x-async-responses'
    endpoints = "Endpoints"
    callbacks = "Callbacks"
    ms_name=os.getenv('CI_PROJECT_NAME')
    parser = argparse.ArgumentParser(description='Search swagger yaml file in microservice repository')
    parser.add_argument('-p', '--path', required=True, help='Path to conf dicrectory')
    arguments = parser.parse_args()

    for filename in os.listdir(arguments.path):
        if ms_name in filename:
            print("Swagger file", filename, "is used")
            swaggerFile = os.path.join(arguments.path, filename)
            swaggerFile = os.path.splitext(filename)[0]
            endpointsf(swaggerFile)
            callbacksf(swaggerFile)
