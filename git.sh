git status

git add         IMAGES
git add         git.sh LICENSE README.md

git add         ./MESH/beam.med
git add         ./MESH/beam_holes.med
git add         ./MESH/beam_shell.med
git add         ./MESH/heatsink.med
git add         ./MESH/beam_3D.med

git add         ./STUDY/beam
git add         ./STUDY/beam_holes
git add         ./STUDY/heatsink
git add         ./STUDY/beam_3D

git commit -m "constraints optimization, time measurement"

git push

git ls-files


# git log
# git config credential.helper store
# git push -f -u origin main
# git rm -r --cached ./imgsrc

