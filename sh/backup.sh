filename="restore_$(date '+%Y_%m_%d').sql"

sudo mysqldump flask_cookbook > /var/www/flask_cookbook/backups/$filename

#sudo cp /var/cookbook/backups/$filename /var/www/html/backups/$filename
