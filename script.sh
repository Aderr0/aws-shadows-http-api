#!/bin/bash



######################################
# CONSTANTS
######################################

PATH_TO_APP="src/aws_create_request"
APP_NAME="app.py"



######################################
# ARGUMENTS PARSER
######################################

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--conf-file)
            CONF_FILE="$2"
            shift # past argument
            shift # past value
            ;;
        -m|--method)
            METHOD="$2"
            shift # past argument
            shift # past value
            ;;
        -t|--thing-name)
            THING_NAME="$2"
            shift # past argument
            shift # past value
            ;;
        -r|--region)
            REGION="$2"
            shift # past argument
            shift # past value
            ;;
        -s|--shadow-name)
            SHADOW_NAME="$2"
            shift # past argument
            shift # past value
            ;;
        -d|--state-document)
            PATH_TO_STATE_DOCUMENT="$2"
            shift # past argument
            shift # past value
            ;;
        -*|--*)
            echo "Usage: ./script.sh -c <configuration file> -m <method> -t <thing name> [-s <shadow name>] [-d <request state document>]"
            echo "Unknown option $1"
            exit 1
            ;;
        *)
            POSITIONAL_ARGS+=("$1") # save positional arg
            shift # past argument
            ;;
    esac
done

# set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

if [ ! -f "$CONF_FILE" ] || [ ! "$METHOD" ] || [ ! "$THING_NAME" ]
then 
    echo "Usage: ./script.sh -c <configuration file> -m <method> -t <thing name> [-r <region>] [-s <shadow name>] [-d <request state document>]"
    exit 1
fi 



######################################
# MAIN
######################################

# load variables
source "$CONF_FILE"

PARAMS="-t $THING_NAME -m $METHOD -a $AWS_ACCESS_KEY_ID -k $AWS_SECRET_ACCESS_KEY"

if [ "$REGION" ]
then 
    PARAMS="$PARAMS -r $REGION"
fi 
if [ "$SHADOW_NAME" ]
then 
    PARAMS="$PARAMS -s $SHADOW_NAME"
fi 
if [ "$PATH_TO_STATE_DOCUMENT" ]
then 
    PARAMS="$PARAMS -d $PATH_TO_STATE_DOCUMENT"
fi 

python3 $PATH_TO_APP/$APP_NAME $PARAMS 
