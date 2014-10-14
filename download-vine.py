import sys, json, os, re, argparse, time, urllib, string
from urllib.request import urlopen 
from random import uniform

def get_filename(video_url):
    regobj = re.search("(s\/)(.*?)\mp4", video_url)
    return regobj.group()[2:]

def sanitize(s):
    valid_ch = frozenset("-_.() %s%s" % (string.ascii_letters, string.digits))
    return "".join(ch if ch in valid_ch else "_" for ch in s)

def main(args):
    api_profile = "https://api.vineapp.com/users/profiles/"
    api_timeline = "https://api.vineapp.com/timelines/users/"
    vine_id = args.id
    url = api_profile + vine_id
    path = args.path
    if args.revine.lower() in ("false", "no", "f", "0"):
        include_revines = False
    else:
        include_revines = True
    if args.description.lower() in ("false", "no", "f", "0"):
        use_description = False
    else:
        use_description = True

    # Check if directory exists
    if not os.path.exists(path):
        print("Invalid path")
        sys.exit(9)

    # Get Vine profile JSON 
    print(url)
    
    jsonurl = urlopen(url)
    profile_data = json.loads(jsonurl.read().decode('utf8'))
    jsonurl.close()
    
    # except:
    #   # Will get thrown if ID is not valid
    #   print("Error parsing ID")
    #   sys.exit(0)
    
    username = profile_data["data"]["username"]
    nextPage = 1
    count=0
    while(True):
        time.sleep(uniform(0.50, 1.75))
        print("Downling page: "+str(nextPage))
        if (nextPage!=1):
            url=api_timeline + vine_id + "?page=" +str(nextPage) + "&anchor="+str(anchor)+"&size=999999"
        else:
            url = api_timeline + vine_id + "?size=999999"
        # Get timeline JSON
        try:
            print(url)
            jsonurl = urlopen(url)
            timeline_data = json.loads(jsonurl.read().decode('utf8'))
            jsonurl.close()
            print (timeline_data["data"]["anchor"])
            
        except:
            print("Error retrieving timeline")
            sys.exit(0)

        nextPage=nextPage+1
        anchor = timeline_data["data"]["anchor"]
        
        # Loop through all videos on the timeline 
        for record in timeline_data["data"]["records"]:

            video_url = record["videoUrl"]
            if use_description:
                filename = record["created"][:-7] + "_"+sanitize(record["description"]) + ".mp4"
            else:
                filename = get_filename(video_url)          
            filepath = path + "/" + filename

            if not include_revines:             
                if record["username"] != username:  
                    # We don't want this vine from another user, skip record
                    continue

            if not os.path.isfile(filepath):
                # If file doesn't already exist, download it
                print("Downloading" + str(count) +" "+ filename)
                count=count+1
                try:
                    urllib.request.urlretrieve(video_url, filepath)
                except:
                    print("Error downloading file")

                # Might throw off flood protection if the API has any
                time.sleep(uniform(0.25, 1.75))         
            else:
                print("Skipping " + filename + ", file already exists")
        # if the anchor is empty 
        if (int(anchor)<1):
            print("Done")
            sys.exit(0) 

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Your Vine is Mine")
    parser.add_argument('-i', 
        '--id', 
        help="The Vine user ID", 
        required=True)
    parser.add_argument('-p', 
        '--path', 
        help="The path to the download folder", 
        required=True)
    parser.add_argument('-r', 
        '--revine', 
        help="Include revines [default = TRUE]", 
        required=False, 
        default="true", 
        choices=['true', 'false'])
    parser.add_argument('-d', 
        '--description', 
        help="Use the description as the filename [default = TRUE]", 
        required=False, 
        default="true", 
        choices=['true', 'false'])
    args = parser.parse_args()
    main(args)
