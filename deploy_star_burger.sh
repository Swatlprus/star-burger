#!/bin/bash
set -e
source .env

echo '----Start command git commit----'
git commit -m 'Local commit'

echo '----Start command git pull----'
git pull

echo '----Install Python Library----'
pip install -r requirements.txt

echo '----Install NodeJs Library----'
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo '----Collect Static----'
python3 manage.py collectstatic --no-input

echo '----Migrate----'
python3 manage.py migrate --no-input

echo '----Restart Nginx----'
systemctl restart nginx

echo '----Send status in Rollbar----'
hash=$(git rev-parse HEAD)

curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_TOKEN \
  -F environment=$ROLLBAR_ENVIROMENT \
  -F revision=$hash \
  -F local_username=$USER \
  -F comment="Deployed new version" \
  -F status=succeeded

echo '----SUCCES Deploy----'
