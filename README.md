---
title: DSFS-33 Front
emoji: 🐨
colorFrom: indigo
colorTo: pink
sdk: docker
pinned: false
license: apache-2.0
short_description: 'dsfs-33-frontend app'
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

## Docker

docker build -t dsfs-33-front-end .

docker run -it -v "$(pwd):/home/user/app" -p 4000:7860 --env-file .env -e PORT=7860  dsfs-33-front-end

