#!/bin/bash

#cd /Users/bob/IdeaProjects/

for f in `ls ./`
do
  if [ -d "${f}" ]
  then
      echo -e "\n${f}"
      cd ${f}

      git fetch -aptP

      echo "update result:"
      git rebase origin/production

      cd ..
    fi
done
#echo -e "\nFinished"