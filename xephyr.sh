NEWDISPLAY=:$(( ${DISPLAY#:}+1))
Xephyr -screen 1366x768 -ac $NEWDISPLAY &
export DISPLAY=$NEWDISPLAY
kwin &
konsole &