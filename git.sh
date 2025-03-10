git status

git add         IMAGES
git add         git.sh LICENSE README.md

git add         ./MESH/beam_hole.med
git add         ./MESH/beam_shell.med
git add         ./MESH/heatsink.med

git add         ./STUDY/beam
git add         ./STUDY/heatsink

git commit -m "extended with thermal analyses"

git push

git ls-files


# git log
# git config credential.helper store
# git push -f -u origin main
# git rm -r --cached ./imgsrc

