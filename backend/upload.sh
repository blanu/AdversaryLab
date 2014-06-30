curl -i -X POST adversary-lab.appspot.com:80/uploadReport -H "Content-Type: text/json" --data-binary "@compiled/$1.json"
