export PYTHONPATH=$PYTHONPATH:/home/guypesto/deploy:/home/guypesto/deploy/seattle
export DJANGO_SETTINGS_MODULE='seattlegeni.website.settings'

CURRENT_VERSION="0.1o"
#/home/guypesto/deploy/seattlegeni/dev/scripts/graphs
name=node_overview
/home/guypesto/deploy/seattlegeni/stats/scripts/print_data_point.py $name $CURRENT_VERSION >>/home/guypesto/deploy/seattlegeni/stats/public_html/$name.txt 2>>/home/guypesto/deploy/seattlegeni/dev/scripts/graphs$name.err

name=node_type
/home/guypesto/deploy/seattlegeni/stats/scripts/print_data_point.py $name >>/home/guypesto/deploy/seattlegeni/stats/public_html/$name.txt 2>>/home/guypesto/deploy/seattlegeni/dev/scripts/graphs/$name.err

name=vessels
/home/guypesto/deploy/seattlegeni/stats/scripts/print_data_point.py $name >>/home/guypesto/deploy/seattlegeni/stats/public_html/$name.txt 2>>/home/guypesto/deploy/seattlegeni/dev/scripts/graphs/$name.err

name=advertise
/home/guypesto/deploy/seattlegeni/stats/scripts/print_data_point.py $name >>/home/guypesto/deploy/seattlegeni/stats/public_html/$name.txt 2>>/home/guypesto/deploy/seattlegeni/dev/scripts/graphs/$name.err

