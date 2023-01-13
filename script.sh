

PATH_TO_APP="src"
APP_NAME="app.py"

PARAMS_NUMBER=3

# Check arguments
if [ $# -lt $(($PARAMS_NUMBER-1)) ]
then
    echo "$0 <*configuration file*> <*method*> <shadow state document>"
    exit 1
fi

CONF_FILE=$1
METHOD=$2
PATH_TO_STATE_DOCUMENT=$3

if [ ! -f "$CONF_FILE" ]
then 
    trace_error "Please create configuration file <$CONF_FILE> from template"
    exit 1
fi 
# load variables
source "$CONF_FILE"


# Check arguments
if [ $# -eq 3 ]
then
    PARAMS="-t $THING_NAME -m $METHOD -sd $PATH_TO_STATE_DOCUMENT -a $AWS_ACCESS_KEY_ID -s $AWS_SECRET_ACCESS_KEY"
else
    PARAMS="-t $THING_NAME -m $METHOD -a $AWS_ACCESS_KEY_ID -s $AWS_SECRET_ACCESS_KEY"
fi

python3 $PATH_TO_APP/$APP_NAME $PARAMS 
