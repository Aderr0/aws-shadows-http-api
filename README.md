# AWS Shadows HTTP API

Using the HTTP API of AWS is a mess. To make it easier, AWS develops two solutions : the SDK and the CLI.

However, in IoT, we don't want to download GB of codes on our things. The more codes are downloads, the more it consumes battery.

I wanted to manipulte a part of AWS IoT Core : AWS Shadows. But only with natives modules of python.

## How does it works ?

With this repo you can :
- GET a shadow of a thing

In the TODO list of this repo, there are : 
- UPDATE a shadow 
- DELETE a shadow

### GET a Shadow

1. Clone the repo
2. Copy the file ```conf.template``` and rename it for something else (conf.Aderr0 for example)
3. Open ```constants``` file and complete it
3. Execute the script ```script.sh``` 

### UPDATE a Shadow

TODO

### DELETE a Shadow

TODO

## How to manipulate AWS HTTP API ?