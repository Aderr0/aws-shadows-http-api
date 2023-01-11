PATH_TO_APP="src"

CONF_FILE=$1

# Check arguments
if [ $# -ne 1 ]
then
    echo "$0 <configuration file>"
    exit 1
fi

if [ ! -f "$CONF_FILE" ]
then 
    trace_error "Please create configuration file <$CONF_FILE> from template"
    exit 1
fi 
# load variables
source "$CONF_FILE"

python3 $PATH_TO_APP/app.py -t $THING_NAME -a $AWS_ACCESS_KEY_ID -s $AWS_SECRET_ACCESS_KEY 
