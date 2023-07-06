#!/bin/bash
set -e
export ROLLBAR_TOKEN

echo '----Start command git commit----'
git commit -m 'Local commit'

echo '----Start command git pull----'
git pull

echo '----Create venv----'
python -m venv venv

echo '----Activate venv----'
source venv/bin/activate

echo '----Install Python Library----'
pip install -r requirements.txt

echo '----Install NodeJs Library----'
npm ci --dev

echo '----Collect Static----'
python3 manage.py collectstatic --no-input

echo '----Migrate----'
python3 manage.py migrate --no-input

echo '----Restart Systemd----'
systemctl daemon-reload

echo '----Restart Nginx----'
systemctl restart nginx

echo '----Send status in Rollbar----'
hash=$(git rev-parse HEAD)

ROLLBAR_TOKEN=$ROLLBAR_TOKEN

curl https://api.rollbar.com/api/1/deploy/ \
  -F access_token=$ROLLBAR_TOKEN \
  -F environment=production \
  -F revision=$hash \
  -F local_username=$USER \
  -F comment="Deployed new version" \
  -F status=finished

echo '----SUCCES Deploy----'
