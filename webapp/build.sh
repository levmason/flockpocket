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
# files=(
#     # list files here
#     common/utility.js \
#     common/modal.js \
#     api/api.js \
#     directory/badge.js \
#     directory/profile.js \
#     directory/directory.js \
#     directory/results.js \
#     directory/infocard.js \
#     directory/familycard.js \
#     form/input.js \
#     form/new_user.js \
#     menu/top_menu.js \
#     menu/menu.js \
#     flockpocket.js \
# )
files=(`find . -type f -name "*.js"`)
if $QUICK; then
    command="cat"
else
    command="google-closure-compiler --js"
fi
$command ${files[@]} > ../static/js/flockpocket.min.js

#
# flockpocket.min.css
# files=(
#     # list files here
#     common/modal.css \
#     common/content.css \
#     menu/menu.css \
#     menu/top_menu.css \
#     menu/left_menu.css \
#     menu/right_menu.css \
#     directory/directory.css \
#     directory/profile.css \
#     directory/badge.css \
#     flockpocket.css
# )
files=(`find . -type f -name "*.css"`)
cat ${files[@]} > ../static/css/flockpocket.min.css
