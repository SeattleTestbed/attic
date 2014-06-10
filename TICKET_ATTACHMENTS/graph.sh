#!/bin/bash

# Create temporary files for the graphviz commands and output image

relfile1=$(mktemp)
relfile2=$(mktemp)
cmdfile=$(mktemp)
outfile=$(mktemp)

if [ "x$relfile1" = "x" -o "x$relfile2" = "x" -o "x$cmdfile" = "x" -o "x$outfile" = "x" ] ; then
  echo "Could not create temporary files."
  exit 1
fi

# Unfiltered relations
for file in *.py ; do
  cat "$file" | while read line ; do
    
    # Look for lines where we import something
    echo "$line" | grep --silent --regexp="^[ ]*import"
    if [ $? -eq 0 ] ; then

      # Remove leading spaces
      lined=$(echo "$line" | sed -e "s|^[ ]*import[ ]*\([^ ]*\) .*$|\1|")

      if [ "x$lined" = "x" ] ; then
        lined=$(echo "$line" | sed -e "s|^[ ]*import[ ]*\([^ ]*\)$|\1|")
        [ "x$lined" = "x" ] && echo "parsed incorrectly: \"$line\""
      fi

      # Add the relation
      echo "${file/.py/} ${lined}" >> "$relfile1"
    fi
  done
done

for n_times in $(seq 1 5); do # do this a bunch of times

  # Filter relations where the sink is always a sink
  cat "$relfile1" | cut -d' ' -f1 | sort | uniq | while read line ; do
    if ! (grep -q -e " ${line}$" "$relfile1"); then
      grep -v -e "^${line} " "$relfile1" > "$relfile2"
      cat "$relfile2" > "$relfile1"
    fi
  done

  # vice versa
  cat "$relfile1" | cut -d' ' -f2 | sort | uniq | while read line ; do
    if ! (grep -q -e "^${line} " "$relfile1"); then
      grep -v -e " ${line}$" "$relfile1" > "$relfile2"
      cat "$relfile2" > "$relfile1"
    fi
  done

done

echo "digraph G {" > "$cmdfile"
#echo " rankdir=LR;" >> "$cmdfile"
echo " node [shape = circle, size=1];" >> "$cmdfile"

sed -e "s|^\(.*\) \(.*\)| \1 -> \"\2\";|" "$relfile1" >> "$cmdfile"

echo "}" >> "$cmdfile"

# Render the graph
dot -Tpng -o "$outfile" "$cmdfile"
echo "Graph rendered in: $outfile"

# Display it (Eye Of Gnome is an image viewer)
eog "$outfile"
