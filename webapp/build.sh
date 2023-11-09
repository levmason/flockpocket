# check for -q argument
QUICK=false
for arg in "$@"
do
    if [ "$arg" == "-q" ]
    then
	QUICK=true
    fi
done

# go into the static dir
cd ../static/

#
# flockpocket.dep.min.js
files=(
    emoji/emoji.js \
    misc/jquery.blockUI.js \
    misc/jquery.ba-throttle-debounce.min.js \
    moment/moment.min.js \
    moment/moment-timezone-with-data.js \
    croppie/croppie.min.js \
    underscore/underscore-umd-min.js \
    )
cat ${files[@]} > js/flockpocket.dep.min.js

#
# flockpocket.dep.min.css
files=(
    croppie/croppie.min.css \
)
cat ${files[@]} > css/flockpocket.dep.min.css

#
# flockpocket.min.js
cd ../webapp/
files=(`find . -type f -name "*.js"`)
if $QUICK; then
    command="cat"
else
    command="google-closure-compiler --js"
fi
$command ${files[@]} > ../static/js/flockpocket.min.js

#
# flockpocket.min.css
files=(`find . -type f -name "*.css"`)
cat ${files[@]} > ../static/css/flockpocket.min.css
